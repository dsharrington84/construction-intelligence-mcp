from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class ContractorConfidence(StrEnum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LIMITED = "LIMITED"
    NONE = "NONE"


class ContractorEvidence(BaseModel):
    evidence_id: str
    contractor_id: str | None = None
    contractor_name: str
    historical_project_id: str
    contract_number: str | None = None
    source_relation: str
    district: int | None = None
    project_type: str | None = None
    role: str
    bid_rank: int | None = Field(default=None, ge=1)
    was_awarded: bool = False
    activity_date: date | None = None
    self_performed: bool | None = None


class ContractorCandidate(BaseModel):
    contractor_id: str | None = None
    contractor_name: str
    roles: list[str]
    comparable_project_count: int = Field(ge=0)
    comparable_bid_count: int = Field(ge=0)
    comparable_win_count: int = Field(ge=0)
    district_project_count: int = Field(ge=0)
    project_type_project_count: int = Field(ge=0)
    market_share: float | None = Field(default=None, ge=0, le=1)
    relevant_experience: list[str] = Field(default_factory=list)
    self_perform_indicators: list[str] = Field(default_factory=list)
    prime_sub_tendency: str
    historical_competitiveness: str
    most_recent_activity_date: date | None = None
    confidence: ContractorConfidence
    evidence_ids: list[str] = Field(min_length=1)


class ContractorContext(BaseModel):
    project_id: str
    likely_pursuers: list[ContractorCandidate] = Field(default_factory=list)
    historical_winners: list[ContractorCandidate] = Field(default_factory=list)
    district_presence: dict[str, int] = Field(default_factory=dict)
    market_share: dict[str, float] = Field(default_factory=dict)
    relevant_experience: dict[str, list[str]] = Field(default_factory=dict)
    self_perform_indicators: dict[str, list[str]] = Field(default_factory=dict)
    prime_sub_tendencies: dict[str, str] = Field(default_factory=dict)
    historical_competitiveness: dict[str, str] = Field(default_factory=dict)
    confidence: ContractorConfidence
    evidence: list[ContractorEvidence] = Field(default_factory=list)


ContractorIntelligence = ContractorContext
