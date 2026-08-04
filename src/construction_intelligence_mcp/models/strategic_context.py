from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field


class RefinedStatus(StrEnum):
    USABLE = "USABLE"
    USABLE_WITH_LIMITATION = "USABLE_WITH_LIMITATION"
    CONTEXT_ONLY = "CONTEXT_ONLY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    EXCLUDED = "EXCLUDED"


class EvidenceType(StrEnum):
    SOURCE_SECTION = "SOURCE_SECTION"
    REFINED_SECTION = "REFINED_SECTION"
    CONTEXT_SECTION = "CONTEXT_SECTION"
    TABLE_CONTEXT = "TABLE_CONTEXT"
    DOCUMENT_CONTEXT = "DOCUMENT_CONTEXT"
    SEMANTIC_RECORD = "SEMANTIC_RECORD"


class EvidenceStrength(StrEnum):
    DIRECT = "DIRECT"
    SUPPORTING = "SUPPORTING"
    CONTEXTUAL = "CONTEXTUAL"


class SourceConfidence(StrEnum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LIMITED = "LIMITED"
    NONE = "NONE"


class SourceLineage(BaseModel):
    relations: list[str]
    keys: dict[str, str]
    producer_scripts: list[str] = Field(default_factory=list)


class ExecutiveEvidence(BaseModel):
    evidence_id: str
    source_section_id: str
    source_document: str
    source_excerpt: str
    refined_status: RefinedStatus
    evidence_type: EvidenceType
    source_lineage: SourceLineage
    source_heading: str | None = None
    source_page: int | None = None
    source_year: int | None = None
    source_version: str | None = None
    document_type: str | None = None
    section_type: str | None = None
    project_id: str | None = None
    program: str | None = None
    region: str | None = None
    district: int | None = None
    county: str | None = None
    route: str | None = None
    project_type: str | None = None
    asset_category: str | None = None
    strategic_theme: str | None = None
    objective: str | None = None
    policy_driver: str | None = None
    expected_outcome: str | None = None
    semantic_tags: list[str] = Field(default_factory=list)
    refinement_confidence: str | None = None
    source_status: str | None = None
    limitations: list[str] = Field(default_factory=list)


class EvidenceBackedConclusion(BaseModel):
    value: str
    evidence_ids: list[str]


class StrategicEvidence(BaseModel):
    evidence_id: str
    source_document: str
    source_section_id: str
    source_heading: str | None = None
    source_excerpt: str
    relationship_to_project: str
    evidence_strength: EvidenceStrength
    evidence_type: EvidenceType
    refined_status: RefinedStatus
    source_lineage: SourceLineage
    limitations: list[str] = Field(default_factory=list)


class StrategicContext(BaseModel):
    project_id: str
    strategic_context_id: str
    programs: list[EvidenceBackedConclusion] = Field(default_factory=list)
    objectives: list[EvidenceBackedConclusion] = Field(default_factory=list)
    policy_drivers: list[EvidenceBackedConclusion] = Field(default_factory=list)
    expected_outcomes: list[EvidenceBackedConclusion] = Field(default_factory=list)
    strategic_themes: list[EvidenceBackedConclusion] = Field(default_factory=list)
    evidence: list[StrategicEvidence] = Field(default_factory=list)
    source_confidence: SourceConfidence = SourceConfidence.NONE
    limitations: list[str] = Field(default_factory=list)


class ExecutiveEvidenceDiagnostics(BaseModel):
    selected_relations: list[str] = Field(default_factory=list)
    relation_roles: dict[str, str] = Field(default_factory=dict)
    producer_scripts: dict[str, list[str]] = Field(default_factory=dict)
    join_keys: list[dict[str, str]] = Field(default_factory=list)
    join_coverage: dict[str, float] = Field(default_factory=dict)
    eligible_status_distribution: dict[str, int] = Field(default_factory=dict)
    source_text_coverage: float = 0
    source_document_coverage: float = 0
    evidence_type_distribution: dict[str, int] = Field(default_factory=dict)
    duplicate_evidence_count: int = 0
    unmatched_lineage_count: int = 0
    excluded_count: int = 0
    review_required_count: int = 0
    unknown_status_counts: dict[str, int] = Field(default_factory=dict)
    final_evidence_record_count: int = 0
    certification_status: str
    certification_limitations: list[str] = Field(default_factory=list)
