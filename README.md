# CloudDesk Support Assistant
### A Persona-Adaptive Customer Support Agent (RAG + LLM Classification + Human Escalation)

This project implements an AI support agent that detects a customer's
communication persona, retrieves grounded answers from a knowledge base
using Retrieval-Augmented Generation (RAG), adapts its tone to the
detected persona, and escalates to a human agent — with a structured
handoff summary — when it shouldn't answer on its own.

---

## 1. Project Overview

When a customer sends a message, the system:

1. **Classifies** the message into one of three personas — *Technical
   Expert*, *Frustrated User*, or *Business Executive* — using Gemini
   with structured JSON output.
2. **Retrieves** the most relevant chunks from a vector database built
   from a local knowledge base of support articles (`.md`, `.txt`, `.pdf`).
3. **Checks escalation conditions** — low retrieval confidence, a
   sensitive topic (billing/legal/account), or repeated frustration
   across turns.
4. If escalation isn't triggered, it **generates a persona-styled,
   grounded response** using only the retrieved context (no hallucinated
   policy details).
5. If escalation *is* triggered, it returns a short holding message plus
   a **structured JSON handoff summary** for a human agent.

## 2. Tech Stack

| Component | Choice | Version |
|---|---|---|
| Language | Python | 3.11+ |
| LLM + Embeddings | Google Gemini (`google-genai` SDK) | `google-genai>=0.1.0` |
| Chat model | `gemini-2.5-flash` | — |
| Embedding model | `text-embedding-004` | — |
| Vector database | ChromaDB (local, persistent) | `chromadb>=0.4.0` |
| Chunking | LangChain `RecursiveCharacterTextSplitter` | `langchain>=0.1.0` |
| PDF parsing | `pypdf` | `>=3.0.0` |
| Web UI | Streamlit | `>=1.30.0` |
| CLI | Python stdlib | — |
| Config / secrets | `python-dotenv` | `>=1.0.0` |
| Testing | `pytest` | `>=7.0.0` |

## 3. Architecture

```
                       ┌──────────────────────┐
   User Message  ───▶  │  Persona Classifier   │  (Gemini, structured JSON output)
                       └──────────┬───────────┘
                                  │  persona: Technical Expert /
                                  │  Frustrated User / Business Executive
                                  ▼
                       ┌──────────────────────┐
                       │   RAG Retriever       │
                       │  (ChromaDB + Gemini    │
                       │   text-embedding-004)  │
                       └──────────┬───────────┘
                                  │  top-k chunks + cosine similarity scores
                                  ▼
                       ┌──────────────────────┐
                       │  Escalation Check      │──── YES ───▶ ┌────────────────────┐
                       │ (confidence / sensitive │              │ Handoff JSON +      │
                       │  topic / repeated       │              │ holding message     │
                       │  frustration)           │              └────────────────────┘
                       └──────────┬───────────┘
                                  │ NO
                                  ▼
                       ┌──────────────────────┐
                       │ Persona-Adaptive       │
                       │ Response Generator     │ ──▶  Final grounded response
                       │ (Gemini, grounded       │
                       │  in retrieved context)  │
                       └──────────────────────┘
```

This maps directly onto the source files:

| Diagram stage | File |
|---|---|
| Persona Classifier | `src/classifier.py` |
| RAG Retriever (chunking, embeddings, vector DB) | `src/rag_pipeline.py` |
| Escalation Check + Handoff JSON | `src/escalator.py` |
| Adaptive Response Generator | `src/generator.py` |
| Orchestration / multi-turn memory | `src/agent.py`, `src/memory.py` |
| Interfaces | `cli.py`, `app.py` |
| One-time index build | `ingest.py` |

## 4. Persona Detection Strategy

**Method:** A single Gemini call per message, constrained to a JSON
schema (`persona`, `confidence`, `reasoning`) with `enum` restricting
`persona` to exactly the three target classes. This is more reliable than
asking for free-text and parsing it, and it gives a `reasoning` string
that's useful for debugging and for the human handoff summary.

**Prompt design:** The system instruction gives explicit, distinguishing
signals for each persona (jargon/APIs → Technical Expert; emotional
language/urgency → Frustrated User; ROI/timelines/brevity → Business
Executive) rather than just naming the categories, since LLMs classify
far more consistently when given concrete discriminating cues.

