"""
Tests for document loading and chunking. These do NOT require a
GEMINI_API_KEY since they only exercise the parsing/chunking logic, not
embeddings or LLM calls.

Run with: pytest tests/test_rag_pipeline.py -v
"""
from src import config
from src.rag_pipeline import load_documents, chunk_units


def test_load_documents_finds_all_supported_files():
    units = load_documents(config.DATA_DIR)
    assert len(units) > 0

    sources = {u["source"] for u in units}
    assert "password_reset_guide.pdf" in sources
    assert any(s.endswith(".md") for s in sources)
    assert any(s.endswith(".txt") for s in sources)


def test_pdf_units_have_page_metadata():
    units = load_documents(config.DATA_DIR)
    pdf_units = [u for u in units if u["source"] == "password_reset_guide.pdf"]
    assert len(pdf_units) > 0
    assert all(u["section"].startswith("Page") for u in pdf_units)


def test_markdown_units_have_section_headings():
    units = load_documents(config.DATA_DIR)
    md_units = [u for u in units if u["source"] == "api_authentication_guide.md"]
    assert len(md_units) > 1  # multiple headings in this file
    sections = {u["section"] for u in md_units}
    assert "Overview" in sections or "Generating an API Key" in sections


def test_chunking_respects_size_and_overlap():
    units = load_documents(config.DATA_DIR)
    chunks = chunk_units(units)
    assert len(chunks) >= len(units)  # chunking should never reduce count

    for chunk in chunks:
        assert "source" in chunk
        assert "section" in chunk
        assert "chunk_index" in chunk
        assert len(chunk["text"]) <= config.CHUNK_SIZE + config.CHUNK_OVERLAP
        assert chunk["text"].strip() != ""


def test_chunk_ids_would_be_unique():
    units = load_documents(config.DATA_DIR)
    chunks = chunk_units(units)
    ids = [f"{c['source']}::{c['section']}::{c['chunk_index']}" for c in chunks]
    assert len(ids) == len(set(ids)), "Chunk IDs must be unique for ChromaDB"
