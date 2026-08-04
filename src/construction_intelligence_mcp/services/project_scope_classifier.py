from __future__ import annotations

import re
from dataclasses import dataclass

from construction_intelligence_mcp.models.project import ProjectSummary
from construction_intelligence_mcp.models.scope import (
    MarketSector,
    ProjectScope,
    PursuitCategory,
    ScopeClassification,
    ScopeConfidence,
)


@dataclass(frozen=True)
class _ScopeRule:
    scope: ScopeClassification
    strong_keywords: tuple[str, ...]
    supporting_keywords: tuple[str, ...] = ()


# Ordering is governed precedence. More specific scopes intentionally precede broad scopes.
_RULES: tuple[_ScopeRule, ...] = (
    _ScopeRule(
        ScopeClassification.BRIDGE_REHABILITATION,
        (
            "bridge rehabilitation",
            "rehabilitate bridge",
            "bridge deck replacement",
            "replace bridge deck",
            "seismic retrofit",
        ),
        ("bridge repair", "bridge deck"),
    ),
    _ScopeRule(
        ScopeClassification.BRIDGE_REPLACEMENT,
        ("bridge replacement", "replace bridge", "replace existing bridge", "new bridge"),
    ),
    _ScopeRule(
        ScopeClassification.BRIDGE_WIDENING,
        ("bridge widening", "widen bridge", "widen existing bridge"),
    ),
    _ScopeRule(
        ScopeClassification.PAVEMENT_REHABILITATION,
        (
            "pavement rehabilitation",
            "rehabilitate pavement",
            "cold plane and overlay",
            "rubberized hot mix asphalt",
            "replace pavement",
        ),
        ("cold plane", "overlay", "resurface", "pavement"),
    ),
    _ScopeRule(
        ScopeClassification.ROADWAY_REHABILITATION,
        ("roadway rehabilitation", "rehabilitate roadway", "roadway reconstruction"),
        ("reconstruct roadway", "roadway repair", "roadway"),
    ),
    _ScopeRule(
        ScopeClassification.ADA_IMPROVEMENTS,
        ("ada improvements", "ada upgrade", "accessible curb ramp"),
        ("ada", "curb ramp", "accessibility"),
    ),
    _ScopeRule(
        ScopeClassification.COMPLETE_STREETS,
        ("complete streets", "active transportation"),
        ("bike lane", "bicycle lane", "pedestrian", "sidewalk", "shared use path"),
    ),
    _ScopeRule(
        ScopeClassification.ITS_ELECTRICAL,
        ("intelligent transportation system", "traffic management system"),
        ("its", "electrical", "lighting", "fiber optic", "changeable message sign"),
    ),
    _ScopeRule(
        ScopeClassification.TRAFFIC_OPERATIONS,
        ("traffic operations", "traffic signal", "ramp metering"),
        ("signal timing", "traffic control system"),
    ),
    _ScopeRule(
        ScopeClassification.DRAINAGE,
        ("drainage improvements", "stormwater", "storm drain"),
        ("drainage", "culvert", "inlet", "outfall"),
    ),
    _ScopeRule(
        ScopeClassification.SAFETY_IMPROVEMENTS,
        ("safety improvements", "safety project"),
        ("guardrail", "median barrier", "concrete barrier", "rumble strip", "crash cushion"),
    ),
    _ScopeRule(
        ScopeClassification.SIGNING_STRIPING,
        ("signing and striping", "signing striping"),
        ("striping", "pavement markings", "roadside sign"),
    ),
    _ScopeRule(
        ScopeClassification.LANDSCAPING,
        ("landscape improvements", "roadside landscaping"),
        ("landscaping", "revegetation", "irrigation"),
    ),
)

_SECTORS = {
    ScopeClassification.BRIDGE_REHABILITATION: MarketSector.BRIDGE,
    ScopeClassification.BRIDGE_REPLACEMENT: MarketSector.BRIDGE,
    ScopeClassification.BRIDGE_WIDENING: MarketSector.BRIDGE,
    ScopeClassification.ROADWAY_REHABILITATION: MarketSector.ROADWAY,
    ScopeClassification.PAVEMENT_REHABILITATION: MarketSector.ROADWAY,
    ScopeClassification.SAFETY_IMPROVEMENTS: MarketSector.SAFETY,
    ScopeClassification.TRAFFIC_OPERATIONS: MarketSector.SAFETY,
    ScopeClassification.ITS_ELECTRICAL: MarketSector.ELECTRICAL,
    ScopeClassification.DRAINAGE: MarketSector.DRAINAGE,
    ScopeClassification.COMPLETE_STREETS: MarketSector.CIVIL,
    ScopeClassification.ADA_IMPROVEMENTS: MarketSector.CIVIL,
    ScopeClassification.SIGNING_STRIPING: MarketSector.SAFETY,
    ScopeClassification.LANDSCAPING: MarketSector.CIVIL,
    ScopeClassification.OTHER: MarketSector.OTHER,
}

