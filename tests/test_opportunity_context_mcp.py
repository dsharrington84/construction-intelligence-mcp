from construction_intelligence_mcp.models.opportunity_context import OpportunityContext
from construction_intelligence_mcp.server import fetch_opportunity_context


class StubOpportunityContextService:
    def fetch_opportunity_context(self, project_id: str) -> OpportunityContext | None:
        if project_id != "P-1":
            return None
        return OpportunityContext(project_id=project_id, confidence="limited")


def test_fetch_opportunity_context_mcp_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "construction_intelligence_mcp.server._opportunity_context_service",
        StubOpportunityContextService,
    )

    response = fetch_opportunity_context("P-1")

    assert response == {
        "project_id": "P-1",
        "opportunity_drivers": [],
        "strengths": [],
        "weaknesses": [],
        "risks": [],
        "reasons_surfaced": [],
        "portfolio_value": [],
        "confidence": "limited",
        "evidence": [],
    }
    assert fetch_opportunity_context("missing") is None
