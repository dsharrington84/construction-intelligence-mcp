from __future__ import annotations

from collections import defaultdict
from typing import Protocol

from construction_intelligence_mcp.adapters.executive_knowledge_adapter import (
    ExecutiveKnowledgeRecord,
)
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.strategic_context import (
    EvidenceStrength,
    SourceConfidence,
    StrategicConclusion,
    StrategicContext,
    StrategicEvidence,
)
from construction_intelligence_mcp.services.project_service import ProjectService


class ExecutiveKnowledgeRepository(Protocol):
    def fetch_records(self) -> list[ExecutiveKnowledgeRecord]: ...


class StrategicContextService:
    """Deterministically connect projects to certified executive knowledge."""

    def __init__(
        self,
        project_service: ProjectService,
        executive_knowledge: ExecutiveKnowledgeRepository,
    ) -> None:
        self.project_service = project_service
        self.executive_knowledge = executive_knowledge

    def fetch_strategic_context(self, project_id: str) -> StrategicContext | None:
        project = self.project_service.fetch_project(project_id)
        if project is None:
            return None

        matches = []
        for record in self.executive_knowledge.fetch_records():
            matched = self._match(project, record)
            if matched is not None:
                matches.append((record, *matched))
        matches.sort(key=lambda item: (self._strength_rank(item[1]), item[0].evidence_id))

        evidence_by_id: dict[str, StrategicEvidence] = {}
        conclusions: dict[str, dict[str, set[str]]] = {
            name: defaultdict(set)
            for name in (
                "programs",
                "objectives",
                "policy_drivers",
                "expected_outcomes",
                "strategic_themes",
            )
        }
        for record, strength, relationship in matches:
            evidence_by_id.setdefault(
                record.evidence_id,
                StrategicEvidence(
                    evidence_id=record.evidence_id,
                    source_document=record.source_document,
                    source_version=record.source_version,
                    source_year=record.source_year,
                    source_section_id=record.source_section_id,
                    source_heading=record.source_heading,
                    source_excerpt=record.governed_finding,
                    relationship_to_project=relationship,
                    evidence_strength=strength,
                ),
            )
            for field_name in conclusions:
                for value in getattr(record, field_name):
                    if value.strip():
                        conclusions[field_name][value.strip()].add(record.evidence_id)

        evidence = sorted(
            evidence_by_id.values(),
            key=lambda item: (self._strength_rank(item.evidence_strength), item.evidence_id),
        )
        output = {
            name: [
                StrategicConclusion(value=value, evidence_ids=sorted(evidence_ids))
                for value, evidence_ids in sorted(
                    values.items(), key=lambda item: item[0].casefold()
                )
            ]
            for name, values in conclusions.items()
        }
        return StrategicContext(
            project_id=project.project_id,
            strategic_context_id=f"strategic-context:{project.project_id}",
            evidence=evidence,
            source_confidence=self._confidence(evidence),
            **output,
        )

    @classmethod
    def _match(
        cls, project: ProjectDetail, record: ExecutiveKnowledgeRecord
    ) -> tuple[EvidenceStrength, str] | None:
        if record.refined_status and record.refined_status.casefold() not in {
            "certified",
            "refined",
            "approved",
            "published",
        }:
            return None
        if record.project_id:
            return (
                (EvidenceStrength.DIRECT, "Certified finding explicitly identifies this project")
                if record.project_id == project.project_id
                else None
            )

        program = cls._project_program(project)
        if program and cls._contains(record.programs, program):
            return EvidenceStrength.DIRECT, f"Project program matches {program}"
        if project.district is not None and project.district in record.districts:
            return EvidenceStrength.SUPPORTING, f"Applies to Caltrans District {project.district}"
        if project.county and cls._contains(record.counties, project.county):
            return EvidenceStrength.SUPPORTING, f"Applies to project county {project.county}"
        if project.route and cls._contains(record.routes, project.route):
            return EvidenceStrength.SUPPORTING, f"Applies to project route {project.route}"

        scope_values = {
            project.primary_scope,
            project.project_type,
            project.classified_scope.primary_scope.value if project.classified_scope else None,
            project.classified_scope.secondary_scope.value
            if project.classified_scope and project.classified_scope.secondary_scope
            else None,
        }
        for scope in sorted(value for value in scope_values if value):
            if cls._contains(
                record.asset_categories + record.project_types, scope
            ) or cls._contains(record.strategic_themes, scope):
                return EvidenceStrength.SUPPORTING, f"Governed project scope matches {scope}"

        year = project.advertisement_fiscal_year
        if year and (
            (record.time_horizon_start is not None and year < record.time_horizon_start)
            or (record.time_horizon_end is not None and year > record.time_horizon_end)
        ):
            return None
        if (record.geographic_applicability or "").casefold() in {
            "statewide",
            "california",
            "state highway system",
        }:
            return EvidenceStrength.CONTEXTUAL, "Provides statewide strategic context"
        return None

    @staticmethod
    def _project_program(project: ProjectDetail) -> str | None:
        for name in ("program", "program_name", "funding_program"):
            value = project.raw_record.get(name)
            if value is not None and str(value).strip():
                return str(value).strip()
        return None

    @staticmethod
    def _contains(values: list[str], target: str) -> bool:
        normalized = target.strip().casefold()
        return any(value.strip().casefold() == normalized for value in values)

    @staticmethod
    def _strength_rank(strength: EvidenceStrength) -> int:
        return {
            EvidenceStrength.DIRECT: 0,
            EvidenceStrength.SUPPORTING: 1,
            EvidenceStrength.CONTEXTUAL: 2,
        }[strength]

    @staticmethod
    def _confidence(evidence: list[StrategicEvidence]) -> SourceConfidence:
        direct = sum(item.evidence_strength == EvidenceStrength.DIRECT for item in evidence)
        supporting = sum(item.evidence_strength == EvidenceStrength.SUPPORTING for item in evidence)
        if direct and len(evidence) > direct:
            return SourceConfidence.HIGH
        if direct or supporting >= 2:
            return SourceConfidence.MODERATE
        if evidence:
            return SourceConfidence.LIMITED
        return SourceConfidence.NONE
