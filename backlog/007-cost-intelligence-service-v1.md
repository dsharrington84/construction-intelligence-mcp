# Backlog 007 — Cost Intelligence Service v1

## Objective

Implement a governed Cost Intelligence Service that provides historical cost context for one project using certified Caltrans bid history and project scope.

The service must answer:

- What comparable historical projects and bid items exist?
- What historical value range is supported?
- Which cost observations are most relevant to this project?
- How complete and reliable is the available cost evidence?

It must not create an estimate or invent unit prices.

## Inputs

- `project_id`
- `ProjectIntelligence`
- governed project scope
- certified bid, award, bid-item, engineer-estimate, and cost-history objects available in the source DuckDB

Do not parse raw PDFs in this service.

## Outputs

Create typed models for:

- `CostIntelligence`
- `ComparableProjectCost`
- `BidItemCostObservation`
- `CostEvidence`

`CostIntelligence` must contain:

- project_id
- cost_intelligence_id
- comparable_projects
- comparable_bid_items
- project_value_statistics
- cost_risk_flags
- evidence
- source_confidence

Where supported, `project_value_statistics` should include:

- observation_count
- minimum
- median
- mean
- maximum

Do not report a statistic when its supporting observation count is zero.

## Comparable selection

Matching must be deterministic and explainable.

Prefer, in order:

1. Same governed primary scope and district
2. Same governed primary scope in Districts 7, 8, 11, and 12
3. Same scope statewide
4. Closely related secondary scope or project type

Use recency as a transparent ordering factor, not an opaque score.

Preserve all available lineage, including contract number, bid date, district, bidder/award status, bid item code, quantity, unit, and source object.

## Cost risk flags

Only derive flags supported by evidence. Examples may include:

- LIMITED_COMPARABLES
- HIGH_VALUE_SPREAD
- STALE_OBSERVATIONS
- MISSING_QUANTITY
- MIXED_UNITS
- DISTRICT_COVERAGE_LIMITED
- SCOPE_MATCH_LIMITED

Do not assign pursuit risk or bid probability.

## Architecture

Create:

- `models/cost_intelligence.py`
- `services/cost_intelligence_service.py`
- any dedicated read-only cost-history adapter/repository required
- `tests/test_cost_intelligence_service.py`

All SQL must remain in adapters/repositories.

The service must compose over existing project intelligence and scope classification. It must not duplicate project, market, contractor, strategic, or opportunity logic.

## Project Intelligence integration

Replace the cost placeholder in Project Intelligence with the governed `CostIntelligence` object.

If certified cost history is unavailable, return an explicit empty result with `source_confidence=NONE`.

## MCP

Add:

- `fetch_cost_intelligence(project_id)`

Update `fetch_project_intelligence(project_id)` so it includes the same cost intelligence object.

## Tests

Cover:

- same-district/same-scope comparables
- same-scope statewide comparables
- project-value statistics
- bid-item statistics
- deterministic ordering
- duplicate observation removal
- mixed-unit protection
- stale observation flag
- limited comparable flag
- preserved lineage
- missing project
- no cost history
- Project Intelligence integration
- MCP serialization

Integration tests may use the real DuckDB only when `CI_DATABASE` is available and must skip cleanly otherwise.

## Non-goals

Do not:

- create a bid estimate
- recommend markup
- forecast escalation beyond supported source objects
- invent unit prices or quantities
- modify source DuckDB data
- add portfolio logic
- redesign existing services

## Definition of done

- Typed governed cost intelligence objects exist.
- All statistics are traceable to certified observations.
- Missing data remains explicit.
- Project Intelligence includes cost intelligence.
- No SQL exists outside adapters/repositories.
- `pytest` passes.
- `ruff check .` passes.
- `ruff format --check .` passes.
- Commit on a feature branch and stop after commit.
- Do not attempt GitHub authentication or PR creation.
