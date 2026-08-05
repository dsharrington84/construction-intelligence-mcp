from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from fastmcp import FastMCP

from construction_intelligence_mcp.adapters.executive_knowledge_adapter import (
    ExecutiveKnowledgeAdapter,
)
from construction_intelligence_mcp.models.opportunity import OpportunitySearchRequest
from construction_intelligence_mcp.models.project import ProjectSearchRequest
from construction_intelligence_mcp.services.market_service import MarketService
from construction_intelligence_mcp.services.opportunity_service import OpportunityService
from construction_intelligence_mcp.services.project_intelligence_service import (
    ProjectIntelligenceService,
)
from construction_intelligence_mcp.services.project_service import ProjectService
from construction_intelligence_mcp.services.strategic_context_service import StrategicContextService

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
    strategic_context_service = StrategicContextService(
        project_service, ExecutiveKnowledgeAdapter(project_service.adapter)
    )
    return ProjectIntelligenceService(
        project_service,
        MarketService(project_service),
        OpportunityService(project_service),
        strategic_context_service,
    )


def _strategic_context_service() -> StrategicContextService:
    project_service = _service()
    return StrategicContextService(
        project_service, ExecutiveKnowledgeAdapter(project_service.adapter)
    )


def smoke_test() -> None:
    """Print source resolution and a small Southern California project sample."""
    service = _service()
    districts = [7, 8, 11, 12]
    samples = service.search_projects(ProjectSearchRequest(districts=districts, limit=5))
    fields = service.resolved_fields
    executive_adapter = ExecutiveKnowledgeAdapter(service.adapter)
    strategic_service = StrategicContextService(service, executive_adapter)
    print(f"Resolved source table: {service.source_table}")
    print(f"Resolved project identifier field: {fields['project_id']}")
    print(f"Resolved description field: {fields['description']}")
    print(f"Resolved refined executive relation: {executive_adapter.source_relation}")
    print(f"Resolved base executive section relation: {executive_adapter.base_section_relation}")
    print(
        "Resolved source document/source asset relation: "
        f"{executive_adapter.source_document_relation or '(inline base section identity)'}"
    )
    print(f"Executive join keys: {json.dumps(executive_adapter.join_keys)}")
    print(
        "Resolved executive lineage fields: "
        + json.dumps(executive_adapter.lineage_fields, sort_keys=True)
    )
    status_counts = executive_adapter.eligible_record_counts_by_status()
    diagnostics = executive_adapter.diagnostics
    metrics = diagnostics["selected_path_metrics"]
    print(f"Eligible executive records by refined status: {json.dumps(status_counts)}")
    print(f"Refined status distribution: {json.dumps(metrics['refined_status_distribution'])}")
    print(f"Eligible refined rows: {metrics['eligible_refined_rows']}")
    print(f"Matched refined rows: {metrics['matched_refined_rows']}")
    print(f"Unmatched refined rows: {metrics['unmatched_refined_rows']}")
    print(f"Eligible lineage match percentage: {metrics['match_percentage']:.2f}%")
    print(f"Non-null governed-content rows: {metrics['non_null_governed_content_rows']}")
    print(f"Non-null source-document rows: {metrics['non_null_source_document_rows']}")
    print(f"Final executive record count: {metrics['rows_converted_to_records']}")
    print(f"Duplicate multiplication count: {metrics['duplicate_multiplication_count']}")
    rejected = [
        path for path in diagnostics["candidate_paths"] if path["rejection_reason"] is not None
    ]
    print(f"Rejected executive path summaries: {json.dumps(rejected, default=str)}")
    print(f"Total Southern California projects: {service.count_projects(districts)}")
    print("Five sample projects:")
    for project in samples:
        print(json.dumps(project.model_dump(mode="json"), sort_keys=True))
        context = strategic_service.fetch_strategic_context(project.project_id)
        strength_counts = {"DIRECT": 0, "SUPPORTING": 0, "CONTEXTUAL": 0}
        if context:
            for evidence in context.evidence:
                strength_counts[evidence.evidence_strength.value] += 1
        print(
            f"Strategic evidence for {project.project_id}: "
            f"{json.dumps(strength_counts, sort_keys=True)}"
        )


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
def fetch_strategic_context(project_id: str) -> dict | None:
    """Fetch source-backed strategic context for one governed project."""
    context = _strategic_context_service().fetch_strategic_context(project_id)
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
