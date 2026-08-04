from pathlib import Path

import pytest

from construction_intelligence_mcp.models.project import ProjectSearchRequest
from construction_intelligence_mcp.services.project_service import ProjectService

DATABASE = Path(
    "/mnt/c/Users/dshar/Desktop/Caltrans_Pricing_Data/database/caltrans_pricing.duckdb"
)

pytestmark = pytest.mark.skipif(not DATABASE.is_file(), reason="Local DuckDB is unavailable")


def test_search_projects_returns_business_models() -> None:
    service = ProjectService(DATABASE)
    projects = service.search_projects(ProjectSearchRequest(limit=5))

    assert len(projects) == 5
    assert all(project.project_id for project in projects)
    assert all(project.title for project in projects)
    assert all(project.primary_scope for project in projects)


def test_search_projects_filters_southern_california() -> None:
    service = ProjectService(DATABASE)
    projects = service.search_projects(
        ProjectSearchRequest(districts=[7, 8, 11, 12], limit=25)
    )

    assert projects
    assert all(project.district in {7, 8, 11, 12} for project in projects)


def test_fetch_project_round_trip() -> None:
    service = ProjectService(DATABASE)
    project = service.search_projects(ProjectSearchRequest(limit=1))[0]
    fetched = service.fetch_project(project.project_id)

    assert fetched is not None
    assert fetched.project_id == project.project_id
    assert fetched.raw_record