**Fallback:** If `GEMINI_API_KEY` isn't set, a small keyword-based
heuristic (`_fallback_classify` in `src/classifier.py`) is used instead,
purely so the rest of the app (UI, retrieval, escalation) can be
developed and tested before a key is available. **The real LLM
classifier is always used whenever a key is configured** — the fallback
is a development convenience, not a substitute for the graded demo.

## 5. RAG Pipeline Design

**Document ingestion:** `.md` files are split on top-level headings so
each chunk's metadata can cite a *section name*; `.pdf` files are parsed
page-by-page with `pypdf` so chunks can cite a *page number*; `.txt`
files are treated as a single section. (See `src/rag_pipeline.py:load_documents`.)

**Chunking strategy:** `RecursiveCharacterTextSplitter` with
`chunk_size=500`, `chunk_overlap=50`. The recursive splitter tries
paragraph breaks first, then sentences, then words, then raw characters
— this keeps a complete troubleshooting step or API parameter
description intact far more often than a naive fixed-width split would.
The 50-character overlap means content right at a chunk boundary (e.g. an
endpoint URL split mid-sentence) still appears whole in at least one
chunk.

**Embedding model:** Gemini `text-embedding-004` (768-dim), used for both
documents at ingest time and the user's query at retrieval time — using
the same model for both sides is required for the cosine similarity
scores to be meaningful.

**Vector database:** ChromaDB, run as a local persistent client
(`./chroma_db`). Chosen over FAISS because it stores metadata
(source file, section/page, chunk index) alongside the vector natively,
which the escalation/handoff logic depends on.

**Retrieval strategy:** Top-`k=3` chunks per query via cosine similarity.
Chroma returns *distance*; this is converted to a similarity score with
`score = 1 - distance` and clamped to ≥ 0, since the escalation
threshold and UI are expressed in similarity terms.

## 6. Escalation Logic

Escalation triggers (checked in `src/escalator.py`, all configurable in
`src/config.py`):

| Trigger | Logic | Default threshold |
|---|---|---|
| Low retrieval confidence | Best chunk's similarity score < threshold, or no chunks at all | `0.45` |
| Sensitive topic | Message contains a billing/legal/account-modification keyword (refund, chargeback, delete my account, GDPR, etc.) | keyword list in `config.SENSITIVE_KEYWORDS` |
| Repeated frustration | User classified as *Frustrated User* for `N` consecutive turns | `N = 2` |

Sensitive-topic escalation is checked **regardless of retrieval
confidence** — even if the knowledge base has a perfect answer about
refund policy, a refund *demand* is a policy/financial decision that
should go to a human, not be auto-resolved.

When any trigger fires, `escalator.build_handoff_summary()` produces:

```json
{
  "persona": "Frustrated User",
  "issue_summary": "...",
  "escalation_reasons": ["low_retrieval_confidence", "sensitive_topic"],
  "escalation_reasons_explained": ["...", "..."],
  "conversation_history": [{"user_message": "...", "persona": "..."}],
  "documents_consulted": ["billing_refund_policy.txt"],
  "best_retrieval_score": 0.22,
  "recommended_next_steps": ["..."]
}
```

## 7. Setup Instructions

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd persona-support-agent

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# then edit .env and paste your Gemini API key

# 5. Build the vector index (run once, and again after editing /data)
python ingest.py

# 6a. Run the CLI chatbot
python cli.py

