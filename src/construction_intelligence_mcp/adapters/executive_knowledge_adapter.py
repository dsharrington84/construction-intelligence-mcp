from __future__ import annotations

import json
from pathlib import Path

from construction_intelligence_mcp.models.strategic_context import (
    ExecutiveEvidence,
    ExecutiveEvidenceDiagnostics,
)


class ExecutiveContractError(RuntimeError):
    """The checked-in evidence cannot certify an Executive warehouse contract."""


class ExecutiveKnowledgeAdapter:
    """Gate Executive reads on the evidence produced by 010A and 010B.

    The current authoritative snapshots contain no certified relations or joins. This
    adapter intentionally refuses to guess a physical contract. SQL will be added only
    after regenerated artifacts identify certified relations, keys, and producers.
    """

    def __init__(self, repository_root: Path | None = None) -> None:
        self.repository_root = repository_root or Path(__file__).resolve().parents[3]
        self._diagnostics = self._read_certification()

    def _read_certification(self) -> ExecutiveEvidenceDiagnostics:
        warehouse = self.repository_root / "data/output/warehouse"
        pipeline = self.repository_root / "data/output/pipeline"
        relation_inventory = json.loads(
            (warehouse / "executive_relation_inventory.json").read_text()
        )
        join_inventory = json.loads((warehouse / "executive_join_inventory.json").read_text())
        producers = json.loads((pipeline / "executive_table_producers.json").read_text())
        relations = relation_inventory.get("relations", [])
        joins = [join for join in join_inventory.get("joins", []) if join.get("accepted")]
        limitations: list[str] = []
        if relation_inventory.get("metadata", {}).get("evidence_status") != "generated":
            limitations.append("010A relation inventory is not generated from CI_DATABASE.")
        if not relations:
            limitations.append("010A identifies no Executive relations.")
        if not joins:
            limitations.append("010A identifies no accepted Executive lineage joins.")
        if not producers.get("production_relation_writes"):
            limitations.append(
                "010B identifies no Executive warehouse producer in this repository."
            )
        return ExecutiveEvidenceDiagnostics(
            selected_relations=[],
            certification_status="CERTIFIED" if not limitations else "UNAVAILABLE",
            certification_limitations=limitations,
        )

    @property
    def diagnostics(self) -> ExecutiveEvidenceDiagnostics:
        return self._diagnostics

    def list_evidence(self) -> list[ExecutiveEvidence]:
        if self._diagnostics.certification_status != "CERTIFIED":
            detail = " ".join(self._diagnostics.certification_limitations)
            raise ExecutiveContractError(f"Executive Evidence Contract is unavailable: {detail}")
        raise ExecutiveContractError(
            "Artifacts claim certification but no implemented certified relation contract exists."
        )
