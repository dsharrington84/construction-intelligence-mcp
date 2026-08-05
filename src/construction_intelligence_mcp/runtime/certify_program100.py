from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TextIO

from construction_intelligence_mcp.adapters.executive_evidence_adapter import (
    CdpPhysicalImplementationMapping,
)
from construction_intelligence_mcp.models.executive_evidence import ExecutiveEvidenceResult
from construction_intelligence_mcp.models.project import ProjectSearchRequest, ProjectSummary
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
BLOCKED_PROJECT_LINKAGE_MESSAGE = (
    "Program 100 business certification blocked because the accepted Executive Evidence mapping "
    "does not expose sufficient governed project-linkage metadata."
)


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
        result = _build_business_report(env)
    except Exception as exc:  # noqa: BLE001 - command must report governed failure to operators.
        stdout.write("\nCERTIFICATION FAILED\n")
        stdout.write(f"{exc}\n")
        return 1

    stdout.write("\n")
    stdout.write(result.report)
    return result.exit_code


class CertificationResult:
    """Business report plus command exit code."""

    def __init__(self, *, report: str, exit_code: int) -> None:
        self.report = report
        self.exit_code = exit_code


def _build_business_report(environment: dict[str, str]) -> CertificationResult:
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

    evidence_result = evidence_service.fetch_executive_evidence()
    selected_project = candidates[0]
    selected_context: StrategicContext | None = None
    selected_intelligence: ProjectIntelligence | None = None
    for candidate in candidates:
        project = project_service.fetch_project(candidate.project_id)
        if project is None:
            continue
        context = strategic_context_service.fetch_strategic_context(project.project_id)
        intelligence = intelligence_service.fetch_project_intelligence(project.project_id)
        selected_project = candidate
        selected_context = context
        selected_intelligence = intelligence
        if context is not None and intelligence is not None and context.evidence:
            return CertificationResult(
                report=_format_passing_report(
                    database=database,
                    mapping=mapping,
                    intelligence=intelligence,
                    context=context,
                ),
                exit_code=0,
            )

    return CertificationResult(
        report=_format_blocked_report(
            database=database,
            mapping=mapping,
            selected_project=selected_project,
            context=selected_context,
            intelligence=selected_intelligence,
            evidence_result=evidence_result,
        ),
        exit_code=1,
    )


def _format_passing_report(
    *,
    database: Path,
    mapping: CdpPhysicalImplementationMapping,
    intelligence: ProjectIntelligence,
    context: StrategicContext,
) -> str:
    project = intelligence.project
    lines = _report_header(
        result="PASS",
        database=database,
        mapping=mapping,
    )
    lines.extend(_project_lines(project))
    lines.extend(_executed_chain_lines())
    lines.extend(_strategic_context_lines(context))
    return "\n".join(lines)


def _format_blocked_report(
    *,
    database: Path,
    mapping: CdpPhysicalImplementationMapping,
    selected_project: ProjectSummary,
    context: StrategicContext | None,
    intelligence: ProjectIntelligence | None,
    evidence_result: ExecutiveEvidenceResult,
) -> str:
    lines = _report_header(
        result="BLOCKED",
        database=database,
        mapping=mapping,
    )
    lines.append(BLOCKED_PROJECT_LINKAGE_MESSAGE)
    lines.extend(_project_lines(selected_project))
    lines.extend(_executed_chain_lines())
    if context is not None:
        lines.extend(_strategic_context_lines(context))
    else:
        lines.extend(["", "Strategic context", "-----------------", "Strategic context: NONE"])
    lines.extend(
        [
            "",
            "Project intelligence",
            "--------------------",
            "Project intelligence returned: YES"
            if intelligence is not None
            else "Project intelligence returned: NO",
        ]
    )
    lines.extend(_executive_evidence_lines(evidence_result))
    return "\n".join(lines)


def _report_header(
    *,
    result: str,
    database: Path,
    mapping: CdpPhysicalImplementationMapping,
) -> list[str]:
    return [
        "Business certification",
        "----------------------",
        f"Certification result: {result}",
        f"Program: {PROGRAM}",
        f"Certified Data Product: {CERTIFIED_DATA_PRODUCT}",
        f"Runtime database: {database}",
        f"CDP-001 mapping: {mapping.relation}",
        f"Mapping status: {mapping.certification_status}",
        f"Mapping role: {mapping.relation_role}",
    ]


def _project_lines(project: ProjectSummary) -> list[str]:
    return [
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
    ]


def _executed_chain_lines() -> list[str]:
    return [
        "",
        "Executed service chain",
        "----------------------",
        "1. fetch_project() executed for the governed project above.",
        "2. fetch_strategic_context() executed through the Strategic Context service.",
        "3. fetch_project_intelligence() executed through the Project Intelligence service.",
    ]


def _strategic_context_lines(context: StrategicContext) -> list[str]:
    lines = [
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
    if context.evidence:
        lines.extend(["", "Strategic evidence", "------------------"])
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
    if context.limitations:
        lines.extend(["", "Limitations", "-----------"])
        lines.extend(f"- {limitation}" for limitation in context.limitations)
    return lines


def _executive_evidence_lines(result: ExecutiveEvidenceResult) -> list[str]:
    lines = [
        "",
        "Accepted Executive evidence diagnostics",
        "---------------------------------------",
        f"Selected relation: {result.diagnostics.selected_relation}",
        f"Eligible evidence count: {result.diagnostics.eligible_evidence_count}",
        f"Final evidence count: {result.diagnostics.final_evidence_count}",
        f"Lineage coverage: {result.diagnostics.lineage_coverage:.2f}",
        "",
        "Accepted Executive evidence sample",
        "----------------------------------",
    ]
    for item in result.evidence[:5]:
        lines.extend(
            [
                f"- Evidence ID: {item.evidence_id}",
                f"  Source document: {item.source_document}",
                f"  Source section: {item.source_section_id}",
                f"  Source relation: {item.source_lineage.source_relation}",
                f"  Source keys: {item.source_lineage.source_keys}",
                f"  Semantic metadata keys: {sorted(item.semantic_metadata)}",
                f"  Excerpt: {item.source_text}",
            ]
        )
    return lines


def _required(environment: dict[str, str], name: str) -> str:
    value = environment.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} is not configured.")
    return value.strip()


def _value(value: object) -> str:
    return "NONE" if value is None else str(value)


def _money(value: float | None) -> str:
    return "NONE" if value is None else f"${value:,.0f}"
