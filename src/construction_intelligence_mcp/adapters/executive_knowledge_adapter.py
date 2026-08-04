from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter


class ExecutiveKnowledgeRecord(BaseModel):
    """Normalized certified executive knowledge with its original lineage."""

    evidence_id: str
    source_document: str
    source_version: str | None = None
    source_year: int | None = None
    source_section_id: str
    source_heading: str | None = None
    governed_finding: str
    project_id: str | None = None
    programs: list[str] = Field(default_factory=list)
    objectives: list[str] = Field(default_factory=list)
    policy_drivers: list[str] = Field(default_factory=list)
    expected_outcomes: list[str] = Field(default_factory=list)
    strategic_themes: list[str] = Field(default_factory=list)
    districts: list[int] = Field(default_factory=list)
    counties: list[str] = Field(default_factory=list)
    routes: list[str] = Field(default_factory=list)
    asset_categories: list[str] = Field(default_factory=list)
    project_types: list[str] = Field(default_factory=list)
    time_horizon_start: int | None = None
    time_horizon_end: int | None = None
    geographic_applicability: str | None = None
    refined_status: str | None = None


class ExecutiveKnowledgeAdapter:
    """Schema-adaptive, read-only access to certified executive knowledge."""

    RELATIONS = (
        "ci_executive_knowledge",
        "certified_executive_knowledge",
        "executive_knowledge",
    )
    REQUIRED = {
        "evidence_id": ("evidence_id", "knowledge_id", "finding_id"),
        "source_document": ("source_document", "document_title", "source_name"),
        "source_section_id": ("source_section_id", "section_id", "lineage_id"),
        "governed_finding": ("governed_finding", "refined_finding", "source_excerpt"),
    }
    OPTIONAL = {
        "source_version": ("source_version", "document_version"),
        "source_year": ("source_year", "document_year"),
        "source_heading": ("source_heading", "section_heading"),
        "project_id": ("project_id",),
        "programs": ("programs", "program"),
        "objectives": ("objectives", "objective"),
        "policy_drivers": ("policy_drivers", "policy_driver"),
        "expected_outcomes": ("expected_outcomes", "expected_outcome", "owner_outcome"),
        "strategic_themes": ("strategic_themes", "strategic_theme"),
        "districts": ("districts", "district"),
        "counties": ("counties", "county"),
        "routes": ("routes", "route"),
        "asset_categories": ("asset_categories", "asset_category"),
        "project_types": ("project_types", "project_type"),
        "time_horizon_start": ("time_horizon_start", "start_year"),
        "time_horizon_end": ("time_horizon_end", "end_year"),
        "geographic_applicability": ("geographic_applicability", "geography"),
        "refined_status": ("refined_status", "status"),
    }

    def __init__(self, adapter: DuckDBAdapter) -> None:
        self.adapter = adapter
        self.source_relation = next(
            (relation for name in self.RELATIONS if (relation := adapter.resolve_table(name))),
            None,
        )
        self.resolved_fields: dict[str, str | None] = {}
        if self.source_relation is not None:
            columns = set(adapter.columns(self.source_relation))
            for concept, candidates in {**self.REQUIRED, **self.OPTIONAL}.items():
                self.resolved_fields[concept] = next(
                    (candidate for candidate in candidates if candidate in columns), None
                )
            missing = [name for name in self.REQUIRED if self.resolved_fields[name] is None]
            if missing:
                raise RuntimeError(
                    f"Certified executive relation '{self.source_relation}' has unresolved "
                    f"required fields: {', '.join(missing)}."
                )

    def fetch_records(self) -> list[ExecutiveKnowledgeRecord]:
        if self.source_relation is None:
            return []
        projections = [
            (f'"{field}" AS "{concept}"' if field else f'NULL AS "{concept}"')
            for concept, field in self.resolved_fields.items()
        ]
        rows = self.adapter.fetch_all(
            f"SELECT {', '.join(projections)} FROM {self.source_relation}"
        )
        return [self._to_record(row) for row in rows]

    @classmethod
    def _to_record(cls, row: dict[str, Any]) -> ExecutiveKnowledgeRecord:
        list_fields = {
            "programs",
            "objectives",
            "policy_drivers",
            "expected_outcomes",
            "strategic_themes",
            "districts",
            "counties",
            "routes",
            "asset_categories",
            "project_types",
        }
        normalized = dict(row)
        for field in list_fields:
            value = normalized.get(field)
            if value is None:
                normalized[field] = []
            elif not isinstance(value, (list, tuple)):
                normalized[field] = [part.strip() for part in str(value).split(",") if part.strip()]
        normalized["districts"] = [int(value) for value in normalized["districts"]]
        return ExecutiveKnowledgeRecord.model_validate(normalized)
