"""
Embedding: sentence-transformers (local) or Cohere Embed v3 (optional).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from loguru import logger

from backend.config import settings


class BaseEmbedder(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        ...


class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name: str | None = None):
        import os
        import torch
        from sentence_transformers import SentenceTransformer

        # Avoid multi-process tokenizer workers — reduces Windows page-file pressure
        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        # Prevent torch from pre-allocating a large CUDA cache when only CPU is needed
        os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:128")

        name = model_name or settings.embed_model_name
        logger.info(f"Loading SentenceTransformer: {name}")
        self._model = SentenceTransformer(
            name,
            device="cpu",
            model_kwargs={"torch_dtype": torch.float32},
        )
        get_dim = getattr(self._model, "get_embedding_dimension", None) or self._model.get_sentence_embedding_dimension
        self._dim = get_dim()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vecs = self._model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
        return vecs.tolist()

    def embed_query(self, text: str) -> list[float]:
        vec = self._model.encode(text, normalize_embeddings=True)
        return vec.tolist()

    @property
    def dimension(self) -> int:
        return self._dim


class CohereEmbedder(BaseEmbedder):
    def __init__(self):
        import cohere
        if not settings.cohere_api_key:
            raise ValueError("COHERE_API_KEY is not set in .env")
        self._client = cohere.Client(settings.cohere_api_key)
        self._dim = 1024  # Cohere embed-english-v3.0

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document",
        )
        return response.embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self._client.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_query",
        )
        return response.embeddings[0]

    @property
    def dimension(self) -> int:
        return self._dim


_embedder_instance: BaseEmbedder | None = None


def get_embedder() -> BaseEmbedder:
    global _embedder_instance
    if _embedder_instance is None:
        if settings.embed_model == "cohere" and settings.cohere_api_key:
            logger.info("Using Cohere Embed v3 (Config E)")
            _embedder_instance = CohereEmbedder()
        else:
            if settings.embed_model == "cohere":
                logger.warning("COHERE_API_KEY not set — falling back to sentence-transformers")
            _embedder_instance = SentenceTransformerEmbedder()
    return _embedder_instance
