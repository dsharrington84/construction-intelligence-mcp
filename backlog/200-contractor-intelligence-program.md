# Program 200 — Contractor Intelligence

Status: BLOCKED

Reason: Program 100 must complete before Program 200 implementation begins.

## Program Purpose

Explain who participates in the governed construction market, how contractors have historically
performed, and what governed contractor evidence exists for a project.

Program 200 is a planning initiative only. It establishes a dependency-gated roadmap from a
Contractor Processing Pipeline through a Contractor Certified Data Product and evidence engine into
governed Contractor Intelligence. It does not implement Contractor Intelligence, Contractor
Evidence, Contractor Certified Data Product production, services, adapters, MCP tools, or application
features.

## Business Questions

Program 200 answers:

- Who participates in this market?
- How have contractors historically performed?
- What governed contractor evidence exists for this project?

Program 200 does not answer:

- Should we pursue this project?
- How much should it cost?
- What opportunity score should be assigned?

Those questions belong to later governed programs and must not be implemented through Program 200.

## Constitutional Alignment

Program 200 follows the platform vocabulary and boundaries required by the Constitution:

- Processing Pipelines create truth.
- Certified Data Products preserve truth.
- Evidence translates certified truth into canonical, traceable support.
- Intelligence explains truth through governed business contracts.
- Applications present truth and consume Intelligence Layer contracts.
- Business contracts precede implementation.
- Lineage is mandatory for material contractor facts.
- Intelligence must not invent missing contractor business values.
- Consumers must not depend on physical processing internals or storage-specific structures.

The Constitution is authoritative for Program 200. These planning documents align with Phase 0
governance, Program 100 architecture, and the accepted platform decision that Certified Data
Products form the contractual boundary between processing and intelligence.

## Architecture

Program 200 shall follow the same constitutional architecture as Program 100:

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

- Processing produces governed contractor data after Program 100 prerequisites are complete.
- The Contractor Certified Data Product defines the business contract for contractor evidence.
- The Contractor Evidence Engine translates the accepted contract into canonical ContractorEvidence.
- Contractor Intelligence produces ContractorContext from governed evidence.
- Project Intelligence may consume ContractorContext only after the evidence and intelligence
  contracts are implemented and reviewed.
- Applications must not query physical Contractor relations directly.

## Dependencies

| Initiative | Status | Dependency | Unlock condition | Output | Review gate |
|---|---|---|---|---|---|
| 201 Contractor Certified Data Product | BLOCKED | Program 100 certified | Program 100 completes its review gate | Pending Contractor Certified Data Product contract | Contract review confirms grain, keys, lineage, certification, consumer guarantees, and limitations |
| 202 Contractor Evidence Engine | BLOCKED_BY_CONTRACT | 201 accepted | Accepted Contractor Certified Data Product makes ContractorEvidence implementation possible | Canonical ContractorEvidence objects and diagnostics | Engine review confirms eligible evidence, lineage preservation, diagnostics, validation, and governed failure behavior |
| 203 Contractor Intelligence | BLOCKED_BY_IMPLEMENTATION | 201 accepted and 202 certified | ContractorEvidence implementation is certified and reviewed | ContractorContext object suitable for Project Intelligence consumption | Business review proves contractor context uses only governed contractor evidence |

No Program 200 initiative is READY. Program 200 remains blocked until Program 100 completes and is
certified through its review gate.

## Review Gate

Can the platform explain contractor participation and historical market behavior using only
governed contractor evidence?

## Acceptance Criteria

Program 200 exits only when all of the following are true:

- Program 100 has completed and been certified.
- The Contractor Certified Data Product contract is accepted.
- Contractor business grain, keys, lineage, certification rules, consumer guarantees, and known
  limitations are documented.
- Canonical ContractorEvidence is implemented only after contract acceptance.
- ContractorEvidence preserves certified lineage and exposes diagnostics.
- Contractor Intelligence consumes ContractorEvidence rather than physical contractor storage.
- ContractorContext uses governed business language and identifies evidence, confidence,
  evidence strength, and limitations.
- Every non-empty contractor conclusion references governed ContractorEvidence.
- Missing or insufficient evidence produces governed limitations rather than invented business
  values.
- Project Intelligence integration occurs only after ContractorContext is reviewed and accepted.
- MCP or application output, if later authorized, preserves evidence, lineage, confidence, and
  limitations.
- All required tests and checks pass for the implementing initiatives.

## Non-Goals

Program 200 must not implement or define:

- bid/no-bid recommendations;
- opportunity scoring;
- pursuit portfolio recommendations;
- cost intelligence;
- contractor price prediction;
- AI-generated contractor findings;
- unsupported contractor fields;
- direct application access to physical Contractor relations;
- production Python changes during this planning initiative;
- services, adapters, MCP tools, tests, or CI_DATABASE changes during this planning initiative.
