from __future__ import annotations

from pathlib import Path
from typing import Any

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter

_RELATIONS = ("ci_cost_history", "cost_history", "ci_bid_history", "bid_history")
_FIELDS: dict[str, tuple[str, ...]] = {
    "project_id": ("project_id", "historical_project_id", "contract_id"),
    "contract_number": ("contract_number", "contract_no", "contract_id"),
    "description": ("description", "project_description", "project_title"),
    "primary_scope": ("primary_scope", "scope", "work_type", "project_type"),
    "district": ("district",),
    "bid_date": ("bid_date", "award_date", "advertisement_date"),
    "historical_cost": ("historical_cost", "award_amount", "bid_amount", "total_cost"),
    "bid_item_code": ("bid_item_code", "item_code", "item_number"),
    "bid_item_description": ("bid_item_description", "item_description"),
    "quantity": ("quantity", "bid_quantity"),
    "unit": ("unit", "unit_of_measure"),
    "unit_price": ("unit_price", "bid_unit_price"),
    "escalation_factor": ("escalation_factor", "cost_index_factor"),
    "escalation_source": ("escalation_source", "cost_index_source"),
}


class CostHistoryAdapter:
    """Schema-adaptive, read-only access to certified historical cost observations."""

    def __init__(self, database: str | Path) -> None:
        self.adapter = DuckDBAdapter(database)
        self.source_relation = next(
            (relation for name in _RELATIONS if (relation := self.adapter.resolve_table(name))),
            None,
        )
        self.resolved_fields: dict[str, str | None] = {}
        if self.source_relation is not None:
            columns = set(self.adapter.columns(self.source_relation))
            self.resolved_fields = {
                concept: next((name for name in candidates if name in columns), None)
                for concept, candidates in _FIELDS.items()
            }
            required = ("project_id", "primary_scope", "historical_cost")
            missing = [concept for concept in required if self.resolved_fields[concept] is None]
            if missing:
                raise RuntimeError(
                    f"Cost relation '{self.source_relation}' has unresolved required fields: "
                    f"{', '.join(missing)}. Available columns: {', '.join(sorted(columns))}"
                )

    def fetch_observations(self) -> list[dict[str, Any]]:
        if self.source_relation is None:
            return []
        expressions = []
        for concept in _FIELDS:
            field = self.resolved_fields[concept]
            expressions.append(
                f'{self.adapter.quote_identifier(field)} AS "{concept}"'
                if field
                else f'NULL AS "{concept}"'
            )
        return self.adapter.fetch_all(
            f"SELECT {', '.join(expressions)} FROM {self.source_relation}"
        )
