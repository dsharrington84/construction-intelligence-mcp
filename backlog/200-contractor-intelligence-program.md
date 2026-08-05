# Program 200 — Contractor Intelligence

Status: ACTIVE

Planning state: Program 200 planning is ACTIVE after certification of the Construction Intelligence
Platform v1.0 POC baseline and Program 100 planning progress. Implementation remains dependency-gated
by the accepted Contractor Certified Data Product and certified Contractor Evidence Engine.

## Program Purpose

Program 200 preserves the formal name **Contractor Intelligence** while reframing its business
outcome as **Competitive Market Intelligence**: explain the observable competitive market around a
governed project using certified contractor evidence.

Program 200 is a planning and governance initiative only. It establishes a governed path from
Contractor Processing through a Contractor Certified Data Product and evidence engine into
Contractor Intelligence that can later be consumed by Project Intelligence and applications. It does
not implement Contractor Intelligence, Contractor Evidence, Contractor Certified Data Product
production, services, adapters, MCP tools, runtime commands, tests, or application features.

The Program 200 outcome must help estimators understand contractor participation, repeat bidding,
winning history, competitive history, bidder-count norms, market concentration, district experience,
project-type experience, and observable prime/subcontractor relationships. It must not estimate
cost, recommend whether to bid, assign pursuit scores, predict a definite low bidder, or produce
unsupported predictions.

## Estimator-Facing Business Questions

Program 200 answers these Competitive Market Intelligence questions:

- Who participates in this market?
- Who repeatedly bids similar work?
- Who wins?
- Who is consistently competitive?
- How many bidders typically participate?
- How concentrated is the market?
- What district experience is observable for likely market participants?
- What project-type experience is observable for likely market participants?
- What prime/subcontractor relationships are observable?
- What historical contractor evidence supports each conclusion?
- What confidence, limitations, and lineage apply to the competitive-market view?

Program 200 does not answer:

- What should the project cost?
- Should we bid?
- What is the pursuit score?
- Who will definitely be the low bidder?
- What unsupported predictions can be made about future bidder behavior?

Those questions belong to later governed programs or are explicitly outside platform governance
until accepted contracts authorize them.

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
governance, the certified Construction Intelligence Platform v1.0 POC baseline, Program 100
planning progress, and the accepted platform decision that Certified Data Products form the
contractual boundary between processing and intelligence.

## Constitutional Separation and Information Flow

Program 200 preserves the separation between each governed layer:

```text
Contractor Processing
        ↓
Contractor Certified Data Product
        ↓
Contractor Evidence
        ↓
Contractor Intelligence
        ↓
Project Intelligence
        ↓
Applications
```

- Contractor Processing may produce certified contractor facts, but it does not define downstream
  intelligence contracts for applications.
- The Contractor Certified Data Product is the contract boundary for contractor participation,
  bidding, award, relationship, eligibility, lineage, and limitation facts.
- Contractor Evidence translates only accepted certified contractor facts into canonical,
  traceable evidence objects.
- Contractor Intelligence produces Competitive Market Intelligence from Contractor Evidence and
  must expose support for every material conclusion.
- Project Intelligence may later compose Competitive Market Intelligence with governed project
  context only after the required contracts and implementations are accepted.
- Applications may present Competitive Market Intelligence, but they must not query Contractor
  Processing outputs, physical Contractor relations, or Certified Data Product storage directly.

## Program Architecture

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

- Processing produces governed contractor data when the Contractor Certified Data Product contract
  identifies the producer, certification rules, lineage, and publication guarantees.
- The Contractor Certified Data Product defines the business contract for contractor evidence.
- The Contractor Evidence Engine translates the accepted contract into canonical ContractorEvidence.
- Contractor Intelligence produces Competitive Market Intelligence context from governed evidence.
- Project Intelligence may consume Competitive Market Intelligence only after the evidence and
  intelligence contracts are implemented, certified, and reviewed.
- Applications must not query physical Contractor relations directly.

## Dependencies

