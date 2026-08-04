from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ScopeClassification(StrEnum):
    BRIDGE_REHABILITATION = "Bridge Rehabilitation"
    BRIDGE_REPLACEMENT = "Bridge Replacement"
    BRIDGE_WIDENING = "Bridge Widening"
    ROADWAY_REHABILITATION = "Roadway Rehabilitation"
    PAVEMENT_REHABILITATION = "Pavement Rehabilitation"
    SAFETY_IMPROVEMENTS = "Safety Improvements"
    TRAFFIC_OPERATIONS = "Traffic Operations"
    ITS_ELECTRICAL = "ITS / Electrical"
    DRAINAGE = "Drainage"
    COMPLETE_STREETS = "Complete Streets"
    ADA_IMPROVEMENTS = "ADA Improvements"
    SIGNING_STRIPING = "Signing / Striping"
    LANDSCAPING = "Landscaping"
    OTHER = "Other"


class MarketSector(StrEnum):
    BRIDGE = "Bridge"
    ROADWAY = "Roadway"
    ELECTRICAL = "Electrical"
    CIVIL = "Civil"
    DRAINAGE = "Drainage"
    SAFETY = "Safety"
    MULTIDISCIPLINE = "Multidiscipline"
    OTHER = "Other"


class PursuitCategory(StrEnum):
    SEMA_CORE = "SEMA_CORE"
    SEMA_SELECTIVE = "SEMA_SELECTIVE"
    SEMA_PARTNER = "SEMA_PARTNER"
    NOT_TARGET = "NOT_TARGET"


class ScopeConfidence(StrEnum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class ProjectScope(BaseModel):
    """Explainable, deterministic business classification for a project."""

    primary_scope: ScopeClassification
    secondary_scope: ScopeClassification | None = None
    market_sector: MarketSector
    pursuit_category: PursuitCategory
    confidence: ScopeConfidence
    matched_keywords: list[str] = Field(default_factory=list)
