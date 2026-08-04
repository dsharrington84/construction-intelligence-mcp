from __future__ import annotations

from collections.abc import Callable, Iterable

from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.strategic_context import (
    EvidenceBackedConclusion,
    EvidenceStrength,
    ExecutiveEvidence,
    RefinedStatus,
    SourceConfidence,
    StrategicContext,
    StrategicEvidence,
)


class StrategicContextService:
    """Deterministically align governed Executive evidence to governed projects."""

    def __init__(self, evidence_provider: Callable[[], Iterable[ExecutiveEvidence]]) -> None:
        self._evidence_provider = evidence_provider

    def fetch_strategic_context(self, project: ProjectDetail) -> StrategicContext:
        matched: dict[str, tuple[ExecutiveEvidence, EvidenceStrength, str]] = {}
        for item in self._evidence_provider():
            result = self._match(project, item)
            if result is not None and item.refined_status not in {
                RefinedStatus.REVIEW_REQUIRED,
                RefinedStatus.EXCLUDED,
            }:
                strength, relationship = result
                if item.refined_status == RefinedStatus.CONTEXT_ONLY:
                    strength = EvidenceStrength.CONTEXTUAL
                    relationship = "Governed context-only owner evidence"
                matched.setdefault(item.evidence_id, (item, strength, relationship))

        ordered = sorted(matched.values(), key=lambda value: (value[1].value, value[0].evidence_id))
        evidence = [self._strategic_evidence(*value) for value in ordered]
        limitations = sorted({limit for item, _, _ in ordered for limit in item.limitations})
        return StrategicContext(
            project_id=project.project_id,
            strategic_context_id=f"strategic-context:{project.project_id}",
            programs=self._conclusions(ordered, "program"),
            objectives=self._conclusions(ordered, "objective"),
            policy_drivers=self._conclusions(ordered, "policy_driver"),
            expected_outcomes=self._conclusions(ordered, "expected_outcome"),
            strategic_themes=self._conclusions(ordered, "strategic_theme"),
            evidence=evidence,
            source_confidence=self._confidence(evidence),
            limitations=limitations,
        )

    @staticmethod
    def _match(
        project: ProjectDetail, item: ExecutiveEvidence
    ) -> tuple[EvidenceStrength, str] | None:
        if item.project_id and item.project_id == project.project_id:
            return EvidenceStrength.DIRECT, "Explicit governed project linkage"
        if item.route and project.route and item.route.casefold() == project.route.casefold():
            return EvidenceStrength.DIRECT, "Governed route linkage"
        if item.county and project.county and item.county.casefold() == project.county.casefold():
            return EvidenceStrength.DIRECT, "Governed county linkage"
        if item.district is not None and item.district == project.district and item.program:
            return EvidenceStrength.DIRECT, "Governed district and program linkage"
        scope_values = {
            project.project_type,
            project.primary_scope,
            project.classified_scope.primary_scope.value if project.classified_scope else None,
            project.classified_scope.market_sector.value if project.classified_scope else None,
        }
        if (item.project_type and item.project_type in scope_values) or (
            item.asset_category and item.asset_category in scope_values
        ):
            return EvidenceStrength.SUPPORTING, "Governed project-type or asset alignment"
        if item.region or item.district is not None or item.route or item.county or item.project_id:
            return None
        return EvidenceStrength.CONTEXTUAL, "Statewide or owner document context"

    @staticmethod
    def _strategic_evidence(
        item: ExecutiveEvidence, strength: EvidenceStrength, relationship: str
    ) -> StrategicEvidence:
        limitations = list(item.limitations)
        if item.refined_status == RefinedStatus.USABLE_WITH_LIMITATION and not limitations:
            limitations.append("Evidence is certified as usable with limitation.")
        return StrategicEvidence(
            **item.model_dump(
                include={
                    "evidence_id",
                    "source_document",
                    "source_section_id",
                    "source_heading",
                    "source_excerpt",
                    "evidence_type",
                    "refined_status",
                    "source_lineage",
                }
            ),
            relationship_to_project=relationship,
            evidence_strength=strength,
            limitations=limitations,
        )

    @staticmethod
    def _conclusions(
        matched: list[tuple[ExecutiveEvidence, EvidenceStrength, str]], field: str
    ) -> list[EvidenceBackedConclusion]:
        values: dict[str, list[str]] = {}
        for item, _, _ in matched:
            value = getattr(item, field)
            if value:
                values.setdefault(value, []).append(item.evidence_id)
        return [
            EvidenceBackedConclusion(value=value, evidence_ids=sorted(set(ids)))
            for value, ids in sorted(values.items())
        ]

    @staticmethod
    def _confidence(evidence: list[StrategicEvidence]) -> SourceConfidence:
        direct = sum(item.evidence_strength == EvidenceStrength.DIRECT for item in evidence)
        supporting = sum(item.evidence_strength == EvidenceStrength.SUPPORTING for item in evidence)
        limited = any(item.limitations for item in evidence)
        if direct and supporting and not limited:
            return SourceConfidence.HIGH
        if (direct or supporting >= 2) and not limited:
            return SourceConfidence.MODERATE
        if evidence:
            return SourceConfidence.LIMITED
        return SourceConfidence.NONE
