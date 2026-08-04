from datetime import date
from pathlib import Path

import duckdb
import pytest
from pydantic import ValidationError

from construction_intelligence_mcp.models.project import (
    ProjectDetail,
    ProjectSearchRequest,
    ProjectSummary,
)
from construction_intelligence_mcp.models.scope import (
    MarketSector,
    ScopeClassification,
    ScopeConfidence,
)
from construction_intelligence_mcp.services.project_service import ProjectService


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "projects.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute(
        """
        CREATE TABLE ci_market_state (
            market_state_id VARCHAR,
            project_description VARCHAR,
            district VARCHAR,
            county VARCHAR,
            route VARCHAR,
            location VARCHAR,
            project_type VARCHAR,
            programmed_amount DOUBLE,
            advertisement_date DATE,
            advertisement_fiscal_year VARCHAR,
            extra_source_field VARCHAR
        )
        """
    )
    connection.executemany(
        "INSERT INTO ci_market_state VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                "P-1",
                "Replace bridge at Pine Creek",
                "07",
                "Los Angeles",
                "5",
                "Pine Creek",
                "Bridge",
                50_000_000,
                date(2026, 1, 1),
                "FY 2026",
                "complete detail",
            ),
            (
                "P-2",
                "Cold plane and overlay pavement",
                "District 8",
                "San Bernardino",
                "10",
                "Main Street",
                "Roadway",
                10_000_000,
                date(2026, 6, 30),
                "2026/27",
                "second detail",
            ),
            (
                "P-3",
                "Install drainage culvert",
                "11",
                "San Diego",
                "805",
                "Mission Valley",
                "Drainage",
                5_000_000,
                date(2027, 1, 1),
                "2027",
                "third detail",
            ),
            (
                "P-4",
                "Northern signal work",
                "4",
                "Alameda",
                "80",
                "Oakland",
                "Electrical",
                1_000_000,
                date(2026, 3, 1),
                "2026",
                "fourth detail",
            ),
        ],
    )
    connection.close()
    return path


def test_search_projects_returns_business_models(database: Path) -> None:
    projects = ProjectService(database).search_projects(ProjectSearchRequest(limit=2))

    assert len(projects) == 2
    assert all(isinstance(project, ProjectSummary) for project in projects)
    assert not any(hasattr(project, "columns") for project in projects)


def test_search_projects_supports_all_filters(database: Path) -> None:
    projects = ProjectService(database).search_projects(
        ProjectSearchRequest(
            districts=[8, 7, 7],
            advertisement_start=date(2026, 1, 1),
            advertisement_end=date(2026, 6, 30),
            minimum_programmed_value=10_000_000,
            text="pavement",
            limit=5,
        )
    )

    assert [project.project_id for project in projects] == ["P-2"]


@pytest.mark.parametrize("limit", [0, 1001])
def test_search_projects_validates_limit(limit: int) -> None:
    with pytest.raises(ValidationError):
        ProjectSearchRequest(limit=limit)


def test_fetch_project_returns_complete_business_object_or_none(database: Path) -> None:
    service = ProjectService(database)

    project = service.fetch_project("P-1")

    assert isinstance(project, ProjectDetail)
    assert project.project_id == "P-1"
    assert project.project_type == "Bridge"
    assert project.primary_scope == "Bridge Replacement"
    assert project.classified_scope is not None
    assert project.classified_scope.primary_scope == ScopeClassification.BRIDGE_REPLACEMENT
    assert project.classified_scope.market_sector == MarketSector.BRIDGE
    assert project.classified_scope.confidence == ScopeConfidence.HIGH
    assert "replace bridge" in project.classified_scope.matched_keywords
    assert project.raw_record["extra_source_field"] == "complete detail"
    assert service.fetch_project("not-found") is None


def test_count_projects_by_district(database: Path) -> None:
    assert ProjectService(database).count_projects([7, 8, 11, 12]) == 3


def test_missing_database_error_is_actionable(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Set CI_DATABASE"):
        ProjectService(tmp_path / "missing.duckdb")


def test_missing_canonical_table_error_is_actionable(tmp_path: Path) -> None:
    path = tmp_path / "empty.duckdb"
    duckdb.connect(str(path)).close()

    with pytest.raises(RuntimeError, match="Missing canonical table 'ci_market_state'"):
        ProjectService(path)


def test_unresolved_required_project_id_error_lists_columns(tmp_path: Path) -> None:
    path = tmp_path / "invalid.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute("CREATE TABLE ci_market_state (unrelated VARCHAR)")
    connection.close()

    with pytest.raises(RuntimeError, match="unresolved required fields: project_id"):
        ProjectService(path)


def test_actual_market_state_shape_preserves_missing_description(tmp_path: Path) -> None:
    path = tmp_path / "actual-shape.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute(
        """
        CREATE TABLE ci_market_state (
            project_id VARCHAR,
            project_name VARCHAR,
            project_type VARCHAR,
            asset_class VARCHAR,
            source_asset_title VARCHAR,
            district INTEGER,
            county VARCHAR,
            route VARCHAR,
            programmed_amount DOUBLE,
            advertisement_fiscal_year INTEGER
        )
        """
    )
    connection.execute(
        """
        INSERT INTO ci_market_state VALUES
        ('P-ACTUAL', 'Route 5 asset work', 'Capital Maintenance', 'Bridge',
         'Bridge deck rehabilitation candidates', 7, 'Los Angeles', '5', 12000000, 2028)
        """
    )
    connection.close()

    service = ProjectService(path)
    project = service.fetch_project("P-ACTUAL")

    assert project is not None
    assert service.resolved_fields["description"] is None
    assert service.resolved_fields["title"] == "project_name"
    assert project.title == "Route 5 asset work"
    assert project.description is None
    assert project.asset_class == "Bridge"
    assert project.source_asset_title == "Bridge deck rehabilitation candidates"
    assert project.classified_scope is not None
    assert project.classified_scope.primary_scope == ScopeClassification.BRIDGE_REHABILITATION
