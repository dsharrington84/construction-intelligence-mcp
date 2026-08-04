from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from construction_intelligence_mcp.models.opportunity import Opportunity


class PortfolioRequest(BaseModel):
    """The governed opportunity identifiers selected for a pursuit portfolio."""

    opportunity_ids: list[str] = Field(default_factory=list)

    @field_validator("opportunity_ids")
    @classmethod
    def retain_unique_selections(cls, value: list[str]) -> list[str]:
        normalized = [identifier.strip() for identifier in value]
        if any(not identifier for identifier in normalized):
            raise ValueError("opportunity identifiers must not be blank")
        return list(dict.fromkeys(normalized))


class PortfolioExposure(BaseModel):
    name: str
    project_count: int = Field(ge=0)
    programmed_value: float = Field(ge=0)
    share_of_known_revenue: float = Field(ge=0, le=1)


class RiskDistribution(BaseModel):
    risk: str
    project_count: int = Field(ge=0)
    basis: str


class CapacityIndicators(BaseModel):
    project_count: int = Field(ge=0)
    projects_with_known_value: int = Field(ge=0)
    projects_missing_value: int = Field(ge=0)
    average_known_project_value: float | None = Field(default=None, ge=0)
    largest_project_share: float | None = Field(default=None, ge=0, le=1)
    largest_district_share: float | None = Field(default=None, ge=0, le=1)


class StrategicAlignment(BaseModel):
    aligned_project_count: int = Field(ge=0)
    selective_project_count: int = Field(ge=0)
    partner_or_non_target_project_count: int = Field(ge=0)
    unknown_project_count: int = Field(ge=0)
    basis: str


class Portfolio(BaseModel):
    """Explainable aggregate of selected pursuit opportunities; not a delivery plan."""

    selected_projects: list[Opportunity] = Field(default_factory=list)
    total_revenue: float = Field(ge=0)
    revenue_basis: str
    district_exposure: list[PortfolioExposure] = Field(default_factory=list)
    market_exposure: list[PortfolioExposure] = Field(default_factory=list)
    program_mix: list[PortfolioExposure] = Field(default_factory=list)
    risk_distribution: list[RiskDistribution] = Field(default_factory=list)
    opportunity_mix: list[PortfolioExposure] = Field(default_factory=list)
    capacity_indicators: CapacityIndicators
    strategic_alignment: StrategicAlignment
    portfolio_story: str
