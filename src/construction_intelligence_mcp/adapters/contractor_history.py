from __future__ import annotations

from pathlib import Path
from typing import Any

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter

HISTORY_RELATIONS = ("ci_contractor_history", "contractor_history")

_FIELDS: dict[str, tuple[str, ...]] = {
    "contractor_id": ("contractor_id", "bidder_id", "license_number"),
    "contractor_name": ("contractor_name", "bidder_name", "business_name"),
    "project_id": ("project_id", "historical_project_id", "contract_number"),
    "contract_number": ("contract_number", "contract_no"),
    "district": ("district", "caltrans_district"),
    "project_type": ("project_type", "primary_scope", "scope"),
    "role": ("role", "contractor_role", "participant_role"),
    "bid_rank": ("bid_rank", "rank"),
    "was_awarded": ("was_awarded", "is_winner", "awarded"),
    "activity_date": ("activity_date", "bid_date", "award_date"),
    "self_performed": ("self_performed", "is_self_performed"),
}


class ContractorHistoryRepository:
    """Schema-adaptive, read-only access to governed contractor history."""

    def __init__(self, database: str | Path) -> None:
        self.adapter = DuckDBAdapter(database)
        self.source_relation = next(
            (
                relation
                for name in HISTORY_RELATIONS
                if (relation := self.adapter.resolve_table(name))
            ),
            None,
        )
        self.resolved_fields: dict[str, str | None] = {}
        if self.source_relation is not None:
            columns = set(self.adapter.columns(self.source_relation))
            self.resolved_fields = {
                concept: next((name for name in candidates if name in columns), None)
                for concept, candidates in _FIELDS.items()
            }
            required = ("contractor_name", "project_id", "district", "project_type", "role")
            missing = [concept for concept in required if self.resolved_fields[concept] is None]
            if missing:
                raise RuntimeError(
                    "Contractor history has unresolved required fields: " + ", ".join(missing)
                )

    def fetch_history(self) -> list[dict[str, Any]]:
        if self.source_relation is None:
            return []
        projection = []
        for concept in _FIELDS:
            field = self.resolved_fields[concept]
            if field is None:
                projection.append(f"NULL AS {concept}")
            elif concept == "district":
                projection.append(f'TRY_CAST("{field}" AS INTEGER) AS district')
            elif concept == "bid_rank":
                projection.append(f'TRY_CAST("{field}" AS INTEGER) AS bid_rank')
            elif concept in {"was_awarded", "self_performed"}:
                projection.append(f'TRY_CAST("{field}" AS BOOLEAN) AS {concept}')
            elif concept == "activity_date":
                projection.append(f'TRY_CAST("{field}" AS DATE) AS activity_date')
            else:
                projection.append(f'CAST("{field}" AS VARCHAR) AS {concept}')
        return self.adapter.fetch_all(f"SELECT {', '.join(projection)} FROM {self.source_relation}")
