from __future__ import annotations

from collections import Counter
from pathlib import Path
import os
from typing import Any, Sequence

from construction_intelligence_mcp.adapters.executive_evidence_adapter import (
    CdpPhysicalImplementationMapping,
    ExecutiveEvidenceAdapter,
)
from construction_intelligence_mcp.models.executive_evidence import (
    ExecutiveEvidence,
    ExecutiveEvidenceDiagnostics,
    ExecutiveEvidenceLineage,
    ExecutiveEvidenceResult,
)

ELIGIBLE_STATUSES = {"USABLE", "USABLE_WITH_LIMITATION", "CONTEXT_ONLY"}
REJECTED_STATUSES = {"EXCLUDED", "REVIEW_REQUIRED"}


class ExecutiveEvidenceService:
    """Governed Executive Evidence Engine for CDP-001."""

    def __init__(
        self,
        database: str | Path,
        mappings: Sequence[CdpPhysicalImplementationMapping] | None = None,
    ) -> None:
        self.adapter = ExecutiveEvidenceAdapter(
            database, mappings or self._mappings_from_environment()
        )

    def fetch_executive_evidence(self, *, limit: int | None = None) -> ExecutiveEvidenceResult:
        rows = self.adapter.fetch_evidence_rows()
        status_distribution = Counter(self._status(row) for row in rows)
        unknown_statuses = sorted(
            status
            for status in status_distribution
            if status not in ELIGIBLE_STATUSES | REJECTED_STATUSES
        )
        seen: set[str] = set()
        duplicate_count = 0
        rejected_count = 0
        evidence: list[ExecutiveEvidence] = []
        for row in rows:
            evidence_id = self._clean(row.get("evidence_id"))
            status = self._status(row)
            has_lineage = bool(self._clean(row.get("source_document"))) and bool(
                self._clean(row.get("source_section_id"))
            )
            if (
                not evidence_id
                or status not in ELIGIBLE_STATUSES
                or not has_lineage
                or not self._clean(row.get("source_text"))
            ):
                rejected_count += 1
                continue
            if evidence_id in seen:
                duplicate_count += 1
                rejected_count += 1
                continue
            seen.add(evidence_id)
            evidence.append(self._to_evidence(row, evidence_id, status))
        evidence.sort(key=lambda item: item.evidence_id)
        if limit is not None:
            evidence = evidence[:limit]
        diagnostics = self._diagnostics(
            rows, evidence, rejected_count, duplicate_count, unknown_statuses, status_distribution
        )
        return ExecutiveEvidenceResult(evidence=evidence, diagnostics=diagnostics)

    def _diagnostics(
        self,
        rows: list[dict[str, Any]],
        evidence: list[ExecutiveEvidence],
        rejected_count: int,
        duplicate_count: int,
        unknown_statuses: list[str],
        status_distribution: Counter[str],
    ) -> ExecutiveEvidenceDiagnostics:
        total = len(rows)
        return ExecutiveEvidenceDiagnostics(
            selected_relation=self.adapter.source_relation,
            relation_role="executive_certified_data_product",
            join_path=[self.adapter.source_relation],
            eligible_evidence_count=sum(
                1 for row in rows if self._status(row) in ELIGIBLE_STATUSES
            ),
            rejected_evidence_count=rejected_count,
            duplicate_evidence_count=duplicate_count,
            source_text_coverage=self._coverage(rows, "source_text"),
            source_document_coverage=self._coverage(rows, "source_document"),
            lineage_coverage=(
                0
                if total == 0
                else sum(
                    1
                    for row in rows
                    if self._clean(row.get("source_document"))
                    and self._clean(row.get("source_section_id"))
                )
                / total
            ),
            unknown_statuses=unknown_statuses,
            final_evidence_count=len(evidence),
            status_distribution=dict(sorted(status_distribution.items())),
        )

    def _to_evidence(self, row: dict[str, Any], evidence_id: str, status: str) -> ExecutiveEvidence:
        limitations = self._limitations(row, status)
        source_keys = {
            key: value
            for key in (
                "evidence_id",
                "source_document_id",
                "source_section_id",
                "refined_section_id",
                "source_asset_id",
            )
            if (value := self._clean(row.get(key)))
        }
        lineage = ExecutiveEvidenceLineage(
            source_relation=self.adapter.source_relation,
            source_keys=source_keys,
            source_document_id=self._clean(row.get("source_document_id")),
            source_asset_id=self._clean(row.get("source_asset_id")),
            source_section_id=self._clean(row.get("source_section_id")) or "",
            refined_section_id=self._clean(row.get("refined_section_id")),
            producing_pipeline=self._clean(row.get("producing_pipeline")),
            pipeline_version=self._clean(row.get("pipeline_version")),
        )
        metadata = {
            key: value
            for key in (
                "program",
                "strategic_theme",
                "objective",
                "policy_driver",
                "expected_outcome",
                "project_id",
                "district",
                "county",
                "route",
                "project_type",
                "asset_category",
                "statewide",
                "document_context",
                "applicable_start_date",
                "applicable_end_date",
                "context_only",
            )
            if (value := self._clean(row.get(key)))
        }
        return ExecutiveEvidence(
            evidence_id=evidence_id,
            evidence_type=self._clean(row.get("evidence_type")) or "executive_evidence",
            source_document=self._clean(row.get("source_document")) or "",
            source_section_id=self._clean(row.get("source_section_id")) or "",
            source_text=self._clean(row.get("source_text")) or "",
            refinement_status=status,  # type: ignore[arg-type]
            source_lineage=lineage,
            limitations=limitations,
            semantic_metadata=metadata,
        )

    @classmethod
    def _status(cls, row: dict[str, Any]) -> str:
        return (cls._clean(row.get("refinement_status")) or "UNKNOWN").upper()

    @staticmethod
    def _clean(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @classmethod
    def _coverage(cls, rows: list[dict[str, Any]], field: str) -> float:
        return 0 if not rows else sum(1 for row in rows if cls._clean(row.get(field))) / len(rows)

    @classmethod
    def _limitations(cls, row: dict[str, Any], status: str) -> list[str]:
        raw = cls._clean(row.get("limitations"))
        limitations = [item.strip() for item in raw.split(";") if item.strip()] if raw else []
        if status == "USABLE_WITH_LIMITATION" and not limitations:
            limitations.append("Certified usable with limitation")
        if status == "CONTEXT_ONLY" and not limitations:
            limitations.append("Certified for contextual evidence use only")
        return limitations

    @staticmethod
    def _mappings_from_environment() -> list[CdpPhysicalImplementationMapping]:
        relation = os.environ.get("CDP001_EXECUTIVE_EVIDENCE_RELATION")
        if relation is None:
            return []
        return [
            CdpPhysicalImplementationMapping(
                product_identifier="CDP-001",
                relation=relation,
                certification_status=os.environ.get(
                    "CDP001_EXECUTIVE_EVIDENCE_STATUS",
                    "",
                ),
                relation_role=os.environ.get(
                    "CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE",
                    "certified_current",
                ),
            )
        ]
