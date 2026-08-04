from __future__ import annotations

import pytest

from construction_intelligence_mcp.models.project import ProjectSummary
from construction_intelligence_mcp.models.scope import (
    MarketSector,
    PursuitCategory,
    ScopeClassification,
    ScopeConfidence,
)
from construction_intelligence_mcp.services.project_scope_classifier import ProjectScopeClassifier


def project(
    *,
    title: str = "Capital project",
    description: str | None = None,
    project_type: str | None = None,
    location: str | None = None,
    route: str | None = None,
    county: str | None = None,
) -> ProjectSummary:
    return ProjectSummary(
        project_id="P-1",
        title=title,
        description=description,
        project_type=project_type,
        location=location,
        route=route,
        county=county,
        primary_scope="Other",
    )


@pytest.mark.parametrize(
    ("description", "expected_scope"),
    [
        ("Replace existing bridge over Dry Creek", ScopeClassification.BRIDGE_REPLACEMENT),
        ("Seismic retrofit and bridge repair", ScopeClassification.BRIDGE_REHABILITATION),
        ("Widen bridge to add shoulders", ScopeClassification.BRIDGE_WIDENING),
        ("Rehabilitate roadway through town", ScopeClassification.ROADWAY_REHABILITATION),
        ("Cold plane and overlay existing pavement", ScopeClassification.PAVEMENT_REHABILITATION),
        ("Install median barrier and guardrail", ScopeClassification.SAFETY_IMPROVEMENTS),
        ("Upgrade traffic signal and ramp metering", ScopeClassification.TRAFFIC_OPERATIONS),
        ("Install fiber optic ITS equipment", ScopeClassification.ITS_ELECTRICAL),
        ("Replace culvert and improve drainage", ScopeClassification.DRAINAGE),
        ("Construct bike lane and sidewalk", ScopeClassification.COMPLETE_STREETS),
        ("Construct accessible curb ramp", ScopeClassification.ADA_IMPROVEMENTS),
        ("Renew signing and striping", ScopeClassification.SIGNING_STRIPING),
        ("Roadside landscaping and irrigation", ScopeClassification.LANDSCAPING),
    ],
)
def test_classifies_initial_business_scopes(
    description: str, expected_scope: ScopeClassification
) -> None:
    result = ProjectScopeClassifier().classify(project(description=description))

    assert result.primary_scope == expected_scope
    assert result.matched_keywords


def test_uses_every_governed_project_narrative_field() -> None:
    result = ProjectScopeClassifier().classify(
        project(
            title="Improvement project",
            project_type="Electrical upgrades",
            location="At the storm drain",
            route="Route 5",
            county="Orange",
        )
    )

    assert result.primary_scope == ScopeClassification.ITS_ELECTRICAL
    assert result.secondary_scope == ScopeClassification.DRAINAGE
    assert result.market_sector == MarketSector.MULTIDISCIPLINE
    assert result.matched_keywords == ["electrical", "storm drain"]


def test_mixed_scope_has_stable_precedence_and_secondary_scope() -> None:
    classifier = ProjectScopeClassifier()
    mixed = project(description="Replace bridge and install median barrier with new storm drain")

    first = classifier.classify(mixed)
    second = classifier.classify(mixed)

    assert first == second
    assert first.primary_scope == ScopeClassification.BRIDGE_REPLACEMENT
    assert first.secondary_scope == ScopeClassification.DRAINAGE
    assert first.market_sector == MarketSector.MULTIDISCIPLINE
    assert first.confidence == ScopeConfidence.HIGH
    assert first.matched_keywords == ["replace bridge", "storm drain", "median barrier"]


def test_unknown_scope_always_returns_complete_governed_result() -> None:
    result = ProjectScopeClassifier().classify(project(description="Administrative support"))

    assert result.primary_scope == ScopeClassification.OTHER
    assert result.secondary_scope is None
    assert result.market_sector == MarketSector.OTHER
    assert result.pursuit_category == PursuitCategory.NOT_TARGET
    assert result.confidence == ScopeConfidence.UNKNOWN
    assert result.matched_keywords == []


@pytest.mark.parametrize(
    ("description", "confidence"),
    [
        ("Bridge replacement", ScopeConfidence.HIGH),
        ("Culvert and drainage work", ScopeConfidence.MODERATE),
        ("Culvert work", ScopeConfidence.LOW),
        (None, ScopeConfidence.UNKNOWN),
    ],
)
def test_confidence_is_based_on_keyword_strength_and_evidence(
    description: str | None, confidence: ScopeConfidence
) -> None:
    assert (
        ProjectScopeClassifier().classify(project(description=description)).confidence == confidence
    )


def test_keyword_matching_is_case_and_punctuation_insensitive_but_word_bounded() -> None:
    classifier = ProjectScopeClassifier()

    matched = classifier.classify(project(description="COLD-PLANE and OVERLAY pavement"))
    unrelated = classifier.classify(project(description="Benefits analysis"))

    assert matched.matched_keywords == [
        "cold plane and overlay",
        "cold plane",
        "overlay",
        "pavement",
    ]
    assert unrelated.primary_scope == ScopeClassification.OTHER
