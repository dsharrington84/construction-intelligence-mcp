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
    """Assemble certified executive evidence through governed warehouse lineage."""

    RELATION_PREFIX: ClassVar[str] = "ci_executive_knowledge_section_"
    IGNORED_RELATION_TOKENS: ClassVar[tuple[str, ...]] = (
        "history",
        "archive",
        "staging",
        "quarantine",
        "temporary",
    )
    ELIGIBLE_STATUSES: ClassVar[frozenset[str]] = frozenset(
        {"USABLE", "USABLE_WITH_LIMITATION", "CONTEXT_ONLY"}
    )
    EXCLUDED_STATUSES: ClassVar[frozenset[str]] = frozenset({"REVIEW_REQUIRED", "EXCLUDED"})
    REFINED_REQUIRED: ClassVar[dict[str, tuple[str, ...]]] = {
        "evidence_id": (
            "refined_section_key",
            "evidence_id",
            "executive_knowledge_section_refined_id",
            "executive_knowledge_section_id",
            "section_refined_id",
            "refined_section_id",
        ),
        "source_section_id": (
            "source_section_key",
            "source_section_id",
            "source_section_lineage_id",
            "section_lineage_id",
        ),
        "refined_status": (
            "refined_status",
            "refinement_status",
            "usability_status",
        ),
    }
    BASE_CONTENT: ClassVar[tuple[str, ...]] = (
        "governed_finding",
        "governed_content",
        "source_section_content",
        "source_section_text",
        "section_content",
        "section_text",
        "source_text",
        "content_text",
    )
    BASE_SECTION_KEY: ClassVar[tuple[str, ...]] = (
        "section_key",
        "source_section_key",
        "source_section_id",
        "executive_knowledge_section_id",
    )
    DOCUMENT_KEY: ClassVar[tuple[str, ...]] = (
        "source_asset_id",
        "source_asset_key",
        "source_document_id",
        "document_id",
        "document_key",
        "executive_document_id",
    )
    SOURCE_DOCUMENT: ClassVar[tuple[str, ...]] = (
        "source_document",
        "document_title",
        "source_asset_title",
        "source_file_name",
        "file_name",
        "document_name",
    )
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
        self.inspected_relations: dict[str, dict[str, str | None]] = {}
        self._records_cache: list[ExecutiveKnowledgeRecord] | None = None
        self.unmatched_refined_section_count = 0
        self.duplicate_evidence_id_count = 0
        with adapter.connect() as connection:
            schemas = self._discover_schemas(connection)
        self._select_assembly(schemas)

    def fetch_records(self) -> list[ExecutiveKnowledgeRecord]:
        if self._records_cache is not None:
            return list(self._records_cache)
        with self.adapter.connect() as connection:
            rows = self._fetch_assembled_rows(connection)
        records: dict[str, ExecutiveKnowledgeRecord] = {}
        unmatched = 0
        duplicates = 0
        for row in rows:
            if row.get("governed_finding") is None or row.get("source_document") is None:
                unmatched += 1
                continue
            record = self._to_record(row)
            if record.refined_status not in self.ELIGIBLE_STATUSES:
                continue
            if record.evidence_id in records:
                duplicates += 1
                continue
            records[record.evidence_id] = record
        self.unmatched_refined_section_count = unmatched
        self.duplicate_evidence_id_count = duplicates
        self._records_cache = [records[key] for key in sorted(records)]
        return list(self._records_cache)

    def eligible_record_counts_by_status(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self.fetch_records():
            status = record.refined_status or "(missing)"
            counts[status] = counts.get(status, 0) + 1
        return dict(sorted(counts.items()))

    @property
    def diagnostics(self) -> dict[str, Any]:
        return {
            "selected_refined_relation": self.source_relation,
            "selected_base_section_relation": self.base_section_relation,
            "selected_source_document_relation": self.source_document_relation,
            "resolved_fields": dict(self.resolved_fields),
            "join_keys": list(self.join_keys),
            "eligible_record_counts_by_status": self.eligible_record_counts_by_status(),
            "unmatched_refined_section_count": self.unmatched_refined_section_count,
            "duplicate_evidence_id_count": self.duplicate_evidence_id_count,
        }

    def _discover_schemas(self, connection: Any) -> dict[str, set[str]]:
        rows = connection.execute(
            """
            SELECT table_schema, table_name, column_name
            FROM information_schema.columns
            ORDER BY table_schema, table_name, ordinal_position
            """
        ).fetchall()
        schemas: dict[str, set[str]] = {}
        for schema, name, column in rows:
            normalized = str(name).casefold()
            if any(token in normalized for token in self.IGNORED_RELATION_TOKENS):
                continue
            relation = self._qualified(str(schema), str(name))
            schemas.setdefault(relation, set()).add(str(column))
        return schemas

    def _select_assembly(self, schemas: dict[str, set[str]]) -> None:
        for relation, columns in schemas.items():
            concepts = self._relation_concepts(columns)
            if any(concepts.values()):
                self.inspected_relations[relation] = concepts
        refined_candidates = []
        for relation, columns in schemas.items():
            name = self._relation_name(relation)
            if not name.startswith(self.RELATION_PREFIX):
                continue
            fields = self._resolve_named_fields(columns, self.REFINED_REQUIRED)
            if all(fields.values()):
                refined_candidates.append((self._relation_rank(name), relation, fields))
        refined = self._unique_best(refined_candidates, "refined section")
        if refined is None:
            raise RuntimeError(self._assembly_failure("no compatible refined-section relation"))
        _, self.source_relation, refined_fields = refined

        paths = self._assembly_paths(self.source_relation, refined_fields, schemas)
        selected = self._unique_best(paths, "governed assembly path")
        if selected is None:
            raise RuntimeError(
                self._assembly_failure("no governed base-content and source-document join path")
            )
        _, path = selected
        self.base_section_relation = path["base_relation"]
        self.source_document_relation = path["document_relation"]
        self.join_keys = path["join_keys"]
        self._field_sources = path["field_sources"]
        self.resolved_fields = {
            concept: field for concept, (_, field) in self._field_sources.items()
        }
        self.lineage_fields = path["lineage_fields"]

    def _assembly_paths(
        self,
        refined_relation: str,
        refined_fields: dict[str, str | None],
        schemas: dict[str, set[str]],
    ) -> list[tuple[tuple[int, ...], dict[str, Any]]]:
        paths = []
        source_key = refined_fields["source_section_id"]
        assert source_key is not None
        for base_relation, base_columns in schemas.items():
            base_key = self._section_key_field(base_columns)
            content = self._content_field(base_columns)
            same_relation = base_relation == refined_relation
            if not content or (not same_relation and not base_key):
                continue
            section_join = None if same_relation else (source_key, base_key)
            inline_document = self._document_identity_field(base_columns)
            if inline_document:
                paths.append(
                    self._path(
                        refined_relation,
                        refined_fields,
                        base_relation,
                        base_key,
                        content,
                        None,
                        None,
                        inline_document,
                        schemas,
                        section_join,
                    )
                )
                continue
            base_document_key = self._document_key_field(base_columns)
            if not base_document_key:
                continue
            for document_relation, document_columns in schemas.items():
                document_key = self._document_key_field(document_columns)
                document_name = self._document_identity_field(document_columns)
                if not document_key or not document_name:
                    continue
                paths.append(
                    self._path(
                        refined_relation,
                        refined_fields,
                        base_relation,
                        base_key,
                        content,
                        document_relation,
                        document_key,
                        document_name,
                        schemas,
                        section_join,
                        base_document_key,
                    )
                )
        return paths

    def _path(
        self,
        refined_relation: str,
        refined_fields: dict[str, str | None],
        base_relation: str,
        base_key: str | None,
        content: str,
        document_relation: str | None,
        document_key: str | None,
        document_name: str,
        schemas: dict[str, set[str]],
        section_join: tuple[str, str] | None,
        base_document_key: str | None = None,
    ) -> tuple[tuple[int, ...], dict[str, Any]]:
        sources: dict[str, tuple[str, str]] = {
            concept: ("r", field) for concept, field in refined_fields.items() if field is not None
        }
        sources["governed_finding"] = ("b", content)
        sources["source_document"] = ("d" if document_relation else "b", document_name)
        aliases = {"r": refined_relation, "b": base_relation}
        if document_relation:
            aliases["d"] = document_relation
        for concept, candidates in self.OPTIONAL.items():
            for alias in ("r", "b", "d"):
                relation = aliases.get(alias)
                if relation and (field := self._first(schemas[relation], candidates)):
                    sources[concept] = (alias, field)
                    break
        joins = []
        if section_join:
            joins.append(("r", section_join[0], "b", section_join[1]))
        if document_relation and base_document_key and document_key:
            joins.append(("b", base_document_key, "d", document_key))
        lineage = {
            alias: sorted(
                column
                for column in schemas[relation]
                if any(
                    token in column.casefold()
                    for token in ("key", "id", "source", "lineage", "document", "section", "page")
                )
            )
            for alias, relation in aliases.items()
        }
        base_rank = self._relation_rank(self._relation_name(base_relation))
        document_rank = (
            self._relation_rank(self._relation_name(document_relation))
            if document_relation
            else (4, 0)
        )
        rank = (*base_rank, *document_rank)
        return rank, {
            "base_relation": base_relation,
            "document_relation": document_relation,
            "field_sources": sources,
            "join_keys": joins,
            "lineage_fields": lineage,
        }

    def _fetch_assembled_rows(self, connection: Any) -> list[dict[str, Any]]:
        projections = [
            f"{alias}.{self._quote(field)} AS {self._quote(concept)}"
            for concept, (alias, field) in self._field_sources.items()
        ]
        for alias, fields in self.lineage_fields.items():
            projections.extend(
                f"{alias}.{self._quote(field)} AS {self._quote(f'lineage__{alias}__{field}')}"
                for field in fields
            )
        sql = f"SELECT {', '.join(projections)} FROM {self.source_relation} r"
        if self.base_section_relation != self.source_relation:
            left_alias, left_field, right_alias, right_field = self.join_keys[0]
            sql += (
                f" LEFT JOIN {self.base_section_relation} b ON "
                f"{left_alias}.{self._quote(left_field)} = {right_alias}.{self._quote(right_field)}"
            )
        if self.source_document_relation:
            left_alias, left_field, right_alias, right_field = self.join_keys[-1]
            sql += (
                f" LEFT JOIN {self.source_document_relation} d ON "
                f"{left_alias}.{self._quote(left_field)} = {right_alias}.{self._quote(right_field)}"
            )
        status_alias, status_field = self._field_sources["refined_status"]
        eligible_statuses = sorted(self.ELIGIBLE_STATUSES)
        placeholders = ", ".join("?" for _ in eligible_statuses)
        sql += f" WHERE UPPER(CAST({status_alias}.{self._quote(status_field)} AS VARCHAR)) IN ({placeholders})"
        evidence_alias, evidence_field = self._field_sources["evidence_id"]
        sql += f" ORDER BY CAST({evidence_alias}.{self._quote(evidence_field)} AS VARCHAR)"
        cursor = connection.execute(sql, eligible_statuses)
        names = [str(column[0]) for column in cursor.description]
        return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]

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
        normalized = {concept: row.get(concept) for concept in self._field_sources}
        for field in list_fields:
            normalized[field] = self._list_value(normalized.get(field))
        normalized["districts"] = [
            int(match.group())
            for value in normalized["districts"]
            if (match := re.search(r"\d+", str(value)))
        ]
        normalized["refined_status"] = str(normalized["refined_status"]).strip().upper()
        normalized["source_lineage"] = {
            key.removeprefix("lineage__"): str(value)
            for key, value in row.items()
            if key.startswith("lineage__") and value is not None
        }
        return ExecutiveKnowledgeRecord.model_validate(normalized)

    @staticmethod
    def _list_value(value: Any) -> list[str]:
        if value is None:
            return []
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

    @classmethod
    def _resolve_named_fields(
        cls, columns: set[str], concepts: dict[str, tuple[str, ...]]
    ) -> dict[str, str | None]:
        return {
            concept: cls._first(columns, candidates) for concept, candidates in concepts.items()
        }

    @classmethod
    def _relation_concepts(cls, columns: set[str]) -> dict[str, str | None]:
        concepts = cls._resolve_named_fields(columns, cls.REFINED_REQUIRED)
        concepts.update(
            {
                "base_section_key": cls._section_key_field(columns),
                "governed_finding": cls._content_field(columns),
                "source_asset_document_key": cls._document_key_field(columns),
                "source_document": cls._document_identity_field(columns),
            }
        )
        return concepts

    @staticmethod
    def _first(columns: set[str], candidates: tuple[str, ...]) -> str | None:
        return next((candidate for candidate in candidates if candidate in columns), None)

    @classmethod
    def _section_key_field(cls, columns: set[str]) -> str | None:
        exact = cls._first(columns, cls.BASE_SECTION_KEY)
        return exact or next(
            (
                column
                for column in sorted(columns)
                if "section" in column.casefold()
                and column.casefold().endswith(("_key", "_id", "_uid"))
            ),
            None,
        )

    @classmethod
    def _content_field(cls, columns: set[str]) -> str | None:
        exact = cls._first(columns, cls.BASE_CONTENT)
        return exact or next(
            (
                column
                for column in sorted(columns)
                if "refined" not in column.casefold()
                and any(token in column.casefold() for token in ("section", "source", "governed"))
                and any(token in column.casefold() for token in ("content", "text", "finding"))
            ),
            None,
        )

    @classmethod
    def _document_key_field(cls, columns: set[str]) -> str | None:
        exact = cls._first(columns, cls.DOCUMENT_KEY)
        return exact or next(
            (
                column
                for column in sorted(columns)
                if any(token in column.casefold() for token in ("document", "source_asset"))
                and column.casefold().endswith(("_key", "_id", "_uid"))
            ),
            None,
        )

    @classmethod
    def _document_identity_field(cls, columns: set[str]) -> str | None:
        exact = cls._first(columns, cls.SOURCE_DOCUMENT)
        return exact or next(
            (
                column
                for column in sorted(columns)
                if any(token in column.casefold() for token in ("document", "source_asset", "file"))
                and any(token in column.casefold() for token in ("title", "name", "filename"))
            ),
            None,
        )

    @staticmethod
    def _relation_version(name: str) -> int:
        match = re.search(r"_v(\d+)$", name)
        return int(match.group(1)) if match else -1

    @classmethod
    def _relation_rank(cls, name: str) -> tuple[int, int]:
        normalized = name.casefold()
        if "current" in normalized or "certified" in normalized:
            return 3, cls._relation_version(normalized)
        if cls._relation_version(normalized) < 0:
            return 2, -1
        return 1, cls._relation_version(normalized)

    @staticmethod
    def _unique_best(candidates: list[Any], role: str) -> Any | None:
        if not candidates:
            return None
        best_rank = max(candidate[0] for candidate in candidates)
        best = [candidate for candidate in candidates if candidate[0] == best_rank]
        if len(best) > 1:
            relations = sorted(str(candidate[1]) for candidate in best)
            raise RuntimeError(f"Ambiguous {role} candidates at equal rank: {', '.join(relations)}")
        return best[0]

    def _assembly_failure(self, reason: str) -> str:
        details = []
        for relation, fields in sorted(self.inspected_relations.items()):
            resolved = [f"{concept}={field}" for concept, field in fields.items() if field]
            missing = [concept for concept, field in fields.items() if not field]
            details.append(
                f"{relation}: resolved [{', '.join(resolved) or 'none'}]; "
                f"missing [{', '.join(missing) or 'none'}]"
            )
        return (
            f"No governed executive evidence assembly path: {reason}. "
            f"Inspected refined candidates: {'; '.join(details) or 'none'}. "
            "Required joins: refined source-section lineage to governed base content, then "
            "base source-asset/document lineage to governed document identity."
        )

    @staticmethod
    def _relation_name(relation: str) -> str:
        return relation.rsplit(".", maxsplit=1)[-1].strip('"').casefold()

    def _qualified(self, schema: str, name: str) -> str:
        return f"{self.adapter.quote_identifier(schema)}.{self.adapter.quote_identifier(name)}"

    def _quote(self, identifier: str) -> str:
        return self.adapter.quote_identifier(identifier)
