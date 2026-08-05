from construction_intelligence_mcp.models.contractor import (
    ContractorConfidence,
    ContractorContext,
)
from construction_intelligence_mcp.server import fetch_contractor_context


class StubContractorService:
    def fetch_contractor_context(self, project_id: str):
        if project_id == "missing":
            return None
        return ContractorContext(project_id=project_id, confidence=ContractorConfidence.NONE)


def test_fetch_contractor_context_serializes_governed_model(monkeypatch) -> None:
    monkeypatch.setattr(
        "construction_intelligence_mcp.server._contractor_service",
        StubContractorService,
    )

    assert fetch_contractor_context("P-1") == {
        "project_id": "P-1",
        "likely_pursuers": [],
        "historical_winners": [],
        "district_presence": {},
        "market_share": {},
        "relevant_experience": {},
        "self_perform_indicators": {},
        "prime_sub_tendencies": {},
        "historical_competitiveness": {},
        "confidence": "NONE",
        "evidence": [],
    }
    assert fetch_contractor_context("missing") is None
