import pytest

from construction_intelligence_mcp.models.project_intelligence import ProjectIntelligence
from construction_intelligence_mcp.models.strategic_context import (
    SourceConfidence,
    StrategicContext,
)
from construction_intelligence_mcp.server import fetch_project_intelligence, fetch_strategic_context

from test_project_intelligence_service import (
    governed_market,
    governed_project,
)


class StubIntelligenceService:
    def __init__(self, intelligence: ProjectIntelligence) -> None:
        self.intelligence = intelligence

    def fetch_project_intelligence(self, project_id: str) -> ProjectIntelligence | None:
        return self.intelligence if project_id == self.intelligence.project.project_id else None


def test_fetch_project_intelligence_mcp_response(monkeypatch) -> None:
    project = governed_project()
    intelligence = ProjectIntelligence(
        project=project.model_dump(),
        classification=project.classified_scope,
        market={"market_outlook": governed_market(), "market_trend": None},
        opportunity=None,
    )
    monkeypatch.setattr(
        "construction_intelligence_mcp.server._project_intelligence_service",
        lambda: StubIntelligenceService(intelligence),
    )

    response = fetch_project_intelligence("P-1")

    assert response is not None
    assert response["project"]["project_id"] == "P-1"
    assert response["classification"]["primary_scope"] == "Bridge Replacement"
    assert response["strategic_context"] is None
    assert fetch_project_intelligence("missing") is None


class StubStrategicContextService:
    def __init__(self, context: StrategicContext) -> None:
        self.context = context

    def fetch_strategic_context(self, project_id: str) -> StrategicContext | None:
        return self.context if project_id == self.context.project_id else None


def test_fetch_strategic_context_mcp_response(monkeypatch) -> None:
    strategic_context = StrategicContext(
        project_id="P-1",
        strategic_context_id="strategic-context:P-1",
        source_confidence=SourceConfidence.NONE,
        limitations=["No defensible Executive evidence matched the governed project."],
    )
    monkeypatch.setattr(
        "construction_intelligence_mcp.server._strategic_context_service",
        lambda: StubStrategicContextService(strategic_context),
    )

    response = fetch_strategic_context("P-1")

    assert response is not None
    assert response["project_id"] == "P-1"
    assert response["source_confidence"] == "NONE"
    assert fetch_strategic_context("missing") is None


def test_fetch_strategic_context_missing_mapping_fails_clearly(monkeypatch) -> None:
    monkeypatch.delenv("CDP001_EXECUTIVE_EVIDENCE_RELATION", raising=False)

    with pytest.raises(RuntimeError, match="No accepted CDP-001 physical implementation mapping"):
        fetch_strategic_context("P-1")
