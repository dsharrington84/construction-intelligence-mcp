# 201 — Contractor Certified Data Product

Status: BLOCKED

Dependency: Program 100 certified.

## Purpose

Develop the discovery evidence and contract required to accept the governed Contractor Certified
Data Product.

This initiative is a contract-development initiative only. It may inspect repository code,
schemas, scripts, research artifacts, and documented warehouse evidence, but it must not implement
the Contractor Certified Data Product. It must not modify production Python, create a DuckDB
adapter, create `ContractorEvidence`, modify MCP, create warehouse objects, or treat physical
relations as certified business contracts.

## Constitutional Alignment

Initiative 201 belongs to Program 200 — Contractor Intelligence. Its Certified Data Product target
is the future Contractor Certified Data Product, provisionally identified as CDP-002 until accepted
by contract review.

The initiative aligns with the Constitution by keeping certification ahead of implementation:
Processing Pipelines create truth, Certified Data Products preserve truth, Intelligence consumes
certified business contracts, and Applications must not depend on processing internals or physical
warehouse structures. Any warehouse relation, column, script, or diagnostic artifact discovered by
this initiative is evidence for review only; it is not certified until the CDP-002 contract is
accepted.

## Scope Boundary

### In scope

- Read-only inspection of repository code, schemas, scripts, documentation, research artifacts, and
  documented warehouse evidence.
- Discovery task design for candidate contractor warehouse relations and processing lineage.
- Contract-development task design for contractor business grain, keys, identity, participation,
  bid facts, prime/subcontractor relationships, lineage, eligibility, certification, limitations,
  and consumer guarantees.
- Explicit documentation of unresolved concepts.

### Out of scope

- Implementing the Contractor Certified Data Product.
- Modifying production Python.
- Creating a contractor adapter.
- Creating `ContractorEvidence`.
- Modifying MCP tools or transport.
- Creating services, models, tests, warehouse objects, scripts, migrations, or application behavior.
- Certifying a physical DuckDB relation, table, view, file, or diagnostic artifact by name.
- Inferring missing contractor facts from similar names, partial schemas, or convenience joins.

## Current Evidence State

No Contractor Certified Data Product is accepted. No contractor business grain, canonical key,
lineage path, eligibility rule, current relation, or certified source relation is known from this
initiative document. Every desired contractor concept remains unresolved until Initiative 201 tasks
produce reviewed evidence and the CDP-002 contract is accepted.

## Required CDP-002 Contract Topics

The eventual Contractor Certified Data Product contract must address all of the following topics.
Each topic remains unresolved until the associated discovery task produces reviewed evidence:

| Topic | Current status | Required resolution before acceptance |
|---|---|---|
| Business grain | Unresolved | Define the accepted row/object grain and any supported aggregate grains. |
| Business keys | Unresolved | Identify stable contract, contractor, bidder, bid, subcontractor, source-document, and lineage keys when available. |
| Contractor identity | Unresolved | Define canonical identity, normalization, duplicates, conflicts, missing IDs, and historical changes. |
| Participation | Unresolved | Define what qualifies as participation and how prime, bidder, winner, and subcontractor participation differ. |
| Ranked and unranked bids | Unresolved | Define rank semantics, missing-rank handling, and whether unranked bids are eligible evidence. |
| Winner determination | Unresolved | Define source of truth for winning bidder and conflict handling. |
| Bid amount | Unresolved | Define amount type, currency/units, null behavior, and eligibility. |
| Bid date | Unresolved | Define canonical bid date and how it differs from advertisement, opening, award, and contract dates. |
| District | Unresolved | Define district source, normalization, and coverage expectations. |
| Project type | Unresolved | Define project type source, vocabulary, and unresolved/null behavior. |
| Prime/subcontractor relationships | Unresolved | Define relationship grain, role, time/version semantics, and lineage. |
| Lineage | Unresolved | Define relation, row, source-document, and processing provenance required for each material fact. |
| Eligibility | Unresolved | Define eligible, ineligible, rejected, quarantined, historical, and context-only states. |
| Certification status | Unresolved | Define accepted/current status metadata and promotion or mapping requirements. |
| Limitations | Unresolved | Define known limitations and how consumers must expose them. |
| Consumer guarantees | Unresolved | Define what future evidence and intelligence consumers may rely on and required governed failure behavior. |

## Task Backlog

### 201A — Contractor warehouse inventory

**Purpose**

Produce a read-only inventory of candidate warehouse relations and fields that may support the
Contractor Certified Data Product contract, without certifying any physical relation.

**Inputs**

