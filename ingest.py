"""
Run this once (and again any time you change files in /data) to build the
local ChromaDB vector index:

    python ingest.py

This is intentionally a separate, explicit step rather than something that
runs automatically on every chat turn or app startup - re-embedding all
documents on every request would be slow and wasteful (see README
"Performance Notes"). The persisted index lives in ./chroma_db and is
loaded instantly by app.py / cli.py afterward.
"""
import logging
import sys
import time

from src import config
from src.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest")


def main():
    if not config.GEMINI_API_KEY:
        print(
            "ERROR: GEMINI_API_KEY is not set. Add it to your .env file before "
            "running ingestion (embeddings require a live API call)."
        )
        sys.exit(1)

    print(f"Loading documents from: {config.DATA_DIR}")
    pipeline = RAGPipeline()

    start = time.time()

    def progress(i, total):
        bar_len = 30
        filled = int(bar_len * i / total)
        bar = "#" * filled + "-" * (bar_len - filled)
        print(f"\rEmbedding chunks [{bar}] {i}/{total}", end="", flush=True)

    count = pipeline.ingest_from_data_dir(progress_callback=progress)
    elapsed = time.time() - start

    print(f"\nIngested {count} chunks into ChromaDB at '{config.CHROMA_DB_DIR}' "
          f"in {elapsed:.1f}s.")
    print(f"Collection stats: {pipeline.stats()}")


if __name__ == "__main__":
    main()
