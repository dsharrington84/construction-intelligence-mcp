from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from construction_intelligence_mcp.models.project_intelligence import IntelligenceEvidence


class OpportunityContext(BaseModel):
    """Evidence-backed explanation of why a governed project surfaced."""

    project_id: str
    opportunity_drivers: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    reasons_surfaced: list[str] = Field(default_factory=list)
    portfolio_value: list[str] = Field(default_factory=list)
    confidence: Literal["high", "moderate", "limited"]
    evidence: list[IntelligenceEvidence] = Field(default_factory=list)
