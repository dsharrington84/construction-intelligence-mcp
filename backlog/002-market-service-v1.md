# 002 — Market Service V1

**Status:** READY  
**Repository:** `dsharrington84/construction-intelligence-mcp`

## Objective

Expose governed Southern California market intelligence as typed business objects for Districts 7, 8, 11, and 12.

## Scope

Implement:

- `models/market.py`
- `services/market_service.py`
- `tests/test_market_service.py`

## Required outputs

- Overall next-12-month market summary
- District summaries
- Work-type summaries
- Project counts
- Total programmed value
- Median project value
- Minimum and maximum project value
- Value coverage and limitations as supporting metadata, not headline fields

## Rules

- Consume governed services or adapter abstractions; do not duplicate consumer SQL.
- Use distinct project identifiers for project counts.
- Preserve District 7, 8, 11, and 12 as the default market scope.
- Do not present average and median together in the primary summary.
- Distinguish current 12-month totals from prior-period change.
- Do not infer contractor behavior.

## Acceptance tests

- Counts use distinct project grain.
- District totals reconcile to overall totals for included records.
- Work-type totals reconcile to overall totals for included records.
- Missing programmed values are counted and governed.
- Date/fiscal-year proxy is explicitly represented.
- `pytest -q` passes.
- `ruff check .` passes.

## Definition of done

- Code committed on a new branch.
- PR opened against `main`.
- No source DuckDB modifications.
