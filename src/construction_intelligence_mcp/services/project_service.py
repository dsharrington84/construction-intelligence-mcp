from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter
from construction_intelligence_mcp.models.project import (
    ProjectDetail,
    ProjectSearchRequest,
    ProjectSummary,
)
from construction_intelligence_mcp.services.project_scope_classifier import ProjectScopeClassifier

STATE_TABLE = "ci_market_state"

_FIELD_CANDIDATES: dict[str, tuple[str, ...]] = {
    "project_id": ("project_id", "market_state_id"),
    "title": ("project_title", "project_name", "title", "project_description"),
    "description": (
        "project_description",
        "description",
        "project_scope",
        "scope_description",
        "work_description",
    ),
    "district": ("district",),
    "county": ("county", "counties"),
    "route": ("route", "route_number", "state_route"),
    "location": ("location", "project_location", "location_description"),
    "project_type": ("project_type", "work_type"),
    "programmed_value": ("programmed_amount", "programmed_value", "total_programmed_amount"),
    "advertisement_date": ("advertisement_date", "planned_advertisement_date"),
    "advertisement_fiscal_year": ("advertisement_fiscal_year", "fiscal_year"),
}

class ProjectService:
    """Business-facing access to canonical project intelligence."""

    def __init__(self, database: str | Path) -> None:
        self.adapter = DuckDBAdapter(database)
        self.scope_classifier = ProjectScopeClassifier()
        self.source_table = self.adapter.resolve_table(STATE_TABLE)
        if self.source_table is None:
            raise RuntimeError(
                f"Missing canonical table '{STATE_TABLE}' in DuckDB database "
                f"'{self.adapter.database}'."
            )
        self._columns = set(self.adapter.columns(self.source_table))
        self._fields = {
            concept: next((field for field in candidates if field in self._columns), None)
            for concept, candidates in _FIELD_CANDIDATES.items()
        }
        required = ("project_id", "description")
        unresolved = [field for field in required if self._fields[field] is None]
        if unresolved:
            candidates = "; ".join(
                f"{field}: {', '.join(_FIELD_CANDIDATES[field])}" for field in unresolved
            )
            raise RuntimeError(
                f"Canonical table '{STATE_TABLE}' has unresolved required fields: "
                f"{', '.join(unresolved)}. Expected candidates: {candidates}. "
                f"Available columns: {', '.join(sorted(self._columns)) or '(none)'}"
            )

    @property
    def resolved_fields(self) -> dict[str, str | None]:
        return dict(self._fields)

    def search_projects(self, request: ProjectSearchRequest) -> list[ProjectSummary]:
        select_sql = self._select_projection()
        where: list[str] = []
        parameters: list[Any] = []

        district_field = self._fields["district"]
        if request.districts and district_field:
            placeholders = ", ".join("?" for _ in request.districts)
            where.append(
                f"TRY_CAST(REGEXP_REPLACE(CAST(\"{district_field}\" AS VARCHAR), '[^0-9]', '', 'g') AS INTEGER) IN ({placeholders})"
            )
            parameters.extend(request.districts)

        value_field = self._fields["programmed_value"]
        if request.minimum_programmed_value is not None and value_field:
            where.append(f'TRY_CAST("{value_field}" AS DOUBLE) >= ?')
            parameters.append(request.minimum_programmed_value)

        date_field = self._fields["advertisement_date"]
        if request.advertisement_start and date_field:
            where.append(f'TRY_CAST("{date_field}" AS DATE) >= ?')
            parameters.append(request.advertisement_start)
        if request.advertisement_end and date_field:
            where.append(f'TRY_CAST("{date_field}" AS DATE) <= ?')
            parameters.append(request.advertisement_end)

        if request.text:
            searchable = [
                self._fields[name]
                for name in ("title", "description", "location", "route", "county", "project_type")
                if self._fields[name]
            ]
            if searchable:
                haystack = " || ' ' || ".join(
                    f"COALESCE(CAST(\"{field}\" AS VARCHAR), '')" for field in searchable
                )
                where.append(f"LOWER({haystack}) LIKE ?")
                parameters.append(f"%{request.text.lower()}%")

        where_sql = " WHERE " + " AND ".join(where) if where else ""
        order_sql = " ORDER BY programmed_value DESC NULLS LAST, project_id"
        parameters.append(request.limit)
        rows = self.adapter.fetch_all(
            f"SELECT {select_sql} FROM {self.source_table}{where_sql}{order_sql} LIMIT ?",
            parameters,
        )
        return [self._to_summary(row) for row in rows]

    def fetch_project(self, project_id: str) -> ProjectDetail | None:
        identifier = self._fields["project_id"]
        row = self.adapter.fetch_one(
            f'SELECT * FROM {self.source_table} WHERE CAST("{identifier}" AS VARCHAR) = ? LIMIT 1',
            [project_id],
        )
        if row is None:
            return None
        summary = self._to_summary(self._project_row(row))
        return ProjectDetail(**summary.model_dump(), raw_record=row)

    def count_projects(self, districts: list[int] | None = None) -> int:
        """Count canonical projects, optionally constrained to Caltrans districts."""
        request = ProjectSearchRequest(districts=districts)
        district_field = self._fields["district"]
        if request.districts and district_field is None:
            return 0
        where_sql = ""
        parameters: list[Any] = []
        if request.districts:
            placeholders = ", ".join("?" for _ in request.districts)
            where_sql = (
                " WHERE TRY_CAST(REGEXP_REPLACE(CAST("
                f"\"{district_field}\" AS VARCHAR), '[^0-9]', '', 'g') AS INTEGER) "
                f"IN ({placeholders})"
            )
            parameters.extend(request.districts)
        row = self.adapter.fetch_one(
            f"SELECT COUNT(*) AS project_count FROM {self.source_table}{where_sql}", parameters
        )
        return int(row["project_count"]) if row else 0

    def _select_projection(self) -> str:
        expressions: list[str] = []
        for alias, field in self._fields.items():
            if alias == "project_type":
                output_alias = "raw_project_type"
            else:
                output_alias = alias
            if field is None:
                expressions.append(f"NULL AS {output_alias}")
                continue
            if alias == "district":
                expressions.append(
                    f"TRY_CAST(REGEXP_REPLACE(CAST(\"{field}\" AS VARCHAR), '[^0-9]', '', 'g') AS INTEGER) AS district"
                )
            elif alias == "programmed_value":
                expressions.append(f'TRY_CAST("{field}" AS DOUBLE) AS programmed_value')
            elif alias == "advertisement_date":
                expressions.append(f'TRY_CAST("{field}" AS DATE) AS advertisement_date')
            elif alias == "advertisement_fiscal_year":
                expressions.append(
                    f"TRY_CAST(REGEXP_EXTRACT(CAST(\"{field}\" AS VARCHAR), '(20[0-9]{{2}})', 1) AS INTEGER) AS advertisement_fiscal_year"
                )
            else:
                expressions.append(f'CAST("{field}" AS VARCHAR) AS {output_alias}')
        return ", ".join(expressions)

    def _project_row(self, row: dict[str, Any]) -> dict[str, Any]:
        projected: dict[str, Any] = {}
        for alias, field in self._fields.items():
            projected["raw_project_type" if alias == "project_type" else alias] = (
                row.get(field) if field else None
            )
        return projected

    def _to_summary(self, row: dict[str, Any]) -> ProjectSummary:
        project_id = str(row.get("project_id") or "")
        description = self._clean(row.get("description"))
        title = self._clean(row.get("title")) or description or f"Project {project_id}"
        raw_project_type = self._clean(row.get("raw_project_type"))
        value = self._float_or_none(row.get("programmed_value"))
        district = self._int_or_none(row.get("district"))
        reasons = ["Advertises within selected window"]
        if district in {7, 8, 11, 12}:
            reasons.append(f"Southern California District {district}")
        if value is not None and value >= 25_000_000:
            reasons.append("Large programmed value")
        project = ProjectSummary(
            project_id=project_id,
            title=title,
            description=description,
            district=district,
            county=self._clean(row.get("county")),
            route=self._clean(row.get("route")),
            location=self._clean(row.get("location")),
            project_type=raw_project_type,
            primary_scope="Other",
            programmed_value=value,
            advertisement_date=self._date_or_none(row.get("advertisement_date")),
            advertisement_fiscal_year=self._int_or_none(row.get("advertisement_fiscal_year")),
            why_it_surfaced=reasons,
            source_fields=self.resolved_fields,
        )
        classification = self.scope_classifier.classify(project)
        project.primary_scope = classification.primary_scope.value
        project.classified_scope = classification
        if classification.confidence.value != "UNKNOWN":
            project.why_it_surfaced.append(classification.primary_scope.value)
        return project

    @staticmethod
    def _clean(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _float_or_none(value: Any) -> float | None:
        try:
            return None if value is None else float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _int_or_none(value: Any) -> int | None:
        try:
            return None if value is None else int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _date_or_none(value: Any) -> date | None:
        if value is None or isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None
