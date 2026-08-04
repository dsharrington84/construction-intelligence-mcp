# 005 — Project Detail Service V1

**Status:** SUPERSEDED (Executive context contract only)
**Repository:** `dsharrington84/construction-intelligence-mcp`

## Objective

> The original Executive-context assumption is superseded by
> `docs/architecture/005-strategic-context-v2-contract.md`. This file remains the historical
> Project Detail V1 design record; it is not a certified Executive Evidence Contract.

Create the governed project-detail object that will support Opportunity Review and future contractor and cost intelligence.

## Required detail object

- Project identity and title
- Full preserved description
- District, county, route, location, and limits
- Advertisement timing and timing basis
- Programmed value and value availability
- Primary scope and classification evidence
- Executive program/source context
- Market context for the project district and scope
- Why the project surfaced
- Lineage and limitations
- Reserved attachment points for future contractor and cost intelligence

## Rules

- Compose existing services; do not duplicate SQL.
- Do not populate future contractor or cost sections with placeholders presented as facts.
- Preserve source text and lineage.
- Return a typed business model suitable for MCP and a project review page.

## Acceptance tests

- Fetch by project ID returns one complete detail object or `None`.
- Project fields reconcile to `ProjectService`.
- Opportunity fields reconcile to `OpportunityService`.
- Missing executive or market context is governed and does not fail the request.
- `pytest -q` passes.
- `ruff check .` passes.

## Definition of done

- Code committed on a new branch.
- PR opened against `main`.
- No source DuckDB modifications.
