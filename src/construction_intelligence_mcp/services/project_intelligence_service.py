from __future__ import annotations

from construction_intelligence_mcp.models.market import MarketSummaryRequest
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.project_intelligence import (
    IntelligenceProject,
    ProjectIntelligence,
    ProjectMarketIntelligence,
)
from construction_intelligence_mcp.services.market_service import MarketService
from construction_intelligence_mcp.services.opportunity_service import (
    _OPPORTUNITY_ID_PREFIX,
    OpportunityService,
)
from construction_intelligence_mcp.services.project_service import ProjectService
from construction_intelligence_mcp.services.strategic_context_service import (
    StrategicContextService,
)


class ProjectIntelligenceService:
    """Compose existing governed services into one canonical project view."""

    def __init__(
        self,
        project_service: ProjectService,
        market_service: MarketService,
        opportunity_service: OpportunityService,
        strategic_context_service: StrategicContextService | None = None,
    ) -> None:
        self.project_service = project_service
        self.market_service = market_service
        self.opportunity_service = opportunity_service
        self.strategic_context_service = strategic_context_service

    def fetch_project_intelligence(self, project_id: str) -> ProjectIntelligence | None:
        project = self.project_service.fetch_project(project_id)
        if project is None:
            return None
        if project.classified_scope is None:
            raise RuntimeError(
                f"Project '{project.project_id}' is missing its governed scope classification."
            )

        market_request = (
            MarketSummaryRequest(districts=[project.district])
            if project.district is not None
            else MarketSummaryRequest()
        )
        market = self.market_service.summarize_market(market_request)
        opportunity = self.opportunity_service.fetch_opportunity(
            f"{_OPPORTUNITY_ID_PREFIX}{project.project_id}"
        )
        strategic_context = (
            self.strategic_context_service.fetch_strategic_context(project.project_id)
            if self.strategic_context_service is not None
            else None
        )

        return ProjectIntelligence(
            project=self._project_fields(project),
            classification=project.classified_scope,
            market=ProjectMarketIntelligence(
                district_summary=next(
                    (
                        summary
                        for summary in market.by_district
                        if summary.district == project.district
                    ),
                    None,
                ),
                work_type_summary=next(
                    (
                        summary
                        for summary in market.by_work_type
                        if summary.work_type == project.primary_scope
                    ),
                    None,
                ),
                market_outlook=market,
                market_trend=market.period.prior_period_change,
            ),
            opportunity=opportunity,
            strategic_context=strategic_context,
        )

    @staticmethod
    def _project_fields(project: ProjectDetail) -> IntelligenceProject:
        return IntelligenceProject.model_validate(
            project.model_dump(include=set(IntelligenceProject.model_fields))
        )
