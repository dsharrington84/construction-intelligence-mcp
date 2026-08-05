from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from construction_intelligence_mcp.models.executive_evidence import ExecutiveEvidenceLineage


class EvidenceStrength(StrEnum):
    DIRECT = "DIRECT"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"


class SourceConfidence(StrEnum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LIMITED = "LIMITED"
    NONE = "NONE"


class StrategicConclusion(BaseModel):
    """A governed strategic conclusion supported by returned evidence."""

    value: str
    evidence_ids: list[str] = Field(min_length=1)


class StrategicEvidence(BaseModel):
    """Project relationship view of canonical ExecutiveEvidence."""

    evidence_id: str
    source_document: str
    source_section_id: str
    source_excerpt: str
    relationship_to_project: str
    evidence_strength: EvidenceStrength
    source_lineage: ExecutiveEvidenceLineage
    limitations: list[str] = Field(default_factory=list)


class StrategicContext(BaseModel):
    """Evidence-backed explanation of why Caltrans is investing in a project."""

    project_id: str
    strategic_context_id: str
    programs: list[StrategicConclusion] = Field(default_factory=list)
    objectives: list[StrategicConclusion] = Field(default_factory=list)
    policy_drivers: list[StrategicConclusion] = Field(default_factory=list)
    expected_outcomes: list[StrategicConclusion] = Field(default_factory=list)
    strategic_themes: list[StrategicConclusion] = Field(default_factory=list)
    evidence: list[StrategicEvidence] = Field(default_factory=list)
    source_confidence: SourceConfidence
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_conclusion_evidence(self) -> StrategicContext:
        available = {item.evidence_id for item in self.evidence}
        missing: dict[str, list[str]] = {}
        for field in (
            "programs",
            "objectives",
            "policy_drivers",
            "expected_outcomes",
            "strategic_themes",
        ):
            for conclusion in getattr(self, field):
                absent = [
                    evidence_id
                    for evidence_id in conclusion.evidence_ids
                    if evidence_id not in available
                ]
                if absent:
                    missing[f"{field}:{conclusion.value}"] = absent
        if missing:
            raise ValueError(f"Strategic conclusions reference missing evidence IDs: {missing}")
        return self
