# Construction Intelligence Program Roadmap

This roadmap tracks governed program-level work. Status values are planning states, not evidence
that implementation exists.

## Status Values

- `ACTIVE` — planning or implementation sequencing has begun.
- `READY` — dependencies are satisfied enough for the next contract or implementation task to begin.
- `IN_REVIEW` — implementation or contract work is under review and not yet accepted.
- `BLOCKED` — prerequisite work is incomplete.
- `BLOCKED_BY_CONTRACT` — an accepted business contract is missing.
- `BLOCKED_BY_IMPLEMENTATION` — a required implementation is missing or uncertified.
- `COMPLETE` — review gates are accepted and validated.

## Phase 0 — Platform Governance

Status: COMPLETE

## Program 100 — Executive Intelligence

Status: ACTIVE

Program objective: explain why Caltrans is investing in a governed project using certified
Executive evidence.

| Initiative | Status | Dependency | Unlock condition |
|---|---|---|---|
| 100 Executive Intelligence Program | ACTIVE | 101, 102, and 103 | Program review gate succeeds for a Southern California project using governed, traceable Executive evidence |
| 101 Executive Certified Data Product | COMPLETE | Phase 0 governance, Constitution, 010A, 010B, and warehouse inspection evidence | CDP-001 accepted |
| 102 Executive Evidence Engine | COMPLETE | 101 accepted and explicit CDP-001 mapping | ExecutiveEvidence implementation and certification repair reviewed and merged |
| 103 Strategic Context Intelligence | IN_REVIEW | 101 accepted and 102 complete | StrategicContext implementation is under review |

Current repository evidence:

- CDP-001 was accepted through PR #14.
- 010A and 010B remain diagnostic research inputs and do not replace the accepted CDP-001 contract.
- Program 100 Initiative 102 is complete; the merged engine and certification repair require exactly one explicit accepted, current, schema-qualified CDP-001 physical implementation mapping.
- Initiative 103 is in review and consumes ExecutiveEvidence through the Executive Evidence Engine.

## Program 200 — Contractor Intelligence

Status: ACTIVE

Planning state: Program 200 planning is ACTIVE following certification of the Construction
Intelligence Platform v1.0 POC and the Program 100 reference implementation. Production
implementation remains dependency-gated by accepted contractor contracts and certified evidence.

Program objective: provide Competitive Market Intelligence by explaining observable contractor
participation, repeat bidding, winning, competitiveness, bidder counts, market concentration,
district experience, project-type experience, and prime/subcontractor relationships using certified
Contractor evidence.

| Initiative | Status | Dependency |
|---|---|---|
| 201 Contractor Certified Data Product | READY | Certified Construction Intelligence Platform v1.0 POC and certified Program 100 reference implementation |
| 202 Contractor Evidence Engine | BLOCKED_BY_CONTRACT | 201 accepted |
| 203 Contractor Intelligence | BLOCKED_BY_IMPLEMENTATION | 201 accepted and 202 certified |

## Program 300 — Cost & Opportunity Intelligence

Status: BLOCKED

| Initiative | Status | Dependency |
|---|---|---|
| 301 Cost Certified Data Product | BLOCKED | Future roadmap or backlog contract |
| 302 Cost Evidence Engine | BLOCKED | Future roadmap or backlog contract |
| 303 Cost Intelligence | BLOCKED | Future roadmap or backlog contract |
| 304 Opportunity Intelligence | BLOCKED | Future roadmap or backlog contract |
| 305 Portfolio Intelligence | BLOCKED | Future roadmap or backlog contract |
