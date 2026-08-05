from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ExecutiveEvidenceLineage(BaseModel):
    """Certified source lineage preserved for an ExecutiveEvidence object."""

    source_relation: str
    source_keys: dict[str, str] = Field(default_factory=dict)
    source_document_id: str | None = None
    source_asset_id: str | None = None
    source_section_id: str
    refined_section_id: str | None = None
    producing_pipeline: str | None = None
    pipeline_version: str | None = None


class ExecutiveEvidence(BaseModel):
    """Canonical executive evidence exposed by the Executive Evidence Engine."""

    evidence_id: str
    evidence_type: str
    source_document: str
    source_section_id: str
    source_text: str
    refinement_status: Literal["USABLE", "USABLE_WITH_LIMITATION", "CONTEXT_ONLY"]
    source_lineage: ExecutiveEvidenceLineage
    limitations: list[str] = Field(default_factory=list)
    semantic_metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutiveEvidenceDiagnostics(BaseModel):
    """Governed diagnostics for Executive Evidence Engine assembly."""

    selected_relation: str
    relation_role: str
    join_path: list[str] = Field(default_factory=list)
    eligible_evidence_count: int = Field(ge=0)
    rejected_evidence_count: int = Field(ge=0)
    duplicate_evidence_count: int = Field(ge=0)
    source_text_coverage: float = Field(ge=0, le=1)
    source_document_coverage: float = Field(ge=0, le=1)
    lineage_coverage: float = Field(ge=0, le=1)
    unknown_statuses: list[str] = Field(default_factory=list)
    final_evidence_count: int = Field(ge=0)
    status_distribution: dict[str, int] = Field(default_factory=dict)


class ExecutiveEvidenceResult(BaseModel):
    """Evidence response with diagnostics."""

    evidence: list[ExecutiveEvidence]
    diagnostics: ExecutiveEvidenceDiagnostics
