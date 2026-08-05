from __future__ import annotations

from pathlib import Path
from typing import Any

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter

CERTIFIED_RELATION_CANDIDATES = (
    "executive_certified_evidence",
    "ci_executive_evidence",
    "executive_evidence",
)

_FIELD_CANDIDATES: dict[str, tuple[str, ...]] = {
    "evidence_id": ("evidence_id", "refined_section_key", "knowledge_record_id"),
    "evidence_type": ("evidence_type", "section_type", "document_type"),
    "source_document": ("source_document", "source_document_id", "document_title", "document_name"),
    "source_document_id": ("source_document_id", "document_id"),
    "source_section_id": ("source_section_id", "source_section_key", "section_id"),
    "refined_section_id": ("refined_section_id", "refined_section_key"),
    "source_asset_id": ("source_asset_id", "artifact_id", "asset_id"),
    "source_text": ("source_text", "source_excerpt", "refined_text", "section_text"),
    "refinement_status": ("refinement_status", "status", "evidence_status"),
    "limitations": ("limitations", "limitation"),
    "producing_pipeline": ("producing_pipeline", "pipeline_name"),
    "pipeline_version": ("pipeline_version",),
    "program": ("program",),
    "strategic_theme": ("strategic_theme",),
    "objective": ("objective",),
    "policy_driver": ("policy_driver",),
    "expected_outcome": ("expected_outcome",),
}


class ExecutiveEvidenceAdapter:
    """Read-only access to the Executive Certified Data Product implementation."""

    def __init__(self, database: str | Path) -> None:
        self.adapter = DuckDBAdapter(database)
        self.source_relation = self._resolve_certified_relation()
        self.columns = set(self.adapter.columns(self.source_relation))
        self.resolved_fields = {
            concept: next((field for field in candidates if field in self.columns), None)
            for concept, candidates in _FIELD_CANDIDATES.items()
        }
        self._validate_required_fields()

    def fetch_evidence_rows(self) -> list[dict[str, Any]]:
        return self.adapter.fetch_all(
            f"SELECT {self._select_projection()} FROM {self.source_relation} ORDER BY evidence_id"
        )

    def _resolve_certified_relation(self) -> str:
        selected = [
            relation
            for name in CERTIFIED_RELATION_CANDIDATES
            if (relation := self.adapter.resolve_table(name)) is not None
        ]
        if not selected:
            raise RuntimeError(
                "Missing Executive Certified Data Product relation. Expected one of: "
                f"{', '.join(CERTIFIED_RELATION_CANDIDATES)}."
            )
        if len(selected) > 1:
            raise RuntimeError(
                "Ambiguous Executive Certified Data Product relations: " + ", ".join(selected)
            )
        return selected[0]

    def _validate_required_fields(self) -> None:
        required = (
            "evidence_id",
            "evidence_type",
            "source_document",
            "source_section_id",
            "source_text",
            "refinement_status",
        )
        unresolved = [field for field in required if self.resolved_fields[field] is None]
        if unresolved:
            raise RuntimeError(
                "Executive Certified Data Product has unresolved required fields: "
                f"{', '.join(unresolved)}. Available columns: "
                f"{', '.join(sorted(self.columns)) or '(none)'}"
            )

    def _select_projection(self) -> str:
        expressions = []
        for alias, field in self.resolved_fields.items():
            if field is None:
                expressions.append(f"NULL AS {alias}")
            else:
                expressions.append(f'CAST("{field}" AS VARCHAR) AS {alias}')
        return ", ".join(expressions)
