from construction_intelligence_mcp.models.project_intelligence import ProjectIntelligence
from construction_intelligence_mcp.server import fetch_project_intelligence

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
    assert response["executive_signals"] == []
    assert fetch_project_intelligence("missing") is None
