"""
API-key RBAC with optional ticker-level scope.

Roles (weakest → strongest): viewer < analyst < admin

Scoped analysts have role="analyst" but allowed_tickers is restricted to a
subset of the corpus (e.g. ["AAPL"] for an Apple-only analyst).
Full analysts and admins have allowed_tickers=None (unrestricted).

Tickers are used (not company names) because they are standardised and match
the "ticker" metadata field in ChromaDB regardless of how the company name
is formatted (e.g. "MICROSOFT CORP" vs "Microsoft Corporation").
"""
from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import settings

_RANK = {"viewer": 0, "analyst": 1, "admin": 2}
_bearer = HTTPBearer(auto_error=False)


@dataclass
class UserContext:
    role: str
    # None = access to all tickers; list = restricted to these ticker symbols
    allowed_tickers: list[str] | None = field(default=None)

    @property
    def is_scoped(self) -> bool:
        return self.allowed_tickers is not None


def _key_to_context(key: str | None) -> UserContext | None:
    if not key:
        return None
    # Full-access roles
    if key == settings.api_key_admin:
        return UserContext("admin", None)
    if key == settings.api_key_analyst:
        return UserContext("analyst", None)
    if key == settings.api_key_viewer:
        return UserContext("viewer", None)
    # Company-scoped analysts (tickers must match the "ticker" field in ChromaDB)
    if key == settings.api_key_apple_analyst:
        return UserContext("analyst", ["AAPL"])
    if key == settings.api_key_msft_analyst:
        return UserContext("analyst", ["MSFT"])
    if key == settings.api_key_amzn_analyst:
        return UserContext("analyst", ["AMZN"])
    if key == settings.api_key_googl_analyst:
        return UserContext("analyst", ["GOOGL"])
    if key == settings.api_key_meta_analyst:
        return UserContext("analyst", ["META"])
    if key == settings.api_key_nvda_analyst:
        return UserContext("analyst", ["NVDA"])
    if key == settings.api_key_tsla_analyst:
        return UserContext("analyst", ["TSLA"])
    if key == settings.api_key_jpm_analyst:
        return UserContext("analyst", ["JPM"])
    if key == settings.api_key_bac_analyst:
        return UserContext("analyst", ["BAC"])
    if key == settings.api_key_wmt_analyst:
        return UserContext("analyst", ["WMT"])
    return None


def require_user(minimum: str = "analyst"):
    """FastAPI dependency factory — validates key and enforces minimum role."""
    min_rank = _RANK[minimum]

    def _dep(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> UserContext:
        key = creds.credentials if creds else None
        ctx = _key_to_context(key)
        if ctx is None:
            raise HTTPException(status_code=401, detail="Missing or invalid API key.")
        if _RANK[ctx.role] < min_rank:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{ctx.role}' is insufficient. Requires '{minimum}' or higher.",
            )
        return ctx

    return _dep


def resolve_context(key: str | None) -> UserContext | None:
    """Resolve a key without raising — useful outside FastAPI dependency injection."""
    return _key_to_context(key)
