# 005 — Strategic Context v2 Contract

## Evidence state and relationship to 010A/010B

Strategic Context v2 replaces the original 005 Executive placeholder with typed, evidence-backed
conclusions. The authoritative checked-in 010A warehouse inventory has status `not_generated`, no
relations, and no measured joins. The authoritative 010B analysis found no Executive producer or
certified consumption path in this repository. Consequently, **no physical Executive warehouse
dependency is certified in the current snapshot**. The adapter fails clearly rather than selecting
a relation by name, shape, or version. Regenerating 010A is necessary but not sufficient: relation
roles and joins also require owner certification and 010B producer evidence.

## Executive Evidence Contract

`ExecutiveEvidence` preserves the source section, document, excerpt, refinement status, evidence
type, and physical lineage. Semantic attributes remain distinct. Source text is never renamed to
`governed_finding`, and no single relation is assumed to contain every attribute. Source evidence
is the original section; refined or semantic evidence must retain a measured, certified path to it.

Eligible statuses are `USABLE`, `USABLE_WITH_LIMITATION`, and `CONTEXT_ONLY`.
`REVIEW_REQUIRED` and `EXCLUDED` are rejected. Unknown statuses fail Pydantic validation and must
be reported by a future certified adapter before records are returned. Context-only records can
produce contextual evidence only.

## Matching, strength, and confidence

Matching is deterministic and exact. Precedence is explicit project, route/county,
district-plus-program, exact project-type/asset, then statewide context. Regionally scoped evidence
that does not exactly match is omitted. There is no fuzzy matching, randomness, or AI.

`DIRECT` requires governed project, route, county, or district-plus-program linkage. `SUPPORTING`
requires exact governed scope or asset alignment. `CONTEXTUAL` is statewide/owner context.
Conclusions contain the IDs of all supporting evidence.

Confidence is `HIGH` for direct plus supporting evidence without limitations, `MODERATE` for a
direct item or multiple supporting items without limitations, `LIMITED` for contextual or limited
evidence, and `NONE` when nothing defensible matches. It describes source evidence, not pursuit.

## Limitations and certified dependencies

The current implementation can compose and serialize already-certified `ExecutiveEvidence`, but
the checked-in artifacts cannot supply any. The production adapter therefore reports certification
limitations and raises `ExecutiveContractError`. This is the required discrepancy behavior; an
empty strategic result must not be used to conceal a missing warehouse contract.

## Non-goals

This contract does not alter DuckDB, process PDFs, change upstream scripts, create warehouse data,
invent programs/outcomes, recommend bid/no-bid, add cost/contractor/portfolio intelligence, or
infer joins and semantics from column names.
