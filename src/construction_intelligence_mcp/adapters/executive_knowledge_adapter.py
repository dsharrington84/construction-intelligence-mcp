from __future__ import annotations

import json
import re
from typing import Any, ClassVar

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
    source_lineage: dict[str, str] = Field(default_factory=dict)


class ExecutiveKnowledgeAdapter:
    """Schema-adaptive, read-only access to certified executive knowledge."""

    RELATION_PREFIX: ClassVar[str] = "ci_executive_knowledge_section_"
    FALLBACK_RELATIONS: ClassVar[tuple[str, ...]] = ("ci_executive_knowledge_section_refined",)
    ELIGIBLE_STATUSES: ClassVar[frozenset[str]] = frozenset(
        {"USABLE", "USABLE_WITH_LIMITATION", "CONTEXT_ONLY"}
    )
    EXCLUDED_STATUSES: ClassVar[frozenset[str]] = frozenset({"REVIEW_REQUIRED", "EXCLUDED"})
    REQUIRED: ClassVar[dict[str, tuple[str, ...]]] = {
        "evidence_id": (
            "evidence_id",
            "executive_knowledge_section_id",
            "executive_knowledge_section_refined_id",
            "knowledge_section_id",
            "section_refined_id",
            "section_id",
        ),
        "source_document": (
            "source_document",
            "source_document_name",
            "document_title",
            "document_name",
            "source_file_name",
        ),
        "source_section_id": (
            "source_section_id",
            "source_section_key",
            "section_key",
            "section_id",
            "section_lineage_id",
            "lineage_id",
        ),
        "governed_finding": (
            "governed_finding",
            "refined_finding",
            "refined_section_summary",
            "refined_summary",
            "refined_content",
            "section_summary",
            "concise_finding",
        ),
        "refined_status": ("refined_status", "refinement_status", "usability_status", "status"),
    }
    OPTIONAL: ClassVar[dict[str, tuple[str, ...]]] = {
        "source_version": ("source_version", "document_version", "version_label"),
        "source_year": ("source_year", "document_year", "publication_year", "plan_year"),
        "source_heading": ("source_heading", "section_heading", "heading", "section_title"),
        "project_id": ("project_id",),
        "programs": ("programs", "program", "program_names", "program_alignment"),
        "objectives": ("objectives", "objective", "strategic_objectives"),
        "policy_drivers": ("policy_drivers", "policy_driver", "policy_alignment"),
        "expected_outcomes": (
            "expected_outcomes",
            "expected_outcome",
            "owner_outcomes",
            "owner_outcome",
        ),
        "strategic_themes": ("strategic_themes", "strategic_theme", "theme_tags"),
        "districts": ("districts", "district", "district_numbers"),
        "counties": ("counties", "county"),
        "routes": ("routes", "route"),
        "asset_categories": ("asset_categories", "asset_category"),
        "project_types": ("project_types", "project_type"),
        "time_horizon_start": ("time_horizon_start", "start_year"),
        "time_horizon_end": ("time_horizon_end", "end_year"),
        "geographic_applicability": ("geographic_applicability", "geography"),
    }

    def __init__(self, adapter: DuckDBAdapter) -> None:
        self.adapter = adapter
        candidates = [
            relation
            for relation in adapter.find_tables(self.RELATION_PREFIX)
            if "refined" in relation[1].casefold()
            and not any(
                token in relation[1].casefold()
                for token in ("history", "archive", "staging", "quarantine")
            )
        ]
        current = max(candidates, key=lambda item: self._relation_rank(item[1]), default=None)
        self.source_relation = (
            self._qualified(*current)
            if current
            else next(
                (
                    relation
                    for name in self.FALLBACK_RELATIONS
                    if (relation := adapter.resolve_table(name))
                ),
                None,
            )
        )
        self.resolved_fields: dict[str, str | None] = {}
        self.lineage_fields: list[str] = []
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
            self.lineage_fields = sorted(
                column
                for column in columns
                if any(
                    token in column.casefold()
                    for token in ("source", "lineage", "document", "section", "page")
                )
            )

    def fetch_records(self) -> list[ExecutiveKnowledgeRecord]:
        if self.source_relation is None:
            return []
        rows = self.adapter.fetch_all(f"SELECT * FROM {self.source_relation}")
        records = [self._to_record(row) for row in rows]
        return [record for record in records if record.refined_status in self.ELIGIBLE_STATUSES]

    def eligible_record_counts_by_status(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self.fetch_records():
            status = record.refined_status or "(missing)"
            counts[status] = counts.get(status, 0) + 1
        return dict(sorted(counts.items()))

    def _to_record(self, row: dict[str, Any]) -> ExecutiveKnowledgeRecord:
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
        normalized = {
            concept: row.get(field) if field else None
            for concept, field in self.resolved_fields.items()
        }
        for field in list_fields:
            value = normalized.get(field)
            if value is None:
                normalized[field] = []
            else:
                normalized[field] = self._list_value(value)
        normalized["districts"] = [
            int(match.group())
            for value in normalized["districts"]
            if (match := re.search(r"\d+", str(value)))
        ]
        status = normalized.get("refined_status")
        normalized["refined_status"] = str(status).strip().upper() if status else None
        normalized["source_lineage"] = {
            field: str(row[field]) for field in self.lineage_fields if row.get(field) is not None
        }
        return ExecutiveKnowledgeRecord.model_validate(normalized)

    @staticmethod
    def _list_value(value: Any) -> list[str]:
        if isinstance(value, (list, tuple)):
            return [str(item).strip() for item in value if str(item).strip()]
        text = str(value).strip()
        if text.startswith("["):
            try:
                decoded = json.loads(text)
                if isinstance(decoded, list):
                    return [str(item).strip() for item in decoded if str(item).strip()]
            except json.JSONDecodeError:
                pass
        return [part.strip() for part in re.split(r"[,;|]", text) if part.strip()]

    @staticmethod
    def _relation_version(name: str) -> int:
        match = re.search(r"_v(\d+)$", name)
        return int(match.group(1)) if match else -1

    @classmethod
    def _relation_rank(cls, name: str) -> tuple[int, int]:
        normalized = name.casefold()
        governed_alias = int("current" in normalized or "certified" in normalized)
        return governed_alias, cls._relation_version(normalized)

    def _qualified(self, schema: str, name: str) -> str:
        return f"{self.adapter.quote_identifier(schema)}.{self.adapter.quote_identifier(name)}"