- `docs/000-CONSTITUTION.md`.
- `AGENTS.md`.
- `docs/PROGRAMS.md`.
- `docs/DECISIONS.md`.
- `backlog/200-contractor-intelligence-program.md`.
- `backlog/201-contractor-certified-data-product.md`.
- `docs/data-products/100-executive-certified-data-product.md` as the accepted CDP contract pattern.
- `docs/research/` for research-artifact conventions and evidence-state discipline.
- `src/construction_intelligence_mcp/adapters/` and `src/construction_intelligence_mcp/services/` for current architectural boundaries.
- Read-only warehouse catalog/schema evidence when available.
- Any checked-in schema, SQL, pipeline, or diagnostic evidence relevant to contractor, bidder, bid,
  award, subcontractor, source-document, or lineage concepts.

**Outputs**

- Candidate relation inventory that identifies, at minimum, candidate locations for:
  - contract identifiers;
  - contractor identities;
  - bidder identities;
  - bid rank;
  - bid amount;
  - bid status;
  - winning bidder;
  - district;
  - project type;
  - bid date;
  - subcontractor identities;
  - prime/sub relationships;
  - source documents;
  - lineage keys.
- For every candidate relation/field: schema-qualified physical name when available, evidence
  source, row count when safely measurable, null coverage when safely measurable, representative
  bounded examples when permitted, and certification status of the observation as `candidate`,
  `diagnostic`, `unresolved`, or `rejected`.
- Explicit list of concepts with no candidate evidence.
- Explicit warning that candidate relations are not CDP-002 certified.

**Dependencies**

- Program 100 must be certified before CDP-002 can be accepted, but this discovery task may be
  prepared while Program 200 remains blocked.
- Requires read-only access to any available warehouse or documented schema evidence.
- Must preserve adapter-only SQL boundaries if any future discovery script is proposed; this task
  itself does not authorize implementation.

**Exact non-goals**

- Do not implement a contractor adapter, service, model, MCP tool, warehouse object, or test.
- Do not modify production Python.
- Do not name any candidate physical relation as accepted or certified.
- Do not infer business meaning from relation or column names alone.
- Do not mutate the DuckDB warehouse or source data.

**Review gate**

A reviewer can trace every candidate contractor concept to specific read-only evidence and can see
which requested concepts remain unresolved, with no physical relation promoted to certified status.

**Acceptance criteria**

- Inventory covers every required concept listed in this task or marks it unresolved.
- Each candidate relation and field has evidence provenance and diagnostic/candidate status.
- Missing concepts are explicit and not substituted with unrelated fields.
- No production code or warehouse data is modified.
- The artifact states that the inventory is research evidence, not the CDP-002 contract.

**Proposed artifact path**

- `docs/research/201A-contractor-warehouse-inventory.md`

### 201B — Contractor identity and key audit

**Purpose**

Determine the identity and key rules required before contractor and bidder facts can be governed.

**Inputs**

- Accepted output from 201A.
- Candidate contractor, bidder, vendor, license, awardee, subcontractor, and source-document fields.
- Any documented source-system identity rules, warehouse constraints, dictionaries, lookup tables,
  or lineage metadata.
- Representative values and coverage measurements collected read-only.

**Outputs**

- Candidate canonical contractor key analysis.
- Candidate canonical bidder key analysis.
- License/vendor identifier inventory and coverage.
- Name normalization rule findings, including case, punctuation, suffix, joint venture, DBA,
  spacing, abbreviation, and legal-entity handling when evidenced.
- Duplicate identity findings.
- Conflicting identity findings.
- Missing identifier findings.
- Historical identity-change findings, including whether keys are stable over time.
- Recommendation for which identity concepts are contract-ready, blocked, or unresolved.

**Dependencies**

- Depends on 201A candidate relation and field evidence.
- Requires enough representative and aggregate evidence to distinguish stable business keys from
  display names and processing-local IDs.

**Exact non-goals**

- Do not create a contractor identity resolver.
- Do not implement normalization logic.
- Do not merge identities, deduplicate warehouse rows, or correct source data.
- Do not declare a key canonical unless evidence supports stability, uniqueness, lineage, and
  business meaning.

**Review gate**

A reviewer can decide whether contractor and bidder identities are stable enough for CDP-002, or
which identity gaps block acceptance.

**Acceptance criteria**

- Canonical contractor key is accepted, rejected, or explicitly unresolved.
- Canonical bidder key is accepted, rejected, or explicitly unresolved.
- License/vendor identifiers and name fields have coverage and conflict evidence where available.
- Duplicate, conflicting, missing, and historical identity cases are documented.
- The artifact distinguishes business keys from physical row IDs and display names.

**Proposed artifact path**

- `docs/research/201B-contractor-identity-key-audit.md`

### 201C — Participation and performance grain audit

**Purpose**

Determine which contractor participation and performance grains are valid, measurable, and safe to
contract before any ContractorEvidence implementation.

**Inputs**