_PURSUIT_CATEGORIES = {
    ScopeClassification.BRIDGE_REHABILITATION: PursuitCategory.SEMA_CORE,
    ScopeClassification.BRIDGE_REPLACEMENT: PursuitCategory.SEMA_CORE,
    ScopeClassification.BRIDGE_WIDENING: PursuitCategory.SEMA_CORE,
    ScopeClassification.ROADWAY_REHABILITATION: PursuitCategory.SEMA_CORE,
    ScopeClassification.PAVEMENT_REHABILITATION: PursuitCategory.SEMA_CORE,
    ScopeClassification.DRAINAGE: PursuitCategory.SEMA_CORE,
    ScopeClassification.SAFETY_IMPROVEMENTS: PursuitCategory.SEMA_SELECTIVE,
    ScopeClassification.TRAFFIC_OPERATIONS: PursuitCategory.SEMA_SELECTIVE,
    ScopeClassification.COMPLETE_STREETS: PursuitCategory.SEMA_SELECTIVE,
    ScopeClassification.ADA_IMPROVEMENTS: PursuitCategory.SEMA_SELECTIVE,
    ScopeClassification.ITS_ELECTRICAL: PursuitCategory.SEMA_PARTNER,
    ScopeClassification.SIGNING_STRIPING: PursuitCategory.SEMA_PARTNER,
    ScopeClassification.LANDSCAPING: PursuitCategory.NOT_TARGET,
    ScopeClassification.OTHER: PursuitCategory.NOT_TARGET,
}


class ProjectScopeClassifier:
    """Translate project narrative fields into one governed project scope."""

    def classify(self, project: ProjectSummary) -> ProjectScope:
        text = self._project_text(project)
        matches = [(rule, self._matches(text, rule)) for rule in _RULES]
        matches = [(rule, keywords) for rule, keywords in matches if keywords]
        if not matches:
            return ProjectScope(
                primary_scope=ScopeClassification.OTHER,
                market_sector=MarketSector.OTHER,
                pursuit_category=PursuitCategory.NOT_TARGET,
                confidence=ScopeConfidence.UNKNOWN,
                matched_keywords=[],
            )

        primary_rule, primary_keywords = matches[0]
        secondary_scope = matches[1][0].scope if len(matches) > 1 else None
        all_keywords = [keyword for _, keywords in matches for keyword in keywords]
        sector = (
            MarketSector.MULTIDISCIPLINE
            if secondary_scope is not None
            else _SECTORS[primary_rule.scope]
        )
        return ProjectScope(
            primary_scope=primary_rule.scope,
            secondary_scope=secondary_scope,
            market_sector=sector,
            pursuit_category=_PURSUIT_CATEGORIES[primary_rule.scope],
            confidence=self._confidence(primary_rule, primary_keywords, secondary_scope),
            matched_keywords=all_keywords,
        )

    @staticmethod
    def _project_text(project: ProjectSummary) -> str:
        fields = (
            project.title,
            project.description,
            project.project_type,
            project.location,
            project.route,
            project.county,
        )
        raw_text = " ".join(value for value in fields if value)
        return re.sub(r"[^a-z0-9]+", " ", raw_text.casefold()).strip()

    @staticmethod
    def _matches(text: str, rule: _ScopeRule) -> list[str]:
        keywords = (*rule.strong_keywords, *rule.supporting_keywords)
        return [keyword for keyword in keywords if ProjectScopeClassifier._contains(text, keyword)]

    @staticmethod
    def _contains(text: str, keyword: str) -> bool:
        normalized_keyword = re.sub(r"[^a-z0-9]+", " ", keyword.casefold()).strip()
        return re.search(rf"(?:^| )({re.escape(normalized_keyword)})(?: |$)", text) is not None

    @staticmethod
    def _confidence(
        rule: _ScopeRule,
        primary_keywords: list[str],
        secondary_scope: ScopeClassification | None,
    ) -> ScopeConfidence:
        if any(keyword in rule.strong_keywords for keyword in primary_keywords):
            return ScopeConfidence.HIGH
        if len(primary_keywords) >= 2 or secondary_scope is not None:
            return ScopeConfidence.MODERATE
        return ScopeConfidence.LOW
