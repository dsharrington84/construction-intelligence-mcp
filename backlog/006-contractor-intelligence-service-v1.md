# Backlog 006 — Contractor Intelligence Service v1

## Objective

Implement a governed Contractor Intelligence Service that explains which contractors are most relevant to a project based on certified historical bid and subcontractor relationships.

The service must answer:

- Which prime contractors have historically pursued comparable work?
- Which contractors have won comparable work?
- Which contractors are active in the relevant district and scope?
- What evidence supports each contractor-project relationship?

It must not predict a winner or recommend a pursuit decision.

## Inputs

- `project_id`
- `ProjectIntelligence`
- Existing certified bidder, bid-tab, award, and subcontractor relationship objects in the source DuckDB

Do not parse PDFs or raw documents in this service.

## Outputs

Create typed models for:

- `ContractorIntelligence`
- `ContractorCandidate`
- `ContractorEvidence`

`ContractorIntelligence` must contain:

- project_id
- contractor_intelligence_id
- likely_prime_pursuers
- likely_specialty_participants
- district_activity_summary
- scope_activity_summary
- evidence
- source_confidence

Each `ContractorCandidate` should contain, where supported:

- contractor_id
- contractor_name
- role
- comparable_project_count
- comparable_bid_count
- comparable_win_count
- district_project_count
- scope_project_count
- most_recent_activity_date
- evidence_strength
- evidence_ids

## Evidence and lineage

Every surfaced contractor must have traceable evidence.

Evidence must preserve available identifiers such as:

- contract number
- bidder identifier
- subcontractor license or identifier
- source table/object
- bid rank or award status
- district
- project type/scope
- source date or bid date

Evidence strength values:

- DIRECT
- STRONG
- SUPPORTING
- CONTEXTUAL

Do not invent missing bidder, award, or relationship facts.

## Matching rules

Matching must be deterministic and explainable.

Prefer, in order:

1. Same governed project scope and district
2. Same governed scope in Southern California Districts 7, 8, 11, and 12
3. Same district with adjacent scope
4. Statewide comparable scope

Use only certified or canonical historical objects when available.

Do not use an LLM, randomness, or opaque scoring.

## Architecture

Create:

- `models/contractor_intelligence.py`
- `services/contractor_intelligence_service.py`
- any dedicated read-only adapter/repository needed for contractor history
- `tests/test_contractor_intelligence_service.py`

All SQL must remain in adapters/repositories.

The service must compose over existing project intelligence and scope classification. It must not duplicate classification, market, strategic, or opportunity logic.

## Project Intelligence integration

Replace the contractor placeholder in Project Intelligence with the governed `ContractorIntelligence` object.

If contractor history is unavailable, return an explicit empty result with `source_confidence=NONE` rather than failing or inventing contractors.

## MCP

Add:

- `fetch_contractor_intelligence(project_id)`

Update `fetch_project_intelligence(project_id)` so it returns the same contractor intelligence object.

## Tests

Cover:

- same-district/same-scope contractor evidence
- same-scope statewide evidence
- prime pursuit history
- award history
- specialty/subcontractor participation
- duplicate contractor consolidation
- deterministic ordering
- preserved lineage
- missing contractor history
- missing project
- Project Intelligence integration
- MCP serialization

Integration tests may use the real DuckDB only when `CI_DATABASE` is available and must skip cleanly otherwise.

## Non-goals

Do not:

- predict the low bidder
- rank contractors using invented weights
- recommend whether SEMA should pursue
- add cost intelligence
- add portfolio logic
- modify source DuckDB data
- parse source PDFs
- redesign existing services

## Definition of done

- Typed contractor intelligence business objects exist.
- Every surfaced contractor is evidence-backed.
- Duplicate contractor identities are governed and consolidated.
- Project Intelligence includes contractor intelligence.
- Missing evidence returns an explicit empty/NONE result.
- `pytest` passes.
- `ruff check .` passes.
- `ruff format --check .` passes.
- Commit on a feature branch and stop after commit.
- Do not attempt GitHub authentication or PR creation.
