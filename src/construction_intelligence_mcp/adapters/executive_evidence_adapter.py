from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter

ACCEPTED_MAPPING_STATUSES = {"ACCEPTED", "CURRENT"}
PROHIBITED_RELATION_ROLES = {
    "archive",
    "candidate",
    "diagnostic",
    "history",
    "quarantine",
    "review",
    "staging",
    "temporary",
}


@dataclass(frozen=True)
class CdpPhysicalImplementationMapping:
    """Explicit governed physical implementation mapping for one CDP relation."""

    product_identifier: str
    relation: str
    certification_status: str
    relation_role: str = "certified_current"


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
    """Read-only adapter for an explicitly mapped CDP-001 physical implementation."""

    def __init__(
        self,
        database: str | Path,
        mappings: Sequence[CdpPhysicalImplementationMapping],
    ) -> None:
        self.adapter = DuckDBAdapter(database)
        self.mapping = self._select_mapping(mappings)
        self.source_relation = self._resolve_mapped_relation(self.mapping)
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

    def _select_mapping(
        self,
        mappings: Sequence[CdpPhysicalImplementationMapping],
    ) -> CdpPhysicalImplementationMapping:
        cdp_mappings = [mapping for mapping in mappings if mapping.product_identifier == "CDP-001"]
        if not cdp_mappings:
            raise RuntimeError("No accepted CDP-001 physical implementation mapping is configured.")
        accepted = [
            mapping
            for mapping in cdp_mappings
            if mapping.certification_status.upper() in ACCEPTED_MAPPING_STATUSES
        ]
        if not accepted:
            statuses = ", ".join(sorted({mapping.certification_status for mapping in cdp_mappings}))
            raise RuntimeError(
                "CDP-001 physical implementation mapping is not accepted/current. "
                f"Configured status: {statuses or '(none)'}"
            )
        if len(accepted) > 1:
            relations = ", ".join(mapping.relation for mapping in accepted)
            raise RuntimeError(
                "Ambiguous CDP-001 physical implementation mappings; expected exactly one "
                f"accepted/current mapping but found: {relations}"
            )
        mapping = accepted[0]
        if mapping.relation_role.lower() in PROHIBITED_RELATION_ROLES:
            raise RuntimeError(
                "CDP-001 physical implementation mapping points to prohibited relation role: "
                f"{mapping.relation_role}"
            )
        return mapping

    def _resolve_mapped_relation(self, mapping: CdpPhysicalImplementationMapping) -> str:
        parsed = self._parse_schema_qualified_relation(mapping.relation)
        if parsed is None:
            raise RuntimeError(
                "CDP-001 physical implementation mapping must identify a schema-qualified relation."
            )
        schema, relation = parsed
        qualified = (
            f"{self.adapter.quote_identifier(schema)}.{self.adapter.quote_identifier(relation)}"
        )
        if qualified not in self.adapter.relations():
            raise RuntimeError(
                "Mapped CDP-001 physical implementation relation does not exist: "
                f"{schema}.{relation}"
            )
        return qualified

    @staticmethod
    def _parse_schema_qualified_relation(relation: str) -> tuple[str, str] | None:
        parts = [part.strip() for part in relation.split(".")]
        if len(parts) != 2 or not all(parts):
            return None
        return parts[0], parts[1]

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
                "Executive Certified Data Product has unresolved required concepts: "
                f"{', '.join(unresolved)}. Available columns: "
                f"{', '.join(sorted(self.columns)) or '(none)'}"
            )

    def _select_projection(self) -> str:
        expressions = []
        for alias, field in self.resolved_fields.items():
            if field is None:
                expressions.append(f"NULL AS {alias}")
            else:
                expressions.append(f"{self.adapter.quote_identifier(field)} AS {alias}")
        return ", ".join(expressions)
