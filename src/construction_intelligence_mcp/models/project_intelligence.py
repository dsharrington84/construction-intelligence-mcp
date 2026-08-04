from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field

from construction_intelligence_mcp.models.market import (
    DistrictMarketSummary,
    MarketSummary,
    WorkTypeMarketSummary,
)
from construction_intelligence_mcp.models.opportunity import Opportunity
from construction_intelligence_mcp.models.scope import ProjectScope
from construction_intelligence_mcp.models.strategic_context import StrategicContext


class IntelligenceProject(BaseModel):
    """Canonical project fields exposed by Project Intelligence."""

    project_id: str
    title: str
    description: str | None = None
    district: int | None = None
    county: str | None = None
    route: str | None = None
    location: str | None = None
    advertisement_date: date | None = None
    advertisement_fiscal_year: int | None = None
    programmed_value: float | None = None


class ProjectMarketIntelligence(BaseModel):
    """Project-specific views selected from governed market intelligence."""

    district_summary: DistrictMarketSummary | None = None
    work_type_summary: WorkTypeMarketSummary | None = None
    market_outlook: MarketSummary
    market_trend: float | None = None


class ProjectIntelligence(BaseModel):
    """One composed view of all governed intelligence currently known for a project."""

    project: IntelligenceProject
    classification: ProjectScope
    market: ProjectMarketIntelligence
    opportunity: Opportunity | None = None
    strategic_context: StrategicContext
    executive_signals: list[dict] = Field(default_factory=list)
    contractor_signals: list[dict] = Field(default_factory=list)
    cost_signals: list[dict] = Field(default_factory=list)
