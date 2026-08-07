from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from construction_intelligence_mcp.models.opportunity import Opportunity
from construction_intelligence_mcp.models.portfolio import (
    CapacityIndicators,
    Portfolio,
    PortfolioExposure,
    PortfolioRequest,
    RiskDistribution,
    StrategicAlignment,
)
from construction_intelligence_mcp.services.opportunity_service import OpportunityService

_CORE_SCOPES = ("bridge", "roadway", "pavement", "drainage")
_SELECTIVE_SCOPES = ("safety", "traffic", "complete streets", "ada")
_PARTNER_SCOPES = ("electrical", "signing", "striping", "landscaping")


class PortfolioService:
    """Aggregate selected opportunities without scheduling, staffing, or estimating them."""

    def __init__(self, opportunity_service: OpportunityService) -> None:
        self.opportunity_service = opportunity_service

    def fetch_portfolio(self, request: PortfolioRequest) -> Portfolio:
        opportunities = self._resolve_opportunities(request.opportunity_ids)
        total_revenue = sum(item.programmed_value or 0 for item in opportunities)
        known_values = [
            item.programmed_value for item in opportunities if item.programmed_value is not None
        ]
        district_exposure = self._exposure(
            opportunities,
            lambda item: f"District {item.district}" if item.district is not None else "Unknown",
            total_revenue,
        )
        market_exposure = self._exposure(
            opportunities, lambda item: self._market(item.primary_scope), total_revenue
        )
        program_mix = self._exposure(
            opportunities,
            lambda item: (
                str(item.advertisement_fiscal_year)
                if item.advertisement_fiscal_year is not None
                else "Unprogrammed"
            ),
            total_revenue,
        )
        opportunity_mix = self._exposure(
            opportunities, lambda item: item.primary_scope, total_revenue
        )
        return Portfolio(
            selected_projects=opportunities,
            total_revenue=total_revenue,
            revenue_basis="Sum of known programmed values; missing values contribute zero.",
            district_exposure=district_exposure,
            market_exposure=market_exposure,
            program_mix=program_mix,
            risk_distribution=self._risk_distribution(opportunities),
            opportunity_mix=opportunity_mix,
            capacity_indicators=CapacityIndicators(
                project_count=len(opportunities),
                projects_with_known_value=len(known_values),
                projects_missing_value=len(opportunities) - len(known_values),
                average_known_project_value=(
                    sum(known_values) / len(known_values) if known_values else None
                ),
                largest_project_share=(
                    max(known_values) / total_revenue if total_revenue else None
                ),
                largest_district_share=self._largest_share(district_exposure, len(opportunities)),
            ),
            strategic_alignment=self._strategic_alignment(opportunities),
            portfolio_story=self._story(opportunities, total_revenue, district_exposure),
        )

    def _resolve_opportunities(self, opportunity_ids: list[str]) -> list[Opportunity]:
        opportunities: list[Opportunity] = []
        missing: list[str] = []
        for opportunity_id in opportunity_ids:
            opportunity = self.opportunity_service.fetch_opportunity(opportunity_id)
            if opportunity is None:
                missing.append(opportunity_id)
            else:
                opportunities.append(opportunity)
        if missing:
            raise ValueError(f"Selected opportunities were not found: {', '.join(missing)}")
        return opportunities

    @staticmethod
    def _exposure(
        opportunities: list[Opportunity],
        category: Callable[[Opportunity], str],
        total_revenue: float,
    ) -> list[PortfolioExposure]:
        aggregates: dict[str, list[float]] = defaultdict(lambda: [0, 0.0])
        for opportunity in opportunities:
            values = aggregates[category(opportunity)]
            values[0] += 1
            values[1] += opportunity.programmed_value or 0
        return [
            PortfolioExposure(
                name=name,
                project_count=int(values[0]),
                programmed_value=values[1],
                share_of_known_revenue=values[1] / total_revenue if total_revenue else 0,
            )
            for name, values in sorted(aggregates.items())
        ]

    @staticmethod
    def _market(scope: str) -> str:
        normalized = scope.casefold()
        if "bridge" in normalized:
            return "Bridge"
        if "roadway" in normalized or "pavement" in normalized:
            return "Roadway"
        if "drainage" in normalized:
            return "Drainage"
        if "electrical" in normalized or "its" in normalized:
            return "Electrical"
        if "safety" in normalized or "traffic" in normalized or "striping" in normalized:
            return "Safety"
        if "complete streets" in normalized or "ada" in normalized:
            return "Civil"
        return "Other"

    @staticmethod
    def _risk_distribution(opportunities: list[Opportunity]) -> list[RiskDistribution]:
        mapping = {"high": "Low", "moderate": "Moderate", "limited": "High"}
        counts: dict[str, int] = defaultdict(int)
        for opportunity in opportunities:
            counts[mapping[opportunity.source_confidence]] += 1
        return [
            RiskDistribution(
                risk=risk,
                project_count=counts[risk],
                basis="Risk is the inverse of governed source-confidence completeness.",
            )
            for risk in ("Low", "Moderate", "High")
            if counts[risk]
        ]

    @staticmethod
    def _largest_share(exposure: list[PortfolioExposure], project_count: int) -> float | None:
        if not project_count:
            return None
        return max((item.project_count for item in exposure), default=0) / project_count

    @staticmethod
    def _strategic_alignment(opportunities: list[Opportunity]) -> StrategicAlignment:
        counts = {"core": 0, "selective": 0, "partner": 0, "unknown": 0}
        for opportunity in opportunities:
            scope = opportunity.primary_scope.casefold()
            if any(value in scope for value in _CORE_SCOPES):
                counts["core"] += 1
            elif any(value in scope for value in _SELECTIVE_SCOPES):
                counts["selective"] += 1
            elif any(value in scope for value in _PARTNER_SCOPES):
                counts["partner"] += 1
            else:
                counts["unknown"] += 1
        return StrategicAlignment(
            aligned_project_count=counts["core"],
            selective_project_count=counts["selective"],
            partner_or_non_target_project_count=counts["partner"],
            unknown_project_count=counts["unknown"],
            basis="Alignment follows the governed scope-to-pursuit-category rules.",
        )

    @staticmethod
    def _story(
        opportunities: list[Opportunity],
        total_revenue: float,
        district_exposure: list[PortfolioExposure],
    ) -> str:
        if not opportunities:
            return "No opportunities are selected; the portfolio has no revenue or exposure."
        district_count = len(district_exposure)
        missing = sum(item.programmed_value is None for item in opportunities)
        story = (
            f"The portfolio contains {len(opportunities)} projects across {district_count} "
            f"district categories and ${total_revenue:,.0f} in known programmed value."
        )
        if missing:
            story += f" {missing} selected project(s) have no programmed value."
        return story
