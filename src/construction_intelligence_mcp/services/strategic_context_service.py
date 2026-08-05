from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence, Any

from construction_intelligence_mcp.models.executive_evidence import (
    ExecutiveEvidence,
    ExecutiveEvidenceDiagnostics,
    ExecutiveEvidenceResult,
)
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.strategic_context import (
    EvidenceStrength,
    SourceConfidence,
    StrategicConclusion,
    StrategicContext,
    StrategicEvidence,
)


class ProjectProvider(Protocol):
    def fetch_project(self, project_id: str) -> ProjectDetail | None: ...


class ExecutiveEvidenceProvider(Protocol):
    def fetch_executive_evidence(self, *, limit: int | None = None) -> ExecutiveEvidenceResult: ...


_CONCLUSION_FIELDS = {
    "program": "programs",
    "objective": "objectives",
    "policy_driver": "policy_drivers",
    "expected_outcome": "expected_outcomes",
    "strategic_theme": "strategic_themes",
}


class StrategicContextService:
    """Build deterministic StrategicContext from governed projects and ExecutiveEvidence."""

    def __init__(
        self,
        project_provider: ProjectProvider,
        executive_evidence_provider: ExecutiveEvidenceProvider,
    ) -> None:
        self.project_provider = project_provider
        self.executive_evidence_provider = executive_evidence_provider

    def fetch_strategic_context(self, project_id: str) -> StrategicContext | None:
        project = self.project_provider.fetch_project(project_id)
        if project is None:
            return None
        result = self.executive_evidence_provider.fetch_executive_evidence()
        matched = self._matched_evidence(project, result.evidence)
        if not matched:
            return StrategicContext(
                project_id=project.project_id,
                strategic_context_id=self._context_id(project.project_id),
                source_confidence=SourceConfidence.NONE,
                limitations=self._empty_limitations(project, result.diagnostics),
            )
        evidence = [item[1] for item in matched]
        limitations = self._limitations(evidence, result.diagnostics)
        return StrategicContext(
            project_id=project.project_id,
            strategic_context_id=self._context_id(project.project_id),
            evidence=evidence,
            source_confidence=self._confidence(evidence, result.diagnostics),
            limitations=limitations,
            **self._conclusions(matched),
        )

    def _matched_evidence(
        self, project: ProjectDetail, evidence: Sequence[ExecutiveEvidence]
    ) -> list[tuple[ExecutiveEvidence, StrategicEvidence]]:
        by_id: dict[str, tuple[ExecutiveEvidence, StrategicEvidence]] = {}
        for item in evidence:
            relationship = self._relationship(project, item)
            if relationship is None:
                continue
            strategic = StrategicEvidence(
                evidence_id=item.evidence_id,
                source_document=item.source_document,
                source_section_id=item.source_section_id,
                source_excerpt=self._excerpt(item.source_text),
                relationship_to_project=relationship[1],
                evidence_strength=relationship[0],
                source_lineage=item.source_lineage,
                limitations=item.limitations,
            )
            by_id.setdefault(item.evidence_id, (item, strategic))
        return sorted(by_id.values(), key=lambda pair: pair[1].evidence_id)

    def _relationship(
        self, project: ProjectDetail, evidence: ExecutiveEvidence
    ) -> tuple[EvidenceStrength, str] | None:
        metadata = evidence.semantic_metadata or {}
        if self._outside_time_horizon(project, metadata):
            return None
        explicit_projects = self._values(metadata, "project_id", "project_ids")
        if explicit_projects and project.project_id not in explicit_projects:
            return None
        context_only = evidence.refinement_status == "CONTEXT_ONLY" or self._truthy(
            metadata.get("context_only")
        )
        if explicit_projects:
            return self._restricted_strength(context_only, direct=True), "explicit_project_linkage"
        if self._program_plus_attribute(project, metadata):
            return self._restricted_strength(
                context_only
            ), "program_plus_governed_project_attribute"
        for key, value in (
            ("district", project.district),
            ("county", project.county),
            ("route", project.route),
        ):
            if value is not None and str(value) in self._values(metadata, key, f"{key}s"):
                return self._restricted_strength(context_only), f"{key}_linkage"
        if self._project_type_or_asset(project, metadata):
            return self._restricted_strength(context_only), "project_type_or_asset_category_linkage"
        if self._truthy(metadata.get("statewide")) or self._truthy(
            metadata.get("document_context")
        ):
            return EvidenceStrength.CONTEXTUAL, "statewide_or_document_context"
        return None

    def _program_plus_attribute(self, project: ProjectDetail, metadata: dict[str, Any]) -> bool:
        if not self._values(metadata, "program", "programs"):
            return False
        return any(
            [
                project.district is not None
                and str(project.district) in self._values(metadata, "district", "districts"),
                project.county is not None
                and project.county in self._values(metadata, "county", "counties"),
                project.route is not None
                and project.route in self._values(metadata, "route", "routes"),
                self._project_type_or_asset(project, metadata),
            ]
        )

    def _project_type_or_asset(self, project: ProjectDetail, metadata: dict[str, Any]) -> bool:
        project_values = {value for value in (project.project_type, project.primary_scope) if value}
        metadata_values = self._values(
            metadata, "project_type", "project_types", "asset_category", "asset_categories"
        )
        return bool(project_values & metadata_values)

    def _outside_time_horizon(self, project: ProjectDetail, metadata: dict[str, Any]) -> bool:
        if project.advertisement_date is None:
            return False
        start = self._date(metadata.get("applicable_start_date"))
        end = self._date(metadata.get("applicable_end_date"))
        return bool(
            (start and project.advertisement_date < start)
            or (end and project.advertisement_date > end)
        )

    @staticmethod
    def _values(metadata: dict[str, Any], *keys: str) -> set[str]:
        values: set[str] = set()
        for key in keys:
            raw = metadata.get(key)
            if raw is None:
                continue
            items = raw if isinstance(raw, list | tuple | set) else [raw]
            values.update(str(item).strip() for item in items if str(item).strip())
        return values

    @staticmethod
    def _truthy(value: Any) -> bool:
        return str(value).strip().lower() in {"1", "true", "yes", "statewide", "document"}

    @staticmethod
    def _date(value: Any) -> date | None:
        if isinstance(value, date):
            return value
        if value is None:
            return None
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return None

    @staticmethod
    def _restricted_strength(context_only: bool, *, direct: bool = False) -> EvidenceStrength:
        if context_only:
            return EvidenceStrength.CONTEXTUAL
        return EvidenceStrength.DIRECT if direct else EvidenceStrength.SUPPORTING

    @staticmethod
    def _excerpt(text: str, limit: int = 500) -> str:
        return text if len(text) <= limit else f"{text[:limit].rstrip()}…"

    def _conclusions(
        self, matched: list[tuple[ExecutiveEvidence, StrategicEvidence]]
    ) -> dict[str, list[StrategicConclusion]]:
        conclusions: dict[str, dict[str, set[str]]] = {
            field: {} for field in _CONCLUSION_FIELDS.values()
        }
        for executive, strategic in matched:
            if (
                strategic.evidence_strength == EvidenceStrength.CONTEXTUAL
                and executive.refinement_status == "CONTEXT_ONLY"
            ):
                continue
            for key, field in _CONCLUSION_FIELDS.items():
                for value in sorted(self._values(executive.semantic_metadata, key, f"{key}s")):
                    conclusions[field].setdefault(value, set()).add(executive.evidence_id)
        return {
            field: [
                StrategicConclusion(value=value, evidence_ids=sorted(ids))
                for value, ids in sorted(values.items())
            ]
            for field, values in conclusions.items()
        }

    @staticmethod
    def _confidence(
        evidence: list[StrategicEvidence], diagnostics: ExecutiveEvidenceDiagnostics
    ) -> SourceConfidence:
        if not evidence:
            return SourceConfidence.NONE
        if (
            diagnostics.unknown_statuses
            or diagnostics.lineage_coverage < 1
            or diagnostics.source_text_coverage < 1
        ):
            return SourceConfidence.LIMITED
        if any(item.limitations for item in evidence):
            return SourceConfidence.LIMITED
        strengths = [item.evidence_strength for item in evidence]
        if EvidenceStrength.DIRECT in strengths and len(evidence) >= 2:
            return SourceConfidence.HIGH
        if EvidenceStrength.DIRECT in strengths or EvidenceStrength.SUPPORTING in strengths:
            return SourceConfidence.MODERATE
        return SourceConfidence.LIMITED

    @staticmethod
    def _limitations(
        evidence: list[StrategicEvidence], diagnostics: ExecutiveEvidenceDiagnostics
    ) -> list[str]:
        limitations = {limitation for item in evidence for limitation in item.limitations}
        if any(item.evidence_strength == EvidenceStrength.CONTEXTUAL for item in evidence):
            limitations.add(
                "Some Executive evidence is contextual and does not establish direct project causation."
            )
        if diagnostics.unknown_statuses:
            limitations.add("Executive Evidence diagnostics include unknown refinement statuses.")
        if diagnostics.duplicate_evidence_count:
            limitations.add(
                "Duplicate Executive evidence records were rejected by the Evidence Engine."
            )
        return sorted(limitations)

    @staticmethod
    def _empty_limitations(
        project: ProjectDetail, diagnostics: ExecutiveEvidenceDiagnostics
    ) -> list[str]:
        limitations = ["No defensible Executive evidence matched the governed project."]
        if project.district is None and project.county is None and project.route is None:
            limitations.append(
                "Project has insufficient district, county, and route attributes for attribute matching."
            )
        if diagnostics.final_evidence_count == 0:
            limitations.append("Executive Evidence Engine returned no eligible evidence.")
        return limitations

    @staticmethod
    def _context_id(project_id: str) -> str:
        return f"strategic-context:{project_id}"
