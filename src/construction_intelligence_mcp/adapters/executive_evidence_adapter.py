from __future__ import annotations

from pathlib import Path
from typing import Any

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter

_EXECUTIVE_CDP_BLOCKED_MESSAGE = (
    "Executive Evidence Engine is blocked because CDP-001 is IN REVIEW and no current "
    "Executive Certified Data Product relation is certified for Initiative 102 consumption."
)


class ExecutiveEvidenceAdapter:
    """Deferred adapter for the Executive Certified Data Product implementation."""

    def __init__(self, database: str | Path) -> None:
        self.adapter = DuckDBAdapter(database)
        self.source_relation = self._resolve_certified_relation()

    def fetch_evidence_rows(self) -> list[dict[str, Any]]:
        raise RuntimeError(_EXECUTIVE_CDP_BLOCKED_MESSAGE)

    def _resolve_certified_relation(self) -> str:
        raise RuntimeError(_EXECUTIVE_CDP_BLOCKED_MESSAGE)
