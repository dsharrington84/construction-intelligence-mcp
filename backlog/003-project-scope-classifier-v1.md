# 003 — Project Scope Classifier V1

**Status:** READY  
**Repository:** `dsharrington84/construction-intelligence-mcp`

## Objective

Replace broad project categories with estimator-readable primary scopes derived from preserved project descriptions.

## Scope

Implement a deterministic classifier for at least:

- Bridge Rehabilitation
- Bridge Replacement
- Pavement Rehabilitation
- Pavement Preservation
- Full Reconstruction
- Widening / Lane Addition
- Interchange Improvements
- Drainage / Stormwater
- Safety Improvements
- Complete Streets / ADA
- ITS / Electrical
- Retaining Walls / Earthwork
- Mixed Heavy Civil
- Unresolved

## Rules

- Use preserved project description and available location/program text.
- Do not classify from programmed value, district, or contractor assumptions.
- Return matched evidence terms and classification basis.
- Keep broad source category as lineage metadata.
- Deterministic rules only in V1; no model calls.

## Acceptance tests

- Pavement examples separate rehabilitation, preservation, and reconstruction.
- Bridge rehabilitation and replacement are distinct.
- Ambiguous mixed scopes return `Mixed Heavy Civil` or `Unresolved` with limitation.
- Classification output includes evidence terms.
- No database writes.
- `pytest -q` passes.
- `ruff check .` passes.

## Definition of done

- Classifier integrated into `ProjectService` without breaking its public contract.
- Code committed on a new branch.
- PR opened against `main`.
