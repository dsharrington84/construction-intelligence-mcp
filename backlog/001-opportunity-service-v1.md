# 001 — Opportunity Service V1

**Status:** READY  
**Repository:** `dsharrington84/construction-intelligence-mcp`

## Objective

Create the first governed opportunity layer by transforming `ProjectService` results into explainable potential-pursuit business objects.

## Scope

Implement:

- `models/opportunity.py`
- `services/opportunity_service.py`
- `tests/test_opportunity_service.py`
- MCP tool exposure only if it can be added without changing the existing ProjectService contract

## Required business object

Each opportunity must include at minimum:

- `opportunity_id`
- `project_id`
- `title`
- `district`
- `county`
- `route`
- `advertisement_date` or fiscal-year proxy
- `programmed_value`
- `primary_scope`
- `why_it_surfaced`
- `source_confidence`

## Rules

- Use `ProjectService`; do not query DuckDB directly.
- Do not introduce opaque numeric scoring.
- `why_it_surfaced` must be explicit and deterministic.
- Do not claim SEMA fit unless the current preserved project description supports it.
- Preserve missing values as governed limitations rather than inventing replacements.
- Default market scope is Districts 7, 8, 11, and 12.

## Required behaviors

- Search opportunities by district, scope, minimum value, advertisement window, and text.
- Rank deterministically using transparent ordering such as advertisement timing, value, and evidence completeness.
- Fetch one opportunity by ID.
- Return typed Pydantic models.

## Acceptance tests

- Opportunity records retain lineage to `project_id`.
- No duplicate opportunity IDs.
- Search filters work independently and in combination.
- Every returned opportunity has at least one `why_it_surfaced` reason.
- Missing value or date does not crash the service.
- No SQL exists in the opportunity service.
- `pytest -q` passes.
- `ruff check .` passes.

## Definition of done

- Code committed on a new branch.
- PR opened against `main`.
- PR summary lists files changed, commands run, test results, and limitations.
- No source DuckDB modifications.
