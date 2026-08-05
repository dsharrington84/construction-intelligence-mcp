from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from fastmcp import FastMCP

from construction_intelligence_mcp.models.opportunity import OpportunitySearchRequest
from construction_intelligence_mcp.models.project import ProjectSearchRequest
from construction_intelligence_mcp.services.opportunity_service import OpportunityService
from construction_intelligence_mcp.services.opportunity_context_service import (
    OpportunityContextService,
)
from construction_intelligence_mcp.services.market_service import MarketService
from construction_intelligence_mcp.services.project_intelligence_service import (
    ProjectIntelligenceService,
)
from construction_intelligence_mcp.services.project_service import ProjectService

DEFAULT_DATABASE = Path(
    "/mnt/c/Users/dshar/Desktop/Caltrans_Pricing_Data/database/caltrans_pricing.duckdb"
)

mcp = FastMCP(
    name="Construction Intelligence",
    instructions=(
        "Search and fetch governed construction project and opportunity intelligence. "
        "Use opportunity tools for explainable potential pursuits and project tools "
        "for canonical project records."
    ),
)


def _service() -> ProjectService:
    configured = os.environ.get("CI_DATABASE")
    database = Path(configured) if configured else DEFAULT_DATABASE
    return ProjectService(database)


def _opportunity_service() -> OpportunityService:
    return OpportunityService(_service())


def _project_intelligence_service() -> ProjectIntelligenceService:
    project_service = _service()
    return ProjectIntelligenceService(
        project_service,
        MarketService(project_service),
        OpportunityService(project_service),
    )


def _opportunity_context_service() -> OpportunityContextService:
    return OpportunityContextService(_project_intelligence_service())


def smoke_test() -> None:
    """Print source resolution and a small Southern California project sample."""
    service = _service()
    districts = [7, 8, 11, 12]
    samples = service.search_projects(ProjectSearchRequest(districts=districts, limit=5))
    fields = service.resolved_fields
    print(f"Resolved source table: {service.source_table}")
    print(f"Resolved project identifier field: {fields['project_id']}")
    print(f"Resolved description field: {fields['description']}")
    print(f"Total Southern California projects: {service.count_projects(districts)}")
    print("Five sample projects:")
    for project in samples:
        print(json.dumps(project.model_dump(mode="json"), sort_keys=True))


@mcp.tool
def search_projects(
    districts: list[int] | None = None,
    advertisement_start: str | None = None,
    advertisement_end: str | None = None,
    minimum_programmed_value: float | None = None,
    text: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Search canonical projects using business filters."""
    request = ProjectSearchRequest(
        districts=districts,
        advertisement_start=advertisement_start,
        advertisement_end=advertisement_end,
        minimum_programmed_value=minimum_programmed_value,
        text=text,
        limit=limit,
    )
    return [project.model_dump(mode="json") for project in _service().search_projects(request)]


@mcp.tool
def fetch_project(project_id: str) -> dict | None:
    """Fetch one canonical project by project identifier."""
    project = _service().fetch_project(project_id)
    return None if project is None else project.model_dump(mode="json")


@mcp.tool
def fetch_project_intelligence(project_id: str) -> dict | None:
    """Fetch all governed intelligence currently known for one project."""
    intelligence = _project_intelligence_service().fetch_project_intelligence(project_id)
    return None if intelligence is None else intelligence.model_dump(mode="json")


@mcp.tool
def fetch_opportunity_context(project_id: str) -> dict | None:
    """Explain, with governed evidence, why a project surfaced."""
    context = _opportunity_context_service().fetch_opportunity_context(project_id)
    return None if context is None else context.model_dump(mode="json")


@mcp.tool
def search_opportunities(
    districts: list[int] | None = None,
    scope: str | None = None,
    advertisement_start: str | None = None,
    advertisement_end: str | None = None,
    minimum_programmed_value: float | None = None,
    text: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Search explainable potential-pursuit opportunities."""
    request_data = {
        "scope": scope,
        "advertisement_start": advertisement_start,
        "advertisement_end": advertisement_end,
        "minimum_programmed_value": minimum_programmed_value,
        "text": text,
        "limit": limit,
    }
    if districts is not None:
        request_data["districts"] = districts
    request = OpportunitySearchRequest.model_validate(request_data)
    opportunities = _opportunity_service().search_opportunities(request)
    return [opportunity.model_dump(mode="json") for opportunity in opportunities]


@mcp.tool
def fetch_opportunity(opportunity_id: str) -> dict | None:
    """Fetch one potential-pursuit opportunity by opportunity identifier."""
    opportunity = _opportunity_service().fetch_opportunity(opportunity_id)
    return None if opportunity is None else opportunity.model_dump(mode="json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Construction Intelligence MCP server")
    parser.add_argument("command", nargs="?", choices=("serve", "smoke-test"), default="serve")
    args = parser.parse_args()
    if args.command == "smoke-test":
        smoke_test()
        return
    host = os.environ.get("CI_MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("CI_MCP_PORT", "8000"))
    transport = os.environ.get("CI_MCP_TRANSPORT", "sse")
    mcp.run(transport=transport, host=host, port=port)


if __name__ == "__main__":
    main()
