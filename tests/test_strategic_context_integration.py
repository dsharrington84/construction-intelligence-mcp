import os
from pathlib import Path

import pytest

from construction_intelligence_mcp.adapters.executive_evidence_adapter import (
    CdpPhysicalImplementationMapping,
)
from construction_intelligence_mcp.models.project import ProjectSearchRequest
from construction_intelligence_mcp.models.strategic_context import SourceConfidence
from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)
from construction_intelligence_mcp.services.project_service import ProjectService
from construction_intelligence_mcp.services.strategic_context_service import StrategicContextService

DATABASE = Path(os.environ["CI_DATABASE"]).expanduser() if os.environ.get("CI_DATABASE") else None
MAPPED_RELATION = os.environ.get("CDP001_EXECUTIVE_EVIDENCE_RELATION")
MAPPING_STATUS = os.environ.get("CDP001_EXECUTIVE_EVIDENCE_STATUS")
MAPPING_ROLE = os.environ.get("CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE", "certified_current")

pytestmark = pytest.mark.skipif(
    DATABASE is None or not DATABASE.is_file(),
    reason="CI_DATABASE is not set to an available source DuckDB",
)


def test_actual_ci_database_strategic_context_uses_certified_evidence_mapping() -> None:
    assert DATABASE is not None
    if not MAPPED_RELATION or (MAPPING_STATUS or "").upper() not in {"ACCEPTED", "CURRENT"}:
        pytest.fail("CI_DATABASE is configured but accepted/current CDP-001 mapping is unavailable")
    mapping = CdpPhysicalImplementationMapping(
        product_identifier="CDP-001",
        relation=MAPPED_RELATION,
        certification_status=MAPPING_STATUS or "",
        relation_role=MAPPING_ROLE,
    )
    assert len(MAPPED_RELATION.split(".")) == 2
    assert mapping.certification_status.upper() in {"ACCEPTED", "CURRENT"}
    assert mapping.relation_role == "certified_current"

    project_service = ProjectService(DATABASE)
    evidence_service = ExecutiveEvidenceService(DATABASE, [mapping])
    evidence_result = evidence_service.fetch_executive_evidence(limit=100)
    assert evidence_result.diagnostics.selected_relation
    assert evidence_result.diagnostics.final_evidence_count > 0

    projects = project_service.search_projects(
        ProjectSearchRequest(districts=[7, 8, 11, 12], limit=25)
    )
    assert projects
    service = StrategicContextService(project_service, evidence_service)

    contexts = [service.fetch_strategic_context(project.project_id) for project in projects]
    assert all(context is not None for context in contexts)
    for strategic_context in [context for context in contexts if context is not None]:
        returned_evidence = {item.evidence_id for item in strategic_context.evidence}
        for group in (
            strategic_context.programs,
            strategic_context.objectives,
            strategic_context.policy_drivers,
            strategic_context.expected_outcomes,
            strategic_context.strategic_themes,
        ):
            for conclusion in group:
                assert set(conclusion.evidence_ids) <= returned_evidence
        for item in strategic_context.evidence:
            assert item.source_lineage.source_relation
            assert item.source_lineage.source_section_id
        assert strategic_context.source_confidence in SourceConfidence
