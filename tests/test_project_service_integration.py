import os
from pathlib import Path

import pytest

from construction_intelligence_mcp.models.project import ProjectDetail, ProjectSearchRequest
from construction_intelligence_mcp.services.project_service import ProjectService

DATABASE = Path(os.environ["CI_DATABASE"]).expanduser() if os.environ.get("CI_DATABASE") else None

pytestmark = pytest.mark.skipif(
    DATABASE is None or not DATABASE.is_file(),
    reason="CI_DATABASE is not set to an available source DuckDB",
)


def test_actual_schema_search_filters_and_fetch_round_trip() -> None:
    assert DATABASE is not None
    service = ProjectService(DATABASE)
    projects = service.search_projects(ProjectSearchRequest(districts=[7, 8, 11, 12], limit=5))

    assert service.source_table.endswith('"ci_market_state"')
    assert service.resolved_fields["project_id"]
    assert service.resolved_fields["description"]
    assert all(project.district in {7, 8, 11, 12} for project in projects)
    assert all(project.project_id and project.title for project in projects)
    if projects:
        fetched = service.fetch_project(projects[0].project_id)
        assert isinstance(fetched, ProjectDetail)
        assert fetched.raw_record


def test_actual_schema_supports_every_search_filter() -> None:
    assert DATABASE is not None
    service = ProjectService(DATABASE)
    seed = service.search_projects(ProjectSearchRequest(limit=1))[0]
    request = ProjectSearchRequest(
        districts=[seed.district] if seed.district else None,
        advertisement_start=seed.advertisement_date,
        advertisement_end=seed.advertisement_date,
        minimum_programmed_value=seed.programmed_value,
        text=seed.description.split()[0] if seed.description else seed.title.split()[0],
        limit=1,
    )

    results = service.search_projects(request)

    assert results