| Initiative | Status | Dependency | Unlock condition | Output | Review gate |
|---|---|---|---|---|---|
| 201 Contractor Certified Data Product | READY | Certified v1.0 baseline and Program 100 planning progress | Contract-development work may begin | Pending Contractor Certified Data Product contract | Contract review confirms grain, keys, lineage, certification, consumer guarantees, and limitations |
| 202 Contractor Evidence Engine | BLOCKED_BY_CONTRACT | 201 accepted | Accepted Contractor Certified Data Product makes ContractorEvidence implementation possible | Canonical ContractorEvidence objects and diagnostics | Engine review confirms eligible evidence, lineage preservation, diagnostics, validation, and governed failure behavior |
| 203 Contractor Intelligence | BLOCKED_BY_IMPLEMENTATION | 201 accepted and 202 certified | ContractorEvidence implementation is certified and reviewed | Competitive Market Intelligence context suitable for Project Intelligence consumption | Business review proves competitive-market context uses only governed contractor evidence |

Initiative 201 is READY for contract-development work. Initiative 202 remains BLOCKED_BY_CONTRACT
until 201 is accepted. Initiative 203 remains BLOCKED_BY_IMPLEMENTATION until 201 is accepted and
202 is certified.

## POC Deliverables

The Program 200 POC must define governed deliverables for Competitive Market Intelligence without
implementing production Python in this planning task:

- Market participation profile: identifies observed market participants for a governed project or
  comparable market slice.
- Bidder frequency: summarizes how often contractors bid similar governed work.
- Win frequency: summarizes how often contractors win similar governed work.
- Competitive frequency: summarizes how often contractors are observably competitive under accepted
  evidence rules.
- Bidder-count history: summarizes historical bidder counts for comparable governed work.
- Market concentration: explains whether observed participation and wins are concentrated or
  distributed under accepted concentration rules.
- District experience: summarizes observable contractor participation or wins by district.
- Project-type experience: summarizes observable contractor participation or wins by accepted
  project-type concepts.
- Prime/subcontractor relationship evidence: identifies observable prime/subcontractor
  relationships only when certified evidence supports the relationship.
- Confidence: states the confidence basis for each conclusion using accepted evidence-strength,
  completeness, and lineage rules.
- Limitations: surfaces missing, incomplete, ambiguous, ineligible, or unsupported evidence rather
  than filling gaps with assumptions.
- Lineage: preserves the Certified Data Product, evidence records, source identifiers, and
  transformations required to audit each conclusion.

## Project Intelligence Workspace Placement

After Initiative 201 is accepted, Initiative 202 is certified, and Initiative 203 is accepted,
Program 200 may appear in the Project Intelligence Workspace as a Competitive Market Intelligence
section for a governed project. The future workspace presentation is expected to show:

- a market participation summary;
- repeated bidder and winner history;
- competitive-frequency context;
- typical bidder-count and market-concentration context;
- district and project-type experience summaries;
- prime/subcontractor relationship evidence when governed evidence exists;
- confidence, limitations, and lineage for every material conclusion.

This section describes only future application placement. It does not authorize UI implementation,
application code, services, adapters, MCP tools, runtime commands, tests, or direct warehouse access.
The workspace must consume Project Intelligence outputs and must not bypass Contractor
Intelligence or certified Contractor Evidence.

## Program Review Gate

Can a chief estimator understand the likely competitive market for a governed project using only
certified contractor evidence?

## Acceptance Criteria

Program 200 exits only when all of the following are true:

- The Contractor Certified Data Product contract is accepted.
- Contractor business grain, keys, lineage, certification rules, consumer guarantees, and known
  limitations are documented.
- Canonical ContractorEvidence is implemented only after contract acceptance.
- ContractorEvidence preserves certified lineage and exposes diagnostics.
- Contractor Intelligence consumes ContractorEvidence rather than physical contractor storage.
- Competitive Market Intelligence uses governed business language and identifies evidence,
  confidence, evidence strength, and limitations.
- Every non-empty competitive-market conclusion references governed ContractorEvidence.
- Missing or insufficient evidence produces governed limitations rather than invented business
  values.
- Project Intelligence integration occurs only after Competitive Market Intelligence is reviewed
  and accepted.
- MCP or application output, if later authorized, preserves evidence, lineage, confidence, and
  limitations.
- The Program 200 business review gate succeeds.
- All required tests and checks pass for later implementing initiatives.

## Non-Goals

Program 200 must not implement or define:

- bid/no-bid recommendations;
- opportunity scoring;
- pursuit portfolio recommendations;
- cost intelligence;
- contractor price prediction;
- definite low-bidder prediction;
- AI-generated contractor findings without certified evidence;
- unsupported contractor fields;
- direct application access to physical Contractor relations;
- production Python changes during this planning initiative;
- services, adapters, MCP tools, tests, runtime commands, or CI_DATABASE changes during this
  planning initiative.