# 6b. OR run the Streamlit web UI
streamlit run app.py
```

### Getting a Gemini API key
Go to [Google AI Studio](https://aistudio.google.com/app/apikey), create a
key, and paste it into `.env` as `GEMINI_API_KEY`.

## 8. Environment Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Auth for Gemini chat + embedding calls |
| `CHAT_MODEL` | No | `gemini-2.5-flash` | Override the generation/classification model |
| `EMBEDDING_MODEL` | No | `text-embedding-004` | Override the embedding model |
| `RETRIEVAL_CONFIDENCE_THRESHOLD` | No | `0.45` | Escalation threshold for retrieval confidence |
| `DATA_DIR` | No | `./data` | Knowledge base source folder |
| `CHROMA_DB_DIR` | No | `./chroma_db` | Where the persistent vector index is stored |

## 9. Example Queries

| # | Query | Expected Persona | Expected Behavior |
|---|---|---|---|
| 1 | "Where's the guide to clear cookies? It's been an hour and nothing is loading!" | Frustrated User | Empathetic opener, simple bulleted troubleshooting steps |
| 2 | "What are the header parameter requirements for bearer token auth?" | Technical Expert | Precise headers/parameters, grounded in `api_authentication_guide.md` |
| 3 | "Our uptime is dropping. We need a timeline for when billing disputes are resolved." | Business Executive | Short, impact/timeline-focused — but **escalates** (billing dispute = sensitive topic) |
| 4 | "I'm getting internal server errors from your database integration." | Technical Expert | Step-by-step resolution grounded in `api_error_codes.md` |
| 5 | "My billing statement has duplicate charges. I demand an immediate refund!" | Frustrated User | **Escalates** — sensitive topic (refund) — structured handoff JSON generated |
| 6 | "How do I enable SSO for my whole team?" | Technical Expert / Business Executive | Grounded in `sso_saml_setup.md` |
| 7 | "I lost access to my authenticator app and can't log in." | Frustrated User | Grounded in `two_factor_authentication.md`, empathetic tone |

## 10. Known Limitations & Future Improvements

- **Session-only memory.** Conversation history (`src/memory.py`) lives
  in process memory and resets when the app restarts. A production
  version would persist this in SQLite/Redis per `session_id`.
- **Single-turn retrieval.** Each query is embedded independently; the
  retriever doesn't yet rewrite a query using prior conversation context
  (e.g. "what about on iOS?" referring to a previous message). A
  conversational query-rewriting step would improve multi-turn RAG.
- **No reranking step.** Retrieval returns raw cosine-similarity top-k;
  a cross-encoder reranker would likely improve precision for ambiguous
  queries.
- **Sentiment is inferred only through the persona label**, not tracked
  as a separate continuous score. A dedicated sentiment-over-time signal
  (bonus feature) would make "repeated frustration" detection more
  precise than the current consecutive-turn count.
- **No analytics persistence.** The Streamlit sidebar shows session-only
  analytics (persona distribution, escalation count); a real dashboard
  would log this to a database for trend analysis across all users.
- **Single LLM provider.** Only Gemini is wired up; swapping in another
  provider (OpenAI/Claude) would require a thin adapter in
  `classifier.py`/`generator.py`/`rag_pipeline.py` behind the same
  function signatures.

## 11. Testing

```bash
pytest tests/ -v
```

The test suite covers document loading, chunking, the fallback
classifier, and all escalation logic — **without** requiring a
`GEMINI_API_KEY`, so it can run in CI. (Embedding/LLM calls themselves
aren't unit-tested since they require live API access; they were
verified manually during development with a mocked embedding function to
confirm the ingest → store → retrieve wiring is correct end-to-end.)

## 12. Deploying

**Streamlit Community Cloud (free, fastest):**
1. Push this repo to GitHub (`.env` stays out of git — see `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your
   GitHub account, and select this repo + `app.py` as the entry point.
3. Under "Advanced settings → Secrets," add:
   ```
   GEMINI_API_KEY = "your_actual_key"
   ```
4. Deploy. Note: the vector index needs to exist before first use — either
   commit a pre-built `chroma_db/` (small enough here) or call the
   "Rebuild Knowledge Base Index" button in the sidebar after first
   deploy.

## 13. Project Structure

```
persona-support-agent/
├── data/                          # knowledge base (18 docs: .md, .txt, .pdf)
├── src/
│   ├── config.py                  # models, thresholds, paths
│   ├── classifier.py               # persona detection (Gemini + fallback)
│   ├── rag_pipeline.py             # load → chunk → embed → store → retrieve
│   ├── generator.py                # persona-adaptive grounded generation
│   ├── escalator.py                # escalation triggers + handoff JSON
│   ├── memory.py                   # session conversation history
│   └── agent.py                    # orchestrates the full turn
├── tests/                          # offline tests (no API key needed)
├── scripts/generate_sample_pdf.py  # how password_reset_guide.pdf was made
├── ingest.py                       # one-time/on-demand index build
├── cli.py                          # command-line chatbot (min. requirement)
├── app.py                          # Streamlit web UI (bonus)
├── requirements.txt
├── .env.example
└── README.md
```
