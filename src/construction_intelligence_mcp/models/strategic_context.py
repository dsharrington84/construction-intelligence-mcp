from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class EvidenceStrength(StrEnum):
    DIRECT = "DIRECT"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"


class SourceConfidence(StrEnum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LIMITED = "LIMITED"
    NONE = "NONE"


class StrategicEvidence(BaseModel):
    evidence_id: str
    source_document: str
    source_version: str | None = None
    source_year: int | None = None
    source_section_id: str
    source_heading: str | None = None
    source_excerpt: str
    relationship_to_project: str
    evidence_strength: EvidenceStrength
    source_lineage: dict[str, str] = Field(default_factory=dict)


class StrategicConclusion(BaseModel):
    """One source-backed strategic conclusion."""

    value: str
    evidence_ids: list[str] = Field(min_length=1)


class StrategicContext(BaseModel):
    project_id: str
    strategic_context_id: str
    programs: list[StrategicConclusion] = Field(default_factory=list)
    objectives: list[StrategicConclusion] = Field(default_factory=list)
    policy_drivers: list[StrategicConclusion] = Field(default_factory=list)
    expected_outcomes: list[StrategicConclusion] = Field(default_factory=list)
    strategic_themes: list[StrategicConclusion] = Field(default_factory=list)
    evidence: list[StrategicEvidence] = Field(default_factory=list)
    source_confidence: SourceConfidence = SourceConfidence.NONE

    @model_validator(mode="after")
    def conclusions_reference_evidence(self) -> StrategicContext:
        evidence_ids = {item.evidence_id for item in self.evidence}
        for field_name in (
            "programs",
            "objectives",
            "policy_drivers",
            "expected_outcomes",
            "strategic_themes",
        ):
            for conclusion in getattr(self, field_name):
                missing = set(conclusion.evidence_ids) - evidence_ids
                if missing:
                    raise ValueError(
                        f"{field_name} conclusion '{conclusion.value}' references missing "
                        f"evidence: {', '.join(sorted(missing))}"
                    )
        return self
