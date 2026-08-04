from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class CostConfidence(StrEnum):
    """Strength of the historical evidence supporting the cost baseline."""

    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class CostStatistics(BaseModel):
    observation_count: int = Field(ge=1)
    minimum: float = Field(ge=0)
    median: float = Field(ge=0)
    mean: float = Field(ge=0)
    maximum: float = Field(ge=0)


class HistoricalCost(BaseModel):
    """Observed project-cost range; this is a market baseline, not an estimate."""

    basis: str = "Median of comparable historical project costs"
    statistics: CostStatistics
    baseline_cost: float = Field(ge=0)


class HistoricalUnitPrice(BaseModel):
    bid_item_code: str
    description: str | None = None
    unit: str
    statistics: CostStatistics


class BidItemDistribution(BaseModel):
    bid_item_code: str
    description: str | None = None
    unit: str
    observation_count: int = Field(ge=1)
    total_quantity: float | None = Field(default=None, ge=0)
    share_of_observations: float = Field(ge=0, le=1)


class EscalationBasis(BaseModel):
    applied: bool
    method: str
    factor: float | None = Field(default=None, gt=0)
    source_date: date | None = None
    target_date: date | None = None
    source: str | None = None


class ComparableProject(BaseModel):
    project_id: str
    contract_number: str | None = None
    description: str | None = None
    primary_scope: str
    district: int | None = None
    bid_date: date | None = None
    historical_cost: float = Field(ge=0)
    escalated_cost: float = Field(ge=0)
    escalation_factor: float = Field(gt=0)
    match_basis: str
    source_relation: str


class CostVariance(BaseModel):
    reference_value: float = Field(ge=0)
    baseline_cost: float = Field(ge=0)
    amount: float
    percent: float | None = None
    interpretation: str


class CostEvidence(BaseModel):
    source_relation: str
    project_id: str
    contract_number: str | None = None
    bid_date: date | None = None
    bid_item_code: str | None = None
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = None
    unit_price: float | None = Field(default=None, ge=0)
    historical_cost: float | None = Field(default=None, ge=0)


class CostContext(BaseModel):
    """Governed historical market context for a project, never a bid estimate."""

    project_id: str
    historical_cost: HistoricalCost | None = None
    historical_unit_prices: list[HistoricalUnitPrice] = Field(default_factory=list)
    bid_item_distribution: list[BidItemDistribution] = Field(default_factory=list)
    cost_confidence: CostConfidence = CostConfidence.NONE
    escalation_basis: EscalationBasis
    comparable_projects: list[ComparableProject] = Field(default_factory=list)
    variance: CostVariance | None = None
    evidence: list[CostEvidence] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
