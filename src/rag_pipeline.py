"""
RAG Pipeline: document ingestion, chunking, embedding, and retrieval.

Flow (matches the architecture diagram):
    load_documents()  ->  chunk_documents()  ->  ingest_all() [embed + store]
    retrieve_context(query) -> embed query -> cosine similarity search -> top-k chunks
"""
import logging
import os
import re
import time

from pypdf import PdfReader

from src import config

logger = logging.getLogger(__name__)

try:
    # Newer langchain versions split text splitters into their own package.
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


# ---------------------------------------------------------------------------
# 1. Document ingestion & parsing
# ---------------------------------------------------------------------------
def load_documents(data_dir: str = None) -> list[dict]:
    """
    Load every supported file in data_dir and return a list of "raw units":
        {"source": <filename>, "section": <page/heading/N-A>, "text": <str>}

    - .pdf  -> one unit per page (section = "Page N"), so retrieved chunks
               can cite a page number.
    - .md   -> split on top-level markdown headings (section = heading text),
               so retrieved chunks can cite a section name.
    - .txt  -> one unit for the whole file (section = "N/A").
    """
    data_dir = data_dir or config.DATA_DIR
    units = []

    for fname in sorted(os.listdir(data_dir)):
        path = os.path.join(data_dir, fname)
        if not os.path.isfile(path):
            continue

        if fname.lower().endswith(".pdf"):
            units.extend(_load_pdf(path, fname))
        elif fname.lower().endswith(".md"):
            units.extend(_load_markdown(path, fname))
        elif fname.lower().endswith(".txt"):
            units.extend(_load_text(path, fname))
        else:
            logger.info("Skipping unsupported file type: %s", fname)

    logger.info("Loaded %d source units from %s", len(units), data_dir)
    return units


def _load_pdf(path: str, fname: str) -> list[dict]:
    reader = PdfReader(path)
    out = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            out.append({"source": fname, "section": f"Page {page_num}", "text": text})
    return out


def _load_markdown(path: str, fname: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split on top-level (#) or second-level (##) headings, keeping the
    # heading text as the "section" metadata for citation purposes.
    pattern = re.compile(r"^(#{1,2})\s+(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(text))

    if not matches:
        return [{"source": fname, "section": "N/A", "text": text}]

    out = []
    for i, match in enumerate(matches):
        heading = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            out.append({"source": fname, "section": heading, "text": body})
    return out


def _load_text(path: str, fname: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return [{"source": fname, "section": "N/A", "text": text}]


# ---------------------------------------------------------------------------
# 2. Strategic chunking
# ---------------------------------------------------------------------------
def chunk_units(units: list[dict]) -> list[dict]:
    """
    Split each loaded unit into overlapping chunks using a
    RecursiveCharacterTextSplitter (paragraph -> sentence -> word -> char),
    so meaningful text (like a full troubleshooting step) is rarely sliced
    across a chunk boundary.

    Returns a list of:
        {"source": ..., "section": ..., "chunk_index": int, "text": ...}
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = []
    for unit in units:
        pieces = splitter.split_text(unit["text"])
        for idx, piece in enumerate(pieces):
            chunks.append({
                "source": unit["source"],
                "section": unit["section"],
                "chunk_index": idx,
                "text": piece,
            })

    logger.info("Produced %d chunks from %d source units", len(chunks), len(units))
    return chunks


# ---------------------------------------------------------------------------
# 3-5. Embedding, vector store, and retrieval
# ---------------------------------------------------------------------------
class RAGPipeline:
    """Wraps embedding generation + a persistent ChromaDB collection."""

    def __init__(self, db_dir: str = None, collection_name: str = None):
        import chromadb

        self.db_dir = db_dir or config.CHROMA_DB_DIR
        self.collection_name = collection_name or config.COLLECTION_NAME
        self.chroma_client = chromadb.PersistentClient(path=self.db_dir)
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
        self._genai_client = None

    # -- embeddings ---------------------------------------------------
    def _client(self):
        if self._genai_client is None:
            from google import genai
            self._genai_client = genai.Client(api_key=config.GEMINI_API_KEY)
        return self._genai_client

    def get_embedding(self, text: str) -> list[float]:
        """Call Gemini's embedding model for a single piece of text."""
        response = self._client().models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=text,
        )
        return response.embeddings[0].values

    # -- ingestion ------------------------------------------------------
    def reset(self):
        """Drop and recreate the collection (used when rebuilding the KB)."""
        import chromadb
        try:
            self.chroma_client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

    def ingest_chunks(self, chunks: list[dict], progress_callback=None) -> int:
        """
        Embed and store a list of chunks (see chunk_units()).
        progress_callback(i, total) is called after each chunk, if provided.
        """
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk["text"])
            time.sleep(0.7)
            chunk_id = f"{chunk['source']}::{chunk['section']}::{chunk['chunk_index']}"
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                metadatas=[{
                    "source": chunk["source"],
                    "section": chunk["section"],
                    "chunk_index": chunk["chunk_index"],
                }],
                documents=[chunk["text"]],
            )
            if progress_callback:
                progress_callback(i + 1, total)
        return total

    def ingest_from_data_dir(self, data_dir: str = None, progress_callback=None) -> int:
        """Convenience wrapper: load -> chunk -> ingest, resetting the index first."""
        units = load_documents(data_dir)
        chunks = chunk_units(units)
        self.reset()
        return self.ingest_chunks(chunks, progress_callback=progress_callback)

    # -- retrieval --------------------------------------------------------
    def retrieve_context(self, query: str, top_k: int = None) -> list[dict]:
        """
        Embed the query and run a cosine-similarity nearest-neighbor search
        against the vector store. Returns the top-k chunks with metadata and
        a similarity score in [0, 1] (higher = more relevant).
        """
        top_k = top_k or config.TOP_K
        query_vector = self.get_embedding(query)

        count = self.collection.count()
        if count == 0:
            return []

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, count),
        )

        retrieved = []
        if results and results.get("documents"):
            for i in range(len(results["documents"][0])):
                distance = results["distances"][0][i] if results.get("distances") else 1.0
                # Chroma's default space is cosine distance: similarity = 1 - distance
                score = max(0.0, 1.0 - distance)
                metadata = results["metadatas"][0][i]
                retrieved.append({
                    "text": results["documents"][0][i],
                    "source": metadata.get("source"),
                    "section": metadata.get("section"),
                    "score": round(score, 4),
                })
        return retrieved

    def stats(self) -> dict:
        return {"collection": self.collection_name, "chunk_count": self.collection.count()}
