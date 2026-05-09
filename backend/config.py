from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Embeddings
    embed_model: str = "local"  # "local" | "cohere"
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    cohere_api_key: str = ""

    # Reranker
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Pipeline knobs
    chunk_strategy: str = "recursive"  # "fixed" | "recursive" | "semantic"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_retrieve: int = 20
    top_k_rerank: int = 5
    bm25_weight: float = 0.4
    dense_weight: float = 0.6

    # Storage paths
    chroma_persist_dir: str = "data/chroma_db"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"

    # Server
    port: int = 8000
    debug: bool = False

    # RBAC — full-access keys
    api_key_admin: str = "admin-key"
    api_key_analyst: str = "analyst-key"
    api_key_viewer: str = "viewer-key"
    # RBAC — company-scoped analyst keys
    api_key_apple_analyst: str = "apple-analyst-key"
    api_key_msft_analyst: str = "msft-analyst-key"
    api_key_amzn_analyst: str = "amzn-analyst-key"
    api_key_googl_analyst: str = "googl-analyst-key"
    api_key_meta_analyst: str = "meta-analyst-key"
    api_key_nvda_analyst: str = "nvda-analyst-key"
    api_key_tsla_analyst: str = "tsla-analyst-key"
    api_key_jpm_analyst: str = "jpm-analyst-key"
    api_key_bac_analyst: str = "bac-analyst-key"
    api_key_wmt_analyst: str = "wmt-analyst-key"

    @property
    def chroma_collection_name(self) -> str:
        return "ragixai_cohere" if self.embed_model == "cohere" else "ragixai_local"

    @property
    def repo_root(self) -> Path:
        return Path(__file__).parent.parent


settings = Settings()
