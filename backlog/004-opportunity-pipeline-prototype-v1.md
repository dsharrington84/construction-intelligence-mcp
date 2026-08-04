# 004 — Opportunity Pipeline Prototype V1

**Status:** BLOCKED by 001 and 003  
**Repository:** `dsharrington84/construction-intelligence-mcp`

## Objective

Create a visible prototype that lists potential pursuits and lets the user select projects into a live pursuit portfolio.

## Scope

Build a lightweight local web interface or generated HTML prototype that consumes `OpportunityService` only.

## Required interface

Project list fields:

- Select / review control
- Project title
- District
- Route / county / location
- Advertisement timing
- Programmed value
- Primary scope
- Why it surfaced
- Details control

Live portfolio panel:

- Selected project count
- Total programmed value
- District mix
- Primary-scope mix
- Median selected project value

Filters:

- District 7, 8, 11, 12
- Primary scope
- Advertisement window
- Minimum value
- Text search

## Rules

- No SQL in the consumer.
- No developer metadata in the visible header.
- No average value in the primary view.
- No contractor intelligence yet.
- Selection state may be browser-local in V1.
- The page must lead with projects, not market metrics.

## Acceptance tests

- Selecting or clearing a project updates the portfolio immediately.
- Filters update the visible list without changing source data.
- Every project shows a human-readable scope and why-it-surfaced reasons.
- Empty selection and missing-value states are handled cleanly.
- `pytest -q` passes.
- `ruff check .` passes.

## Definition of done

- Prototype launch command documented.
- Screenshot or generated artifact included in PR notes.
- Code committed on a new branch.
- PR opened against `main`.
