"""
Three chunking strategies: fixed-size, recursive character, semantic.
"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from backend.config import settings


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, metadata: dict) -> list[dict]:
        ...


class FixedSizeChunker(BaseChunker):
    """Split at exact token boundaries using tiktoken."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.enc = tiktoken.get_encoding("cl100k_base")

    def chunk(self, text: str, metadata: dict) -> list[dict]:
        tokens = self.enc.encode(text)
        chunks = []
        start = 0
        idx = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.enc.decode(chunk_tokens)
            chunks.append({
                "text": chunk_text,
                "metadata": {**metadata, "chunk_index": idx, "strategy": "fixed"},
            })
            start += self.chunk_size - self.overlap
            idx += 1
        return chunks


class RecursiveCharChunker(BaseChunker):
    """LangChain recursive character splitter — respects sentence and paragraph boundaries."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 4,  # approx 4 chars per token
            chunk_overlap=overlap * 4,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk(self, text: str, metadata: dict) -> list[dict]:
        parts = self.splitter.split_text(text)
        return [
            {"text": p, "metadata": {**metadata, "chunk_index": i, "strategy": "recursive"}}
            for i, p in enumerate(parts)
            if len(p.strip()) > 50
        ]


class SemanticChunker(BaseChunker):
    """Split where cosine similarity between adjacent sentences drops below a threshold."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return self._model

    def chunk(self, text: str, metadata: dict) -> list[dict]:
        import numpy as np

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]
        if len(sentences) <= 2:
            return [{"text": text, "metadata": {**metadata, "chunk_index": 0, "strategy": "semantic"}}]

        model = self._get_model()
        embeddings = model.encode(sentences, batch_size=32, show_progress_bar=False)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / (norms + 1e-10)

        chunks = []
        current: list[str] = [sentences[0]]
        idx = 0

        for i in range(1, len(sentences)):
            sim = float(np.dot(embeddings[i - 1], embeddings[i]))
            if sim < self.threshold and len(current) >= 3:
                chunks.append({
                    "text": " ".join(current),
                    "metadata": {**metadata, "chunk_index": idx, "strategy": "semantic"},
                })
                current = [sentences[i]]
                idx += 1
            else:
                current.append(sentences[i])

        if current:
            chunks.append({
                "text": " ".join(current),
                "metadata": {**metadata, "chunk_index": idx, "strategy": "semantic"},
            })
        return chunks


def get_chunker(strategy: str | None = None) -> BaseChunker:
    s = (strategy or settings.chunk_strategy).lower()
    if s == "fixed":
        return FixedSizeChunker(settings.chunk_size, settings.chunk_overlap)
    if s == "semantic":
        return SemanticChunker()
    return RecursiveCharChunker(settings.chunk_size, settings.chunk_overlap)


def chunk_all_docs(strategy: str | None = None, progress_callback=None) -> list[dict]:
    """Chunk all raw EDGAR docs and save to processed/chunks/*.jsonl"""
    from backend.pipeline.ingest import load_manifest

    chunker = get_chunker(strategy)
    raw_dir = Path(settings.repo_root) / settings.raw_data_dir / "edgar"
    out_dir = Path(settings.repo_root) / settings.processed_data_dir / "chunks"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()
    if not manifest:
        logger.warning("No ingested documents found. Run ingest first.")
        return []

    all_chunks: list[dict] = []
    for i, doc_meta in enumerate(manifest):
        doc_path = Path(doc_meta["path"])
        if not doc_path.exists():
            logger.warning(f"Missing file: {doc_path}")
            continue

        text = doc_path.read_text(encoding="utf-8")
        meta = {
            "doc_id": doc_meta["doc_id"],
            "company": doc_meta.get("company_name", doc_meta.get("ticker", "unknown")),
            "ticker": doc_meta.get("ticker", ""),
            "year": doc_meta.get("year", 0),
            "section": "10-K",
        }
        chunks = chunker.chunk(text, meta)
        all_chunks.extend(chunks)

        if progress_callback:
            progress_callback((i + 1) / len(manifest), f"Chunked {doc_meta['doc_id']}")

        logger.info(f"Chunked {doc_meta['doc_id']} → {len(chunks)} chunks")

    # Write all chunks to a single jsonl file
    out_file = out_dir / f"chunks_{strategy or settings.chunk_strategy}.jsonl"
    with out_file.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    logger.info(f"Saved {len(all_chunks)} chunks → {out_file}")
    return all_chunks


def load_chunks(strategy: str | None = None) -> list[dict]:
    out_dir = Path(settings.repo_root) / settings.processed_data_dir / "chunks"
    fname = f"chunks_{strategy or settings.chunk_strategy}.jsonl"
    path = out_dir / fname
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
