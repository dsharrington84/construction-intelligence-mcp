from __future__ import annotations

from collections.abc import Iterable

from construction_intelligence_mcp.models.opportunity_context import OpportunityContext
from construction_intelligence_mcp.models.project_intelligence import (
    IntelligenceEvidence,
    IntelligenceObservation,
    ProjectIntelligence,
)
from construction_intelligence_mcp.services.project_intelligence_service import (
    ProjectIntelligenceService,
)


class OpportunityContextService:
    """Explain why projects surfaced without recommending or scoring them."""

    def __init__(self, project_intelligence_service: ProjectIntelligenceService) -> None:
        self.project_intelligence_service = project_intelligence_service

    def fetch_opportunity_context(self, project_id: str) -> OpportunityContext | None:
        intelligence = self.project_intelligence_service.fetch_project_intelligence(project_id)
        if intelligence is None:
            return None

        observations = self._observations(intelligence)
        by_category = {
            category: sorted(
                {
                    observation.statement
                    for observation in observations
                    if observation.category == category
                }
            )
            for category in (
                "opportunity_driver",
                "strength",
                "weakness",
                "risk",
                "reason_surfaced",
                "portfolio_value",
            )
        }
        evidence = self._deduplicate_evidence(
            item for observation in observations for item in observation.evidence
        )
        return OpportunityContext(
            project_id=intelligence.project.project_id,
            opportunity_drivers=by_category["opportunity_driver"],
            strengths=by_category["strength"],
            weaknesses=by_category["weakness"],
            risks=by_category["risk"],
            reasons_surfaced=by_category["reason_surfaced"],
            portfolio_value=by_category["portfolio_value"],
            confidence=self._confidence(intelligence),
            evidence=evidence,
        )

    @classmethod
    def _observations(cls, intelligence: ProjectIntelligence) -> list[IntelligenceObservation]:
        observations = [
            *intelligence.executive_signals,
            *intelligence.contractor_signals,
            *intelligence.cost_signals,
        ]
        project = intelligence.project
        if project.programmed_value is not None:
            evidence = IntelligenceEvidence(
                source="project_intelligence.programmed_value",
                statement=f"Programmed value is ${project.programmed_value:,.0f}.",
            )
            observations.append(
                IntelligenceObservation(
                    category="portfolio_value",
                    statement=evidence.statement,
                    evidence=[evidence],
                )
            )
        if intelligence.market.work_type_summary is not None:
            summary = intelligence.market.work_type_summary
            evidence = IntelligenceEvidence(
                source="market_context.work_type_summary",
                statement=(
                    f"{summary.project_count} {summary.work_type} project(s) represent "
                    f"${summary.total_programmed_value:,.0f} in the market period."
                ),
            )
            observations.append(
                IntelligenceObservation(
                    category="opportunity_driver",
                    statement=evidence.statement,
                    evidence=[evidence],
                )
            )
        if intelligence.opportunity is not None:
            for reason in intelligence.opportunity.why_it_surfaced:
                evidence = IntelligenceEvidence(
                    source="project_intelligence.opportunity", statement=reason
                )
                observations.append(
                    IntelligenceObservation(
                        category="reason_surfaced", statement=reason, evidence=[evidence]
                    )
                )
        return observations

    @staticmethod
    def _confidence(intelligence: ProjectIntelligence) -> str:
        specialized_contexts = (
            intelligence.executive_signals,
            intelligence.contractor_signals,
            intelligence.cost_signals,
        )
        available = sum(bool(context) for context in specialized_contexts)
        if available == len(specialized_contexts):
            return "high"
        if available:
            return "moderate"
        return "limited"

    @staticmethod
    def _deduplicate_evidence(
        evidence: Iterable[IntelligenceEvidence],
    ) -> list[IntelligenceEvidence]:
        unique = {(item.source, item.statement): item for item in evidence}
        return [unique[key] for key in sorted(unique)]