- Accepted outputs from 201A and 201B.
- Candidate bid, award, contract, district, project type, subcontractor, time, and lineage fields.
- Any documented bid ranking, award, winner, subcontracting, and performance semantics.
- Read-only aggregate measurements for distinct counts, duplicate rates, null rates, and candidate
  key cardinality where available.

**Outputs**

- Grain audit for:
  - contractor;
  - contractor × contract;
  - bidder × contract;
  - contractor × district;
  - contractor × project type;
  - prime × subcontractor;
  - contractor × time period.
- For each grain: candidate key set, expected cardinality, duplicate evidence, null behavior,
  eligible fact types, unsupported fact types, and unresolved questions.
- Distinction between participation facts and performance facts.
- Analysis of ranked bids, unranked bids, bid status, winner determination, bid amount, bid date,
  district, and project type at each supported grain.

**Dependencies**

- Depends on 201A for field availability and 201B for identity/key viability.
- Winner, bid rank, and bid amount grains depend on evidence that these fields share a valid
  contract/bidder relationship.

**Exact non-goals**

- Do not compute contractor performance metrics for production use.
- Do not build ContractorEvidence or ContractorContext.
- Do not create scores, rankings, recommendations, or predictive signals.
- Do not collapse unsupported grains into approximate aggregates.

**Review gate**

A reviewer can identify which grains are contract-ready and which grains remain blocked by missing
keys, ambiguous identity, inadequate lineage, or missing business semantics.

**Acceptance criteria**

- Every required grain is accepted, rejected, or explicitly unresolved.
- Ranked and unranked bid handling is documented as accepted, rejected, or unresolved.
- Winner determination has an evidenced source of truth or is marked unresolved.
- Bid amount, bid date, district, project type, and prime/subcontractor relationship availability
  are documented at the relevant grains.
- No performance measure is proposed without an accepted grain and lineage path.

**Proposed artifact path**

- `docs/research/201C-contractor-participation-performance-grain-audit.md`

### 201D — Lineage and certification audit

**Purpose**

Determine whether contractor facts can be traced to certified sources and whether certification,
current-versus-historical, exclusion, and quarantine rules are sufficient for CDP-002 acceptance.

**Inputs**

- Accepted outputs from 201A, 201B, and 201C.
- Candidate source-document fields and document inventories.
- Candidate pipeline metadata, build manifests, relation roles, status fields, current-row markers,
  version fields, rejected/quarantined data evidence, and source-key fields.
- `docs/research/` conventions for keeping diagnostic research separate from accepted contracts.

**Outputs**

- Certified source relation analysis, explicitly distinguishing certified, current, historical,
  staging, candidate, diagnostic, rejected, and unknown relation roles when evidenced.
- Processing lineage map from source documents or source systems through candidate warehouse
  outputs, including unresolved or unverifiable edges.
- Row provenance requirements and available keys.
- Source-document traceability analysis.
- Exclusion rules and eligibility analysis.
- Rejected/quarantined data inventory when available.
- Current versus historical relation analysis and current-row selection requirements.
- Certification gaps that must be closed before CDP-002 acceptance.

**Dependencies**

- Depends on 201A relation inventory and 201C grain audit.
- Depends on 201B if identity lineage is required to support contractor/bidder facts.
- Requires warehouse-owner or processing-pipeline evidence for certification claims; name matches
  and diagnostic profiles are insufficient.

**Exact non-goals**

- Do not certify any relation from repository inspection alone.
- Do not create certification metadata or promotion code.
- Do not repair lineage, rejected data, or quarantined records.
- Do not infer current rows from newest dates unless the producer contract defines that rule.

**Review gate**

A reviewer can verify whether every material contractor fact has adequate lineage and whether any
certification, eligibility, or historical/current ambiguity blocks CDP-002.

**Acceptance criteria**

- Certified source relations are either evidenced or explicitly unresolved.
- Processing lineage and row provenance are documented with unresolved edges clearly marked.
- Source-document traceability is accepted, rejected, or unresolved.
- Exclusion, rejected/quarantined, and eligibility rules are evidenced or unresolved.
- Current versus historical relation handling is evidenced or unresolved.
- No candidate relation is labelled certified without owner-backed certification evidence.

**Proposed artifact path**

- `docs/research/201D-contractor-lineage-certification-audit.md`

### 201E — Contractor CDP contract draft

**Purpose**

Draft the CDP-002 business contract using reviewed discovery evidence while preserving unresolved
concepts and avoiding acceptance of uncertified physical relations.

**Inputs**

- Accepted outputs from 201A, 201B, 201C, and 201D.
- `docs/data-products/100-executive-certified-data-product.md` as a formatting and governance
  precedent, not as a contractor fact source.
- Program 200 roadmap and Constitution.
- Any accepted decision records relevant to Certified Data Product boundaries.

**Outputs**

