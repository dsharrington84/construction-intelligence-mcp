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

## Program 100 — Executive Intelligence

Program objective: explain why Caltrans is investing in a governed project using certified
Executive evidence.

| Initiative | Status | Dependency | Unlock condition |
|---|---|---|---|
| 100 Executive Intelligence Program | ACTIVE | 101, 102, and 103 | Program review gate succeeds for a Southern California project using governed, traceable Executive evidence |
| 101 Executive Certified Data Product | IN_REVIEW | Phase 0 governance, Constitution, 010A, 010B, and warehouse inspection evidence | CDP-001 is reviewed and accepted |
| 102 Executive Evidence Engine | BLOCKED_BY_CONTRACT | 101 accepted | Accepted CDP-001 makes ExecutiveEvidence implementation possible |
| 103 Strategic Context Intelligence | BLOCKED_BY_IMPLEMENTATION | 101 accepted and 102 certified | ExecutiveEvidence implementation is certified and reviewed |

Repository evidence as of this roadmap update:

- CDP-001 exists as PR #14 and remains pending acceptance for this branch.
- 010A and 010B research documents under `docs/research/` show Executive warehouse and processing evidence is diagnostic and not certified until CDP-001 acceptance.
- Program 100 implementation remains blocked until CDP-001 is accepted, even though Program 100 planning is ACTIVE.

## Program 200 — Contractor Intelligence

Program objective: explain contractor participation and historical market behavior using certified
Contractor evidence.

Status: BLOCKED

Reason: Program 100 must complete before Program 200 implementation begins. No Program 200
initiative is READY.

| Initiative | Status | Dependency | Unlock condition |
|---|---|---|---|
| 200 Contractor Intelligence Program | BLOCKED | Program 100 certified; 201, 202, and 203 | Program review gate succeeds using governed, traceable Contractor evidence |
| 201 Contractor Certified Data Product | BLOCKED | Program 100 certified | Accepted Contractor Certified Data Product contract defines grain, keys, lineage, certification, consumer guarantees, and limitations |
| 202 Contractor Evidence Engine | BLOCKED_BY_CONTRACT | 201 accepted | Accepted Contractor Certified Data Product makes ContractorEvidence implementation possible |
| 203 Contractor Intelligence | BLOCKED_BY_IMPLEMENTATION | 201 accepted and 202 certified | ContractorEvidence implementation is certified and reviewed |

Program review question: Can the platform explain contractor participation and historical market
behavior using only governed contractor evidence?

Program 200 preserves the Program 100 architecture:

```text
Contractor Processing Pipeline
        ↓
Contractor Certified Data Product
        ↓
Contractor Evidence Engine
        ↓
Contractor Intelligence
        ↓
Project Intelligence
        ↓
Applications
```

Program 200 must not add bid/no-bid recommendations, opportunity scoring, pursuit portfolio
recommendations, cost intelligence, or application shortcuts around governed Contractor evidence.

## Program 300 — Cost & Opportunity Intelligence

Status: BLOCKED

Program 300 remains blocked until its planned unlock condition is accepted in a future roadmap or
backlog contract. Program 300 must not begin through Program 100 or Program 200 work.
# Platform Programs

This document records the platform roadmap at the Program level. It does not define implementation details.

## Phase 0: Platform Governance

Status: Completed

---

## Program 100: Executive Intelligence

- 101 Executive Certified Data Product
- 102 Executive Evidence Engine
- 103 Strategic Context

Status: Not Started

---

## Program 200: Contractor Intelligence

- 201 Contractor Certified Data Product
- 202 Contractor Evidence Engine
- 203 Contractor Intelligence

Status: BLOCKED

Reason: Program 100 must complete before implementation begins.

---

## Program 300: Cost & Opportunity Intelligence

- 301 Cost Certified Data Product
- 302 Cost Evidence Engine
- 303 Cost Intelligence
- 304 Opportunity Intelligence
- 305 Portfolio Intelligence

Status: Not Started
