from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TextIO

from construction_intelligence_mcp.adapters.executive_evidence_adapter import (
    CdpPhysicalImplementationMapping,
)
from construction_intelligence_mcp.models.project import ProjectSearchRequest
from construction_intelligence_mcp.models.project_intelligence import ProjectIntelligence
from construction_intelligence_mcp.models.strategic_context import StrategicContext
from construction_intelligence_mcp.runtime.validate import run_validation
from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)
from construction_intelligence_mcp.services.market_service import MarketService
from construction_intelligence_mcp.services.opportunity_service import OpportunityService
from construction_intelligence_mcp.services.project_intelligence_service import (
    ProjectIntelligenceService,
)
from construction_intelligence_mcp.services.project_service import ProjectService
from construction_intelligence_mcp.services.strategic_context_service import StrategicContextService

SOUTHERN_CALIFORNIA_DISTRICTS = [7, 8, 11, 12]
PROGRAM = "Program 100 — Executive Intelligence"
CERTIFIED_DATA_PRODUCT = "CDP-001 — Executive Knowledge Certified Data Product"


def run_certification(
    *,
    environment: dict[str, str] | None = None,
    stdout: TextIO = sys.stdout,
) -> int:
    """Run Program 100 Business Certification after mandatory runtime validation."""

    env = dict(os.environ if environment is None else environment)
    stdout.write("Program 100 Business Certification Report\n")
    stdout.write("=========================================\n\n")
    stdout.write("Runtime validation\n")
    stdout.write("------------------\n")
    validation_exit_code = run_validation(environment=env, stdout=stdout)
    if validation_exit_code != 0:
        stdout.write("\nCERTIFICATION FAILED\n")
        stdout.write("Runtime validation failed; intelligence execution was not attempted.\n")
        return validation_exit_code

    try:
        report = _build_business_report(env)
    except Exception as exc:  # noqa: BLE001 - command must report governed failure to operators.
        stdout.write("\nCERTIFICATION FAILED\n")
        stdout.write(f"{exc}\n")
        return 1

    stdout.write("\n")
    stdout.write(report)
    return 0


def _build_business_report(environment: dict[str, str]) -> str:
    database = Path(_required(environment, "CI_DATABASE")).expanduser()
    mapping = CdpPhysicalImplementationMapping(
        product_identifier="CDP-001",
        relation=_required(environment, "CDP001_EXECUTIVE_EVIDENCE_RELATION"),
        certification_status=_required(environment, "CDP001_EXECUTIVE_EVIDENCE_STATUS"),
        relation_role=_required(environment, "CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE"),
    )
    project_service = ProjectService(database)
    evidence_service = ExecutiveEvidenceService(database, [mapping])
    strategic_context_service = StrategicContextService(project_service, evidence_service)
    intelligence_service = ProjectIntelligenceService(
        project_service,
        MarketService(project_service),
        OpportunityService(project_service),
        strategic_context_service,
    )

    candidates = project_service.search_projects(
        ProjectSearchRequest(districts=SOUTHERN_CALIFORNIA_DISTRICTS, limit=100)
    )
    if not candidates:
        raise RuntimeError("No Southern California governed projects were found.")

    selected_context: StrategicContext | None = None
    selected_intelligence: ProjectIntelligence | None = None
    for candidate in candidates:
        project = project_service.fetch_project(candidate.project_id)
        if project is None:
            continue
        context = strategic_context_service.fetch_strategic_context(project.project_id)
        intelligence = intelligence_service.fetch_project_intelligence(project.project_id)
        if context is not None and intelligence is not None and context.evidence:
            selected_context = context
            selected_intelligence = intelligence
            break
    if selected_context is None or selected_intelligence is None:
        raise RuntimeError(
            "No Southern California governed project received defensible eligible Executive evidence."
        )

    return _format_report(
        database=database,
        mapping=mapping,
        intelligence=selected_intelligence,
        context=selected_context,
    )


def _format_report(
    *,
    database: Path,
    mapping: CdpPhysicalImplementationMapping,
    intelligence: ProjectIntelligence,
    context: StrategicContext,
) -> str:
    project = intelligence.project
    lines = [
        "Business certification",
        "----------------------",
        "Certification result: PASS",
        f"Program: {PROGRAM}",
        f"Certified Data Product: {CERTIFIED_DATA_PRODUCT}",
        f"Runtime database: {database}",
        f"CDP-001 mapping: {mapping.relation}",
        f"Mapping status: {mapping.certification_status}",
        f"Mapping role: {mapping.relation_role}",
        "",
        "Governed Southern California project",
        "------------------------------------",
        f"Project ID: {project.project_id}",
        f"Title: {project.title}",
        f"District: {_value(project.district)}",
        f"County: {_value(project.county)}",
        f"Route: {_value(project.route)}",
        f"Advertisement date: {_value(project.advertisement_date)}",
        f"Programmed value: {_money(project.programmed_value)}",
        "",
        "Executed service chain",
        "----------------------",
        "1. fetch_project() returned the governed project above.",
        "2. fetch_strategic_context() returned eligible Executive evidence.",
        "3. fetch_project_intelligence() integrated Strategic Context into Project Intelligence.",
        "",
        "Strategic context",
        "-----------------",
        f"Source confidence: {context.source_confidence}",
        f"Evidence count: {len(context.evidence)}",
    ]
    for label, conclusions in (
        ("Programs", context.programs),
        ("Objectives", context.objectives),
        ("Policy drivers", context.policy_drivers),
        ("Expected outcomes", context.expected_outcomes),
        ("Strategic themes", context.strategic_themes),
    ):
        if conclusions:
            lines.append(f"{label}: " + "; ".join(item.value for item in conclusions))
    lines.extend(["", "Evidence", "--------"])
    for item in context.evidence:
        lines.extend(
            [
                f"- Evidence ID: {item.evidence_id}",
                f"  Source document: {item.source_document}",
                f"  Source section: {item.source_section_id}",
                f"  Relationship: {item.relationship_to_project}",
                f"  Strength: {item.evidence_strength}",
                f"  Source relation: {item.source_lineage.source_relation}",
                f"  Source keys: {item.source_lineage.source_keys}",
                f"  Excerpt: {item.source_excerpt}",
            ]
        )
        if item.limitations:
            lines.append(f"  Limitations: {'; '.join(item.limitations)}")
    if context.limitations:
        lines.extend(["", "Limitations", "-----------"])
        lines.extend(f"- {limitation}" for limitation in context.limitations)
    lines.append("")
    return "\n".join(lines)


def _required(environment: dict[str, str], name: str) -> str:
    value = environment.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} is not configured.")
    return value.strip()


def _value(value: object) -> str:
    return "NONE" if value is None else str(value)


def _money(value: float | None) -> str:
    return "NONE" if value is None else f"${value:,.0f}"
