import os
from pathlib import Path

import pytest

from construction_intelligence_mcp.adapters.executive_knowledge_adapter import (
    ExecutiveKnowledgeAdapter,
)
from construction_intelligence_mcp.models.project import ProjectSearchRequest
from construction_intelligence_mcp.services.project_service import ProjectService
from construction_intelligence_mcp.services.strategic_context_service import StrategicContextService


@pytest.fixture
def configured_database() -> Path:
    configured = os.environ.get("CI_DATABASE")
    if not configured:
        pytest.skip("CI_DATABASE is not configured")
    database = Path(configured).expanduser()
    if not database.is_file():
        pytest.skip(f"CI_DATABASE is unavailable: {database}")
    return database


def test_actual_executive_source_and_southern_california_context(
    configured_database: Path,
) -> None:
    project_service = ProjectService(configured_database)
    executive_adapter = ExecutiveKnowledgeAdapter(project_service.adapter)

    assert executive_adapter.source_relation is not None
    assert executive_adapter.source_relation in executive_adapter.inspected_relations
    assert all(
        executive_adapter.resolved_fields[concept] is not None
        for concept in (
            "evidence_id",
            "source_document",
            "source_section_id",
            "governed_finding",
            "refined_status",
        )
    )
    records = executive_adapter.fetch_records()
    assert records
    assert executive_adapter.diagnostics["selected_path_metrics"]["match_percentage"] > 0
    assert all(
        record.refined_status in ExecutiveKnowledgeAdapter.ELIGIBLE_STATUSES for record in records
    )
    assert not any(
        record.refined_status in ExecutiveKnowledgeAdapter.EXCLUDED_STATUSES for record in records
    )
    assert executive_adapter.lineage_fields
    assert executive_adapter.unmatched_refined_section_count >= 0
    assert executive_adapter.duplicate_evidence_id_count >= 0

    projects = project_service.search_projects(
        ProjectSearchRequest(districts=[7, 8, 11, 12], limit=5)
    )
    assert projects
    context = StrategicContextService(project_service, executive_adapter).fetch_strategic_context(
        projects[0].project_id
    )

    assert context is not None
    assert context.evidence or context.source_confidence == "NONE"
