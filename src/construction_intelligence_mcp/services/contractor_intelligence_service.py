from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from construction_intelligence_mcp.adapters.contractor_history import ContractorHistoryRepository
from construction_intelligence_mcp.models.contractor import (
    ContractorCandidate,
    ContractorConfidence,
    ContractorContext,
    ContractorEvidence,
)
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.services.project_service import ProjectService


class ContractorIntelligenceService:
    """Produce deterministic contractor context using historical evidence only."""

    def __init__(
        self,
        project_service: ProjectService,
        history_repository: ContractorHistoryRepository,
    ) -> None:
        self.project_service = project_service
        self.history_repository = history_repository

    def fetch_contractor_context(self, project_id: str) -> ContractorContext | None:
        project = self.project_service.fetch_project(project_id)
        if project is None:
            return None
        rows = self._comparable_rows(project, self.history_repository.fetch_history())
        if not rows:
            return ContractorContext(project_id=project_id, confidence=ContractorConfidence.NONE)
        evidence = [self._evidence(index, row) for index, row in enumerate(rows, 1)]
        candidates = self._candidates(project, rows, evidence)
        winners = [candidate for candidate in candidates if candidate.comparable_win_count]
        return ContractorContext(
            project_id=project_id,
            likely_pursuers=candidates,
            historical_winners=winners,
            district_presence={c.contractor_name: c.district_project_count for c in candidates},
            market_share={
                c.contractor_name: c.market_share for c in candidates if c.market_share is not None
            },
            relevant_experience={c.contractor_name: c.relevant_experience for c in candidates},
            self_perform_indicators={
                c.contractor_name: c.self_perform_indicators for c in candidates
            },
            prime_sub_tendencies={c.contractor_name: c.prime_sub_tendency for c in candidates},
            historical_competitiveness={
                c.contractor_name: c.historical_competitiveness for c in candidates
            },
            confidence=self._context_confidence(candidates),
            evidence=evidence,
        )

    fetch_contractor_intelligence = fetch_contractor_context

    @staticmethod
    def _comparable_rows(
        project: ProjectDetail, rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        scope = project.primary_scope.casefold()
        comparable = [
            row
            for row in rows
            if str(row.get("contractor_name") or "").strip()
            and str(row.get("project_type") or "").strip().casefold() == scope
        ]
        return sorted(
            comparable,
            key=lambda row: (
                0 if row.get("district") == project.district else 1,
                str(row.get("contractor_name") or "").casefold(),
                str(row.get("project_id") or ""),
            ),
        )

    def _candidates(
        self,
        project: ProjectDetail,
        rows: list[dict[str, Any]],
        evidence: list[ContractorEvidence],
    ) -> list[ContractorCandidate]:
        grouped: dict[str, list[tuple[dict[str, Any], ContractorEvidence]]] = defaultdict(list)
        for row, item in zip(rows, evidence, strict=True):
            identity = str(row.get("contractor_id") or row["contractor_name"]).strip().casefold()
            grouped[identity].append((row, item))
        total_wins = sum(bool(row.get("was_awarded")) for row in rows)
        candidates = [self._candidate(project, records, total_wins) for records in grouped.values()]
        return sorted(
            candidates,
            key=lambda item: (
                -item.district_project_count,
                -item.project_type_project_count,
                -item.comparable_win_count,
                -item.comparable_bid_count,
                item.contractor_name.casefold(),
            ),
        )

    @staticmethod
    def _candidate(
        project: ProjectDetail,
        records: list[tuple[dict[str, Any], ContractorEvidence]],
        total_wins: int,
    ) -> ContractorCandidate:
        rows = [record[0] for record in records]
        items = [record[1] for record in records]
        roles = sorted({str(row["role"]).strip().upper() for row in rows})
        projects = {str(row["project_id"]) for row in rows}
        district_projects = {
            str(row["project_id"]) for row in rows if row.get("district") == project.district
        }
        wins = sum(bool(row.get("was_awarded")) for row in rows)
        bids = sum(role == "PRIME" for role in (str(row["role"]).strip().upper() for row in rows))
        tendency = "PRIME" if roles == ["PRIME"] else "SUB" if roles == ["SUB"] else "PRIME_AND_SUB"
        ranked = [row["bid_rank"] for row in rows if row.get("bid_rank") is not None]
        competitiveness = (
            "HISTORICAL_WINNER"
            if wins
            else "COMPETITIVE_BIDDER"
            if any(rank <= 3 for rank in ranked)
            else "PARTICIPANT"
        )
        indicators = (
            ["Explicit historical self-perform record"]
            if any(row.get("self_performed") is True for row in rows)
            else []
        )
        confidence = (
            ContractorConfidence.HIGH
            if district_projects and wins
            else ContractorConfidence.MODERATE
            if district_projects
            else ContractorConfidence.LIMITED
        )
        dates = [row["activity_date"] for row in rows if isinstance(row.get("activity_date"), date)]
        name = str(rows[0]["contractor_name"]).strip()
        return ContractorCandidate(
            contractor_id=str(rows[0]["contractor_id"]) if rows[0].get("contractor_id") else None,
            contractor_name=name,
            roles=roles,
            comparable_project_count=len(projects),
            comparable_bid_count=bids,
            comparable_win_count=wins,
            district_project_count=len(district_projects),
            project_type_project_count=len(projects),
            market_share=wins / total_wins if total_wins else None,
            relevant_experience=sorted(
                f"{row['project_id']}: {row['project_type']}" for row in rows
            ),
            self_perform_indicators=indicators,
            prime_sub_tendency=tendency,
            historical_competitiveness=competitiveness,
            most_recent_activity_date=max(dates) if dates else None,
            confidence=confidence,
            evidence_ids=[item.evidence_id for item in items],
        )

    def _evidence(self, index: int, row: dict[str, Any]) -> ContractorEvidence:
        return ContractorEvidence(
            evidence_id=f"contractor-evidence:{index}",
            contractor_id=row.get("contractor_id"),
            contractor_name=str(row["contractor_name"]).strip(),
            historical_project_id=str(row["project_id"]),
            contract_number=row.get("contract_number"),
            source_relation=self.history_repository.source_relation or "unavailable",
            district=row.get("district"),
            project_type=row.get("project_type"),
            role=str(row["role"]).strip().upper(),
            bid_rank=row.get("bid_rank"),
            was_awarded=bool(row.get("was_awarded")),
            activity_date=row.get("activity_date"),
            self_performed=row.get("self_performed"),
        )

    @staticmethod
    def _context_confidence(candidates: list[ContractorCandidate]) -> ContractorConfidence:
        return max(
            (candidate.confidence for candidate in candidates),
            key=lambda value: {
                ContractorConfidence.NONE: 0,
                ContractorConfidence.LIMITED: 1,
                ContractorConfidence.MODERATE: 2,
                ContractorConfidence.HIGH: 3,
            }[value],
        )
