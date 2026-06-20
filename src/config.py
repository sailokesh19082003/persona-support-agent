"""
Central configuration for the Persona-Adaptive Support Agent.

Everything that is a "tunable knob" (model names, thresholds, paths) lives
here so it can be explained and adjusted in one place, instead of being
scattered (and hardcoded) across modules.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env into the process environment, if present

# ---------------------------------------------------------------------------
# API credentials
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
# Chat / generation model used for both persona classification and the
# final adaptive response generation.
CHAT_MODEL = os.environ.get("CHAT_MODEL", "gemini-2.5-flash")

# Embedding model used to vectorize document chunks and user queries.
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-004")

# ---------------------------------------------------------------------------
# RAG pipeline settings
# ---------------------------------------------------------------------------
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
CHROMA_DB_DIR = os.environ.get("CHROMA_DB_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
COLLECTION_NAME = "support_kb"

CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50     # characters shared between adjacent chunks
TOP_K = 3              # number of chunks retrieved per query

# ---------------------------------------------------------------------------
# Escalation settings
# ---------------------------------------------------------------------------
# If the best retrieved chunk's cosine similarity is below this, we treat
# the knowledge base as "not having a good enough answer".
RETRIEVAL_CONFIDENCE_THRESHOLD = float(os.environ.get("RETRIEVAL_CONFIDENCE_THRESHOLD", 0.45))

# Keyword triggers for topics that should always go to a human, regardless
# of how confident the retrieval was (billing disputes, legal, account
# deletion, etc.) — these are policy decisions, not knowledge gaps.
SENSITIVE_KEYWORDS = [
    "refund", "chargeback", "charge back", "dispute", "lawsuit", "legal action",
    "sue", "fraud", "unauthorized charge", "delete my account",
    "close my account", "data deletion", "gdpr", "ccpa", "transfer ownership",
    "cancel my subscription", "billing dispute", "compliance",
]

# If a user is classified as "Frustrated User" this many consecutive turns
# in a row, escalate even if retrieval confidence looks fine — repeated
# frustration is itself a signal that self-service isn't working.
MAX_FRUSTRATION_TURNS = 2

PERSONAS = ["Technical Expert", "Frustrated User", "Business Executive"]

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
APP_TITLE = "CloudDesk Support Assistant"