- Draft Contractor Certified Data Product contract for CDP-002.
- Candidate business concepts for contractor identity, bidder identity, participation, ranked and
  unranked bids, winner determination, bid amount, bid date, district, project type,
  prime/subcontractor relationships, lineage, eligibility, certification status, limitations, and
  consumer guarantees.
- Explicit `Pending Contract`, `Pending Certification`, `Unsupported`, or `Accepted Candidate`
  status for each business concept.
- Proposed consumer contract for future Initiative 202 Contractor Evidence Engine.
- Explicit prohibition on direct consumer dependence on physical relations.

**Dependencies**

- Depends on 201A through 201D accepted research artifacts.
- Program 100 certification remains the roadmap dependency before final CDP-002 acceptance.
- Requires governance review before Initiative 202 can become ready.

**Exact non-goals**

- Do not implement the contract in code.
- Do not create or modify adapters, services, models, MCP, or tests.
- Do not name uncertified physical relations as accepted implementation mappings.
- Do not resolve unsupported concepts by inventing values or approximate substitutions.

**Review gate**

A reviewer can evaluate the draft contract in business language and verify that all unsupported or
unresolved concepts remain explicit rather than hidden behind implementation assumptions.

**Acceptance criteria**

- Draft addresses every required CDP-002 contract topic.
- Draft identifies accepted, pending, unsupported, and unresolved concepts separately.
- Draft defines candidate business grain and keys only to the extent supported by reviewed
  evidence.
- Draft defines eligibility, certification, lineage, limitations, and consumer guarantees.
- Draft does not certify physical relation names or direct storage dependencies.

**Proposed artifact path**

- `docs/data-products/201-contractor-certified-data-product-draft.md`

### 201F — Contract review and acceptance gate

**Purpose**

Define the evidence, tests, and governance review required before CDP-002 can be accepted and
Initiative 202 can begin.

**Inputs**

- Draft CDP-002 contract from 201E.
- Research artifacts from 201A through 201D.
- Program 200 roadmap.
- Constitution and decision records.
- Any owner-provided certification evidence, mapping evidence, or source-system documentation.

**Outputs**

- CDP-002 review checklist.
- Required evidence package for acceptance.
- Required validation tests to be implemented only in the future task that accepts or implements
  the contract, not in this planning task.
- Acceptance gate decision record or contract status update plan.
- Explicit unlock criteria for Initiative 202.

**Dependencies**

- Depends on 201E draft contract.
- Depends on Program 100 certification before final acceptance.
- Requires reviewer confirmation that unresolved concepts do not block or are listed as accepted
  limitations with governed failure behavior.

**Exact non-goals**

- Do not run or implement production ContractorEvidence tests in this planning task.
- Do not implement Initiative 202.
- Do not create MCP exposure.
- Do not accept CDP-002 without the required evidence package and review.

**Review gate**

CDP-002 can be accepted only if reviewers confirm that the contract is storage-independent,
evidence-backed, lineage-preserving, explicit about limitations, and sufficient for a future
Contractor Evidence Engine to fail clearly when required concepts are unavailable.

**Acceptance criteria**

- Review checklist covers business grain, keys, identity, participation, bids, winner, amounts,
  dates, district, project type, prime/subcontractor relationships, lineage, eligibility,
  certification status, limitations, and consumer guarantees.
- Required tests include successful evidence selection, governed failure for missing required
  concepts, identity conflict handling, duplicate handling, rejected/quarantined exclusion,
  current-versus-historical behavior, source-document lineage, and consumer guarantee validation.
- Required evidence package identifies source relations, source keys, producer/certification
  ownership, quality measurements, unresolved concepts, and known limitations.
- Initiative 202 remains blocked unless CDP-002 is accepted.
- No physical relation is accepted as certified without explicit mapping and certification evidence.

**Proposed artifact path**

- `docs/data-products/201F-contractor-cdp-review-checklist.md`

## Initiative 201 Definition of Done

Initiative 201 is complete only when:

- Program 100 is certified.
- Tasks 201A through 201F have accepted artifacts.
- CDP-002 exists as an accepted Contractor Certified Data Product contract.
- The contract decomposes contractor participation and historical market behavior into governed
  business concepts.
- Every unresolved business concept is explicit.
- No physical relation is falsely certified.
- Future ContractorEvidence implementation has a sufficient accepted business contract.
- Initiative 202 is unlocked only by contract acceptance, not by diagnostic discovery.

## Current Blockers and Limitations

- Program 200 remains blocked until Program 100 completes its review gate.
- CDP-002 is not accepted.
- Contractor warehouse inventory is not complete.
- Contractor identity and keys are unresolved.
- Participation and performance grains are unresolved.
- Lineage and certification evidence is unresolved.
- Eligibility, current/historical handling, rejected/quarantined data, and consumer guarantees are
  unresolved.
- No ContractorEvidence or ContractorContext implementation is authorized by this initiative.
