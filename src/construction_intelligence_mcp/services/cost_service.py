from __future__ import annotations

from collections import defaultdict
from datetime import date
from statistics import mean, median
from typing import Any, Protocol

from construction_intelligence_mcp.adapters.cost_history_adapter import CostHistoryAdapter
from construction_intelligence_mcp.models.cost import (
    BidItemDistribution,
    ComparableProject,
    CostConfidence,
    CostContext,
    CostEvidence,
    CostStatistics,
    CostVariance,
    EscalationBasis,
    HistoricalCost,
    HistoricalUnitPrice,
)
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.services.project_service import ProjectService


class CostHistorySource(Protocol):
    source_relation: str | None

    def fetch_observations(self) -> list[dict[str, Any]]: ...


class CostService:
    """Build a deterministic market baseline exclusively from historical evidence."""

    def __init__(
        self,
        project_service: ProjectService,
        cost_history: CostHistorySource | None = None,
    ) -> None:
        self.project_service = project_service
        self.cost_history = cost_history or CostHistoryAdapter(project_service.adapter.database)

    def fetch_cost_context(self, project_id: str) -> CostContext | None:
        project = self.project_service.fetch_project(project_id)
        if project is None:
            return None
        source = self.cost_history.source_relation
        if source is None:
            return self._empty(project, "No governed cost-history relation is available.")

        rows = self._deduplicate(self.cost_history.fetch_observations())
        matches = [row for row in rows if self._scope(row) == project.primary_scope]
        matches = [row for row in matches if self._text(row.get("project_id")) != project_id]
        if not matches:
            return self._empty(project, "No historical projects match the governed primary scope.")

        comparables = self._comparables(project, matches, source)
        if not comparables:
            return self._empty(project, "Matching history has no usable project cost values.")
        unit_prices = self._unit_prices(matches)
        distribution = self._distribution(matches)
        values = [item.escalated_cost for item in comparables]
        statistics = self._statistics(values)
        historical_cost = HistoricalCost(statistics=statistics, baseline_cost=statistics.median)
        return CostContext(
            project_id=project_id,
            historical_cost=historical_cost,
            historical_unit_prices=unit_prices,
            bid_item_distribution=distribution,
            cost_confidence=self._confidence(comparables, unit_prices),
            escalation_basis=self._escalation_basis(matches, project),
            comparable_projects=comparables,
            variance=self._variance(project.programmed_value, statistics.median),
            evidence=self._evidence(matches, source),
            limitations=self._limitations(comparables, unit_prices),
        )

    @staticmethod
    def _empty(project: ProjectDetail, limitation: str) -> CostContext:
        return CostContext(
            project_id=project.project_id,
            escalation_basis=EscalationBasis(
                applied=False, method="No escalation: insufficient historical evidence"
            ),
            limitations=[limitation],
        )

    def _comparables(
        self, project: ProjectDetail, rows: list[dict[str, Any]], source: str
    ) -> list[ComparableProject]:
        by_project: dict[str, dict[str, Any]] = {}
        for row in rows:
            identifier = self._text(row.get("project_id"))
            cost = self._number(row.get("historical_cost"))
            if identifier and cost is not None and identifier not in by_project:
                by_project[identifier] = row
        result = []
        for identifier, row in by_project.items():
            factor = self._number(row.get("escalation_factor")) or 1.0
            district = self._integer(row.get("district"))
            result.append(
                ComparableProject(
                    project_id=identifier,
                    contract_number=self._text(row.get("contract_number")),
                    description=self._text(row.get("description")),
                    primary_scope=self._scope(row),
                    district=district,
                    bid_date=self._date(row.get("bid_date")),
                    historical_cost=float(row["historical_cost"]),
                    escalated_cost=float(row["historical_cost"]) * factor,
                    escalation_factor=factor,
                    match_basis=(
                        "Same primary scope and district"
                        if district is not None and district == project.district
                        else "Same primary scope statewide"
                    ),
                    source_relation=source,
                )
            )
        return sorted(
            result,
            key=lambda item: (
                item.district != project.district,
                -(item.bid_date.toordinal() if item.bid_date else 0),
                item.project_id,
            ),
        )

    def _unit_prices(self, rows: list[dict[str, Any]]) -> list[HistoricalUnitPrice]:
        groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            code, unit = self._text(row.get("bid_item_code")), self._text(row.get("unit"))
            price = self._number(row.get("unit_price"))
            if code and unit and price is not None:
                groups[(code, unit)].append(row)
        return [
            HistoricalUnitPrice(
                bid_item_code=code,
                description=self._text(group[0].get("bid_item_description")),
                unit=unit,
                statistics=self._statistics([float(row["unit_price"]) for row in group]),
            )
            for (code, unit), group in sorted(groups.items())
        ]

    def _distribution(self, rows: list[dict[str, Any]]) -> list[BidItemDistribution]:
        valid = [row for row in rows if self._text(row.get("bid_item_code"))]
        groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in valid:
            groups[
                (self._text(row["bid_item_code"]) or "", self._text(row.get("unit")) or "UNKNOWN")
            ].append(row)
        return [
            BidItemDistribution(
                bid_item_code=code,
                description=self._text(group[0].get("bid_item_description")),
                unit=unit,
                observation_count=len(group),
                total_quantity=(
                    sum(quantities)
                    if (
                        quantities := [
                            self._number(row.get("quantity"))
                            for row in group
                            if self._number(row.get("quantity")) is not None
                        ]
                    )
                    else None
                ),
                share_of_observations=len(group) / len(valid),
            )
            for (code, unit), group in sorted(groups.items())
        ]

    @staticmethod
    def _statistics(values: list[float]) -> CostStatistics:
        return CostStatistics(
            observation_count=len(values),
            minimum=min(values),
            median=median(values),
            mean=mean(values),
            maximum=max(values),
        )

    def _escalation_basis(
        self, rows: list[dict[str, Any]], project: ProjectDetail
    ) -> EscalationBasis:
        factors = [self._number(row.get("escalation_factor")) for row in rows]
        factors = [factor for factor in factors if factor is not None]
        sources = sorted(
            {source for row in rows if (source := self._text(row.get("escalation_source")))}
        )
        dates = [value for row in rows if (value := self._date(row.get("bid_date")))]
        return EscalationBasis(
            applied=any(factor != 1 for factor in factors),
            method=(
                "Source-provided historical cost-index factors"
                if factors
                else "Nominal historical dollars; no governed escalation factor available"
            ),
            factor=median(factors) if factors else None,
            source_date=max(dates) if dates else None,
            target_date=project.advertisement_date,
            source=", ".join(sources) or None,
        )

    @staticmethod
    def _confidence(
        comparables: list[ComparableProject], prices: list[HistoricalUnitPrice]
    ) -> CostConfidence:
        if len(comparables) >= 5 and sum(item.statistics.observation_count for item in prices) >= 5:
            return CostConfidence.HIGH
        if len(comparables) >= 3:
            return CostConfidence.MODERATE
        return CostConfidence.LOW

    @staticmethod
    def _variance(reference: float | None, baseline: float) -> CostVariance | None:
        if reference is None:
            return None
        amount = reference - baseline
        return CostVariance(
            reference_value=reference,
            baseline_cost=baseline,
            amount=amount,
            percent=(amount / baseline * 100 if baseline else None),
            interpretation="Programmed value minus the historical market baseline",
        )

    @staticmethod
    def _limitations(
        comparables: list[ComparableProject], prices: list[HistoricalUnitPrice]
    ) -> list[str]:
        limitations = []
        if len(comparables) < 3:
            limitations.append("Limited comparable project history (fewer than three projects).")
        if not prices:
            limitations.append("No governed historical unit-price observations are available.")
        return limitations

    def _evidence(self, rows: list[dict[str, Any]], source: str) -> list[CostEvidence]:
        return [
            CostEvidence(
                source_relation=source,
                project_id=self._text(row.get("project_id")) or "",
                contract_number=self._text(row.get("contract_number")),
                bid_date=self._date(row.get("bid_date")),
                bid_item_code=self._text(row.get("bid_item_code")),
                quantity=self._number(row.get("quantity")),
                unit=self._text(row.get("unit")),
                unit_price=self._number(row.get("unit_price")),
                historical_cost=self._number(row.get("historical_cost")),
            )
            for row in rows
        ]

    @staticmethod
    def _deduplicate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: dict[tuple[str, ...], dict[str, Any]] = {}
        keys = (
            "project_id",
            "contract_number",
            "bid_item_code",
            "unit",
            "quantity",
            "unit_price",
            "historical_cost",
        )
        for row in rows:
            unique.setdefault(tuple(str(row.get(key)) for key in keys), row)
        return list(unique.values())

    @staticmethod
    def _scope(row: dict[str, Any]) -> str:
        return str(row.get("primary_scope") or "").strip()

    @staticmethod
    def _text(value: Any) -> str | None:
        text = "" if value is None else str(value).strip()
        return text or None

    @staticmethod
    def _number(value: Any) -> float | None:
        try:
            number = float(value)
            return number if number >= 0 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _integer(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _date(value: Any) -> date | None:
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value)[:10]) if value is not None else None
        except ValueError:
            return None
