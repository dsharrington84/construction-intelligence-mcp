from __future__ import annotations

from datetime import date

from construction_intelligence_mcp.models.opportunity import Opportunity, OpportunitySearchRequest
from construction_intelligence_mcp.models.project import ProjectSearchRequest, ProjectSummary
from construction_intelligence_mcp.services.project_service import ProjectService

_OPPORTUNITY_ID_PREFIX = "project-opportunity:"


class OpportunityService:
    """Turn governed projects into explainable potential pursuits."""

    def __init__(self, project_service: ProjectService) -> None:
        self.project_service = project_service

    def search_opportunities(self, request: OpportunitySearchRequest) -> list[Opportunity]:
        projects = self.project_service.search_projects(
            ProjectSearchRequest(
                districts=request.districts or None,
                advertisement_start=request.advertisement_start,
                advertisement_end=request.advertisement_end,
                minimum_programmed_value=request.minimum_programmed_value,
                text=request.text,
                limit=1000,
            )
        )
        matches = [project for project in projects if self._matches(project, request)]
        matches.sort(key=self._ranking_key)
        return [self._to_opportunity(project, request) for project in matches[: request.limit]]

    def fetch_opportunity(self, opportunity_id: str) -> Opportunity | None:
        if not opportunity_id.startswith(_OPPORTUNITY_ID_PREFIX):
            return None
        project_id = opportunity_id.removeprefix(_OPPORTUNITY_ID_PREFIX)
        if not project_id:
            return None
        project = self.project_service.fetch_project(project_id)
        if project is None:
            return None
        return self._to_opportunity(project, OpportunitySearchRequest(districts=[]))

    @staticmethod
    def _matches(project: ProjectSummary, request: OpportunitySearchRequest) -> bool:
        if request.districts and project.district not in request.districts:
            return False
        if request.scope and request.scope.casefold() not in project.primary_scope.casefold():
            return False
        if request.minimum_programmed_value is not None and (
            project.programmed_value is None
            or project.programmed_value < request.minimum_programmed_value
        ):
            return False
        if request.advertisement_start and (
            project.advertisement_date is None
            or project.advertisement_date < request.advertisement_start
        ):
            return False
        if request.advertisement_end and (
            project.advertisement_date is None
            or project.advertisement_date > request.advertisement_end
        ):
            return False
        if request.text:
            searchable = " ".join(
                value
                for value in (
                    project.title,
                    project.description,
                    project.county,
                    project.route,
                    project.location,
                    project.primary_scope,
                )
                if value
            )
            if request.text.casefold() not in searchable.casefold():
                return False
        return True

    @classmethod
    def _to_opportunity(
        cls, project: ProjectSummary, request: OpportunitySearchRequest
    ) -> Opportunity:
        reasons = cls._reasons(project, request)
        return Opportunity(
            opportunity_id=f"{_OPPORTUNITY_ID_PREFIX}{project.project_id}",
            project_id=project.project_id,
            title=project.title,
            district=project.district,
            county=project.county,
            route=project.route,
            advertisement_date=project.advertisement_date,
            advertisement_fiscal_year=project.advertisement_fiscal_year,
            programmed_value=project.programmed_value,
            primary_scope=project.primary_scope,
            why_it_surfaced=reasons,
            source_confidence=cls._source_confidence(project),
        )

    @staticmethod
    def _reasons(project: ProjectSummary, request: OpportunitySearchRequest) -> list[str]:
        reasons: list[str] = []
        if request.districts and project.district in request.districts:
            reasons.append(f"Located in selected Caltrans District {project.district}")
        if request.scope:
            reasons.append(f"Primary scope matches requested scope: {project.primary_scope}")
        if request.minimum_programmed_value is not None:
            reasons.append(
                f"Programmed value meets minimum of ${request.minimum_programmed_value:,.0f}"
            )
        if request.advertisement_start or request.advertisement_end:
            reasons.append("Advertisement date is within the requested window")
        if request.text:
            reasons.append(f"Project fields contain requested text: {request.text}")
        if not reasons:
            reasons.append("Available as a governed potential-pursuit project")
        return reasons

    @staticmethod
    def _source_confidence(project: ProjectSummary) -> str:
        evidence = (
            project.district,
            project.county,
            project.route,
            project.advertisement_date or project.advertisement_fiscal_year,
            project.programmed_value,
        )
        present = sum(value is not None for value in evidence)
        if present >= 4 and project.primary_scope != "Unclassified Project":
            return "high"
        if present >= 2:
            return "moderate"
        return "limited"

    @classmethod
    def _ranking_key(cls, project: ProjectSummary) -> tuple[date, float, int, str]:
        advertisement_date = project.advertisement_date
        if advertisement_date is None and project.advertisement_fiscal_year is not None:
            advertisement_date = date(project.advertisement_fiscal_year, 1, 1)
        advertisement_date = advertisement_date or date.max
        programmed_value = -(project.programmed_value or 0)
        completeness = -cls._evidence_completeness(project)
        return advertisement_date, programmed_value, completeness, project.project_id

    @staticmethod
    def _evidence_completeness(project: ProjectSummary) -> int:
        evidence = (
            project.district,
            project.county,
            project.route,
            project.advertisement_date or project.advertisement_fiscal_year,
            project.programmed_value,
            None if project.primary_scope == "Unclassified Project" else project.primary_scope,
        )
        return sum(value is not None for value in evidence)
