# Program 100 — Executive Intelligence

Status: BLOCKED

## Program Purpose

Explain why Caltrans is investing in a governed project using certified executive evidence.

Program 100 is a contract-gated intelligence program. It does not implement bid/no-bid,
contractor, cost, opportunity scoring, or portfolio capabilities. It establishes the path from an
Executive Processing Pipeline through a Certified Data Product and evidence engine into governed
Strategic Context.

## Constitutional Alignment

Program 100 follows the platform vocabulary and boundaries required by the Constitution:

- Processing Pipelines create truth.
- Certified Data Products preserve truth.
- Intelligence explains truth.
- Applications present truth.
- Evidence precedes conclusions.
- Lineage is mandatory.
- Business contracts precede implementation.
- Consumers depend on contracts rather than physical storage.

The checked-in repository currently lacks `docs/000-CONSTITUTION.md`; this backlog preserves the
required vocabulary from the assigned governance instructions and must be reconciled with the
Constitution before implementation begins.

## Program Architecture

```text
Executive Processing Pipeline
        ↓
Executive Knowledge Certified Data Product
        ↓
Executive Evidence Engine
        ↓
Strategic Context Intelligence
        ↓
Project Intelligence / MCP Consumers
```

- Processing produces the governed data.
- CDP-001 defines the contract for Executive Knowledge.
- The Evidence Engine translates the CDP into canonical evidence objects.
- Strategic Context produces project-specific intelligence from governed Project objects and
  canonical ExecutiveEvidence.
- Project Intelligence and MCP consumers do not query physical Executive relations directly.

## Program Initiatives

| Initiative | Status | Dependency | Unlock condition | Output | Review gate |
|---|---|---|---|---|---|
| 101 Executive Knowledge Certified Data Product | READY | Phase 0 governance, Constitution, 010A, 010B, and warehouse inspection evidence | CDP-001 is reviewed and accepted | Accepted Executive Knowledge Certified Data Product contract | Contract review confirms grain, lineage, eligibility, and consumer guarantees |
| 102 Executive Evidence Engine | BLOCKED_BY_CONTRACT | 101 accepted | CDP-001 acceptance makes the engine contract implementable | Canonical ExecutiveEvidence objects and diagnostics | Engine review confirms eligible evidence, lineage preservation, and governed failure behavior |
| 103 Strategic Context Intelligence | BLOCKED_BY_IMPLEMENTATION | 101 accepted and 102 certified | ExecutiveEvidence implementation is certified and reviewed | StrategicContext object integrated with Project Intelligence and MCP serialization | Business demonstration proves project-specific context uses only governed evidence |

## Current Status

Repository evidence supports the following status:

- 101 is READY to execute as a contract initiative because `docs/data-products/100-executive-certified-data-product.md` is not present and no accepted CDP-001 contract is checked in.
- 102 is BLOCKED_BY_CONTRACT because no accepted Executive Knowledge CDP contract exists.
- 103 is BLOCKED_BY_IMPLEMENTATION because it depends on both CDP-001 acceptance and a certified Executive Evidence Engine.

Older Project Intelligence behavior, including empty executive signal placeholders, does not make
Program 100 complete. No initiative is complete until its current review gate is satisfied.

## Program Review Gate

Can the platform explain why Caltrans is investing in a Southern California project using only
governed, traceable Executive evidence?

## Program Acceptance Criteria

Program 100 is complete only when all of the following are true:

- CDP-001 is accepted.
- Canonical ExecutiveEvidence is implemented.
- Certified source lineage is preserved.
- Ineligible statuses are excluded.
- Strategic Context consumes ExecutiveEvidence rather than physical warehouse tables.
- Every conclusion references evidence.
- Empty or NONE results remain valid when no defensible evidence exists.
- Actual CI_DATABASE integration produces nonzero eligible Executive evidence.
- At least one Southern California project receives explainable context.
- Smoke test completes promptly.
- MCP output preserves evidence, lineage, confidence, and limitations.
- All tests and checks pass.

## Non-Goals

Program 100 does not produce Program 200 or Program 300 capabilities. It must not implement:

- bid/no-bid recommendations;
- contractor intelligence;
- cost intelligence;
- opportunity scoring;
- portfolio recommendations;
- AI-generated findings;
- unsupported semantic conclusions.
