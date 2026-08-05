# Executive Knowledge Certified Data Product

| Field | Value |
|---|---|
| Product name | Executive Knowledge Certified Data Product |
| Product identifier | CDP-001 |
| Version | 0.1 |
| Status | ACCEPTED |
| Layer | Certified Data Product |
| Owner | Construction Intelligence Platform |
| Initial implementation scope | Caltrans executive documents |
| Owner-agnostic contract | Yes |

## 1. Executive Summary

The Executive Knowledge Certified Data Product is the governed business contract for executive-document evidence that future intelligence capabilities may consume. It exists to separate certified evidence from physical warehouse details, static discovery tooling, and downstream reasoning.

This product provides governed executive evidence. It does **not** provide Strategic Context, strategic conclusions, pursuit recommendations, bid/no-bid recommendations, or portfolio decisions.

This Program 100 Initiative 101 contract defines the authoritative Certified Data Product boundary for Executive Intelligence. It incorporates Phase 0 governance and the Executive reverse-engineering artifacts while preserving unresolved implementation facts as limitations rather than inferring them. It is accepted as the storage-independent CDP-001 business contract.

## 2. Constitutional Alignment

CDP-001 directly implements the governance model defined by `docs/000-CONSTITUTION.md`. This contract is the accepted Program 100 Initiative 101 business contract consumed by Initiative 102, the Executive Evidence Engine.

| Principle | CDP-001 alignment |
|---|---|
| Processing creates truth | CDP-001 treats an Executive Processing Pipeline as the only acceptable producer of certified executive evidence. The current repository does not contain that production pipeline, so production truth remains Pending Certification. |
| Certified Data Products preserve truth | CDP-001 defines the preservation contract: stable evidence identity, lineage, status eligibility, semantic metadata boundaries, and consumer guarantees. |
| Intelligence explains truth | Future Executive Evidence and Strategic Context engines may explain certified evidence; they may not invent missing evidence or replace this contract with direct warehouse queries. |
| Applications present intelligence | Applications and dashboards are prohibited direct consumers of this product. They present intelligence produced by approved engines and services, not raw Certified Data Product records. |
| Evidence precedes conclusions | Strategic conclusions and pursuit recommendations are explicitly outside this product. Downstream conclusions must cite eligible ExecutiveEvidence records first. |
| Lineage is mandatory | Every certified evidence object must preserve enough lineage to identify source document, source asset or artifact, page when available, source section, refined section, producing pipeline, source relation, and source key values. |
| Business contracts precede implementation | This document is a contract-first artifact. It intentionally does not implement Strategic Context, adapters, services, warehouse tables, or pipeline redesign. |


## Program Alignment

CDP-001 belongs to **Program 100 — Executive Intelligence** as **Initiative 101 — Executive Certified Data Product**. Its purpose is to establish the contractual boundary consumed by **Initiative 102 — Executive Evidence Engine**. It does not implement Initiative 102 or Initiative 103, and it does not expand into other program domains except to preserve architectural consistency.

## 3. Business Purpose

CDP-001 is Program 100 Initiative 101. It is responsible for defining the owner-agnostic business meaning, eligibility, lineage, and consumer guarantees for governed executive knowledge derived from Caltrans executive documents.

### Owns

- Governed executive knowledge.
- Source-document lineage.
- Source-section lineage.
- Refinement status.
- Certified evidence eligibility.
- Supported semantic metadata.
- Stable consumer guarantees.

### Does not own

- Strategic Context.
- Opportunity assessment.
- Contractor intelligence.
- Cost intelligence.
- Portfolio decisions.
- Bid/no-bid recommendations.
- Application presentation logic.
- Source-document parsing or warehouse construction.
- Direct mutation of `CI_DATABASE`.

## 4. Business Questions Answered

When certified, CDP-001 can answer:

- What governed executive evidence exists?
- Which document produced each evidence object?
- Which source section produced each evidence object?
- What refinement or eligibility status applies?
- Which supported executive concepts are attached?
- What limitations apply to an evidence object?
- Which source relation and source keys support the evidence object?

CDP-001 cannot answer:

- What strategy should a contractor pursue?
- Which opportunities should be bid?
- Which projects belong in a pursuit portfolio?
- Which contractors are likely competitors?
- What costs should be estimated?
- What unsupported semantic concepts would have been present if extraction had succeeded?
- What business meaning should be assigned to fields that only appear as name matches in diagnostics.

## 5. Producer Contract

The business producer is the **Executive Processing Pipeline**, not DuckDB. DuckDB or any successor storage engine is a physical persistence mechanism only.

The current 010B artifact found no production Executive warehouse build pipeline in this repository. The only evidenced flow is inspection of an externally produced Executive DuckDB by diagnostic tools.

| Pipeline area | Evidence-backed finding | Contract status |
|---|---|---|
| Source intake / OCR | No production script found in this checkout. | Pending Certification |
| Section creation | No production script found in this checkout. | Pending Certification |
| Fragment assembly / extraction | No production script found in this checkout. | Pending Certification |
| Refinement | No production script found in this checkout. | Pending Certification |
| Semantic assembly | No semantic-generation code exists in this checkout. | Pending Certification |
| Certification / promotion | No certification metadata, current-row mechanism, aliases/views, or promotion commands were found. | Pending Certification |
| Diagnostic profiling | `scripts/warehouse/reverse_engineer_executive_warehouse.py` profiles an existing DuckDB read-only and writes warehouse JSON inventories. | Diagnostic only |
| Static pipeline scan | `scripts/pipeline/reverse_engineer_executive_pipeline.py` scans repository files and writes pipeline JSON inventories. | Diagnostic only |

### Output relations

No current, certified, staging, candidate, exception, or promotion Executive relation can be named as safe for consumption from the available artifacts. The checked-in warehouse inventories have `evidence_status: not_generated` and empty relation, join, and semantic inventories.

### Current/certified promotion path

No promotion path is evidenced. A Version 1.0 producer contract must identify the certified output relation or view, current-version selection rule, certification checks, and rejection path.

### Versioning behavior

No versioning behavior is evidenced. Versioned relation names without a certified current alias are insufficient for consumers.

### Known pipeline limitations

- The production Executive pipeline is not present in this repository.
- No production relation writes were discovered.
- No semantic-generation transformation is evidenced.
- `governed_finding` is a profiler search term and synthetic test-fixture column only; it is not a certified produced field.

## 6. Consumer Contract

### Approved consumers

The approved direct downstream consumer boundary is **Initiative 102: Executive Evidence Engine**. Strategic Context consumes the `ExecutiveEvidence` consumer contract produced by that engine; it does not consume CDP-001 physical storage or mappings directly. Other intelligence engines may not consume CDP-001 unless a future accepted contract explicitly authorizes that path.

```text
Executive Knowledge Certified Data Product (CDP-001 / Initiative 101)
        |
        v
Executive Evidence Engine (Initiative 102)
        |
        v
Strategic Context Engine / future approved intelligence engines
        |
        v
Applications and dashboards present intelligence only
```

### Prohibited consumers

```text
Applications / dashboards / direct user interfaces
        X
        X  no direct consumption
        X
Executive Knowledge Certified Data Product
```

Prohibited consumers include applications, dashboards, direct end-user interfaces, and ad hoc warehouse queries presented as intelligence.

Consumers depend on the Certified Data Product business contract. Consumers do not depend on DuckDB, relation names, column names, version suffixes, or storage-specific behavior.

## 7. Business Grain

| Grain | Evidence | Status |
|---|---|---|
| Refined executive evidence record | Best-supported target grain because requested keys and lineage require a stable evidence object that can point back to source section and refined section. | Pending Certification |
| Document | Mentioned as a required lineage target, but no certified document relation is available. | Contextual / Pending Certification |
| Page | Required when available, but no certified page relation is available. | Contextual / Pending Certification |
| Source section | Required lineage target, but no certified section relation is available. | Contextual / Pending Certification |
| Refined section | Required lineage target, but no certified refined-section relation is available. | Candidate canonical / Pending Certification |
| Semantic record | Semantic concepts are name evidence only in the current artifacts. | Unsupported for certified consumption |

The **Proposed Canonical Grain — Pending Certification** is: **one ExecutiveEvidence object representing one eligible refined executive evidence record with source-section lineage**.

This grain remains **Pending Certification** until Program 100 review certifies the producer relation, row identity, lineage path, and join cardinalities. It is selected as the contract target because it is the smallest business grain that can preserve source text, refinement status, evidence type, source-section lineage, and semantic metadata without mixing document-level and semantic-record-level facts.

Risks of mixing grains:

- Document-level fields can be incorrectly repeated across unrelated sections.
- Page-level context can be mistaken for section evidence.
- Source sections and refined sections can have one-to-many or many-to-one relationships that are not certified.
- Semantic records can multiply evidence objects if their grain is not controlled.
- Many-to-many joins can create duplicate or falsely reinforced evidence.

## 8. Business Keys

| Key | Business meaning | Producing stage | Grain | Uniqueness | Stability | Lineage role | Classification | Known limitations |
|---|---|---|---|---|---|---|---|---|
| `refined_section_key` | Identifier for a refined section or refined evidence unit. | Refinement stage. | Refined section. | Pending Certification. | Pending Certification. | Links certified evidence to refined section. | Candidate canonical. | No certified source relation or producer found. |
| `source_section_key` | Identifier for the source section that produced evidence. | Section creation stage. | Source section. | Pending Certification. | Pending Certification. | Required source-section lineage key. | Required lineage key. | No certified source relation or producer found. |
| `artifact_id` | Identifier for source artifact or asset-like extraction artifact. | Source intake or artifact creation stage. | Artifact/source asset. | Pending Certification. | Pending Certification. | Connects evidence to source artifact. | Contextual lineage key. | Appears in diagnostics/test fixtures; not certified. |
| `knowledge_record_id` | Identifier for a knowledge record. | Knowledge extraction stage. | Knowledge record. | Pending Certification. | Pending Certification. | Potential bridge between source/refined evidence and semantic metadata. | Alternate/contextual. | No production source or grain certified. |
| `source_asset_id` | Identifier for the source asset. | Source intake stage. | Source asset. | Pending Certification. | Pending Certification. | Identifies the source asset or artifact. | Required lineage concept when available. | Not present as a certified relation/field in current artifacts. |
| `source_document_id` | Identifier for the original source document. | Document registration stage. | Document. | Pending Certification. | Pending Certification. | Required source-document lineage. | Required lineage key. | Not present as a certified relation/field in current artifacts. |
| Document identifiers | Human or system document identifiers such as title, file, version, or source ID. | Document registration stage. | Document. | Pending Certification. | Pending Certification. | Helps identify original source document. | Contextual. | Specific fields are not certified. |
| Page identifiers | Page number or page-level source ID. | Page extraction stage. | Page. | Pending Certification. | Pending Certification. | Locates evidence when page is available. | Contextual. | Page availability is not certified. |
| Section identifiers | Heading, section ID, section key, or section path. | Section creation stage. | Source section. | Pending Certification. | Pending Certification. | Locates source text within document. | Required lineage concept. | Specific fields and uniqueness are not certified. |

No key is fully certified in the Initiative 101 review contract. A key may become canonical only when the producer proves uniqueness, stability, grain, and lineage role.

## 9. Lineage Contract

The certified lineage path must be the path proven by the Executive Processing Pipeline. The current artifacts do not prove a production path, so the path below is the required contract with unavailable stages marked Pending Certification.

```text
Original executive source document
        |
        v
Source asset / artifact                [Pending Certification]
        |
        v
Page, when available                   [Pending Certification]
        |
        v
Source section                         [Pending Certification]
        |
        v
Knowledge record / extracted content    [Pending Certification]
        |
        v
Refined section                         [Pending Certification]
        |
        v
ExecutiveEvidence                       [CDP-001 contract object]
```

Every ExecutiveEvidence object must preserve enough lineage to identify:

- Original source document.
- Source asset or artifact.
- Page when available.
- Source section.
- Refined section.
- Producing pipeline and pipeline version.
- Source relation.
- Source key values.

A lineage edge is not certified by similar names, coincidental value overlap, or a diagnostic profile alone.

## 10. Executive Evidence Business Object

The canonical business object is `ExecutiveEvidence`.

### Required fields

| Field | Meaning | Status |
|---|---|---|
| `evidence_id` | Stable identifier for the evidence object within the certified product version. | Pending Certification |
| `source_document` | Business identifier or descriptor for the original document. | Pending Certification |
| `source_section_id` | Identifier for the source section. | Pending Certification |
| `source_text` or `source_excerpt` | Verbatim or governed excerpt from the source/refined evidence. | Pending Certification |
| `refinement_status` | Status controlling evidence eligibility. | Pending Certification |
| `evidence_type` | Type from the supported evidence-type list. | Pending Certification |
| `source_lineage` | Structured lineage keys and relation identifiers. | Pending Certification |
| `limitations` | Known caveats for use. | Pending Certification |

The object must not require a physical warehouse field named `governed_finding`. Source text must not be renamed as `governed_finding`.

### Optional fields when certified by source artifacts

| Category | Optional concepts |
|---|---|
| Source text | `source_heading`, `source_page`, `source_year`, `source_version`, `document_type`, `section_type` |
| Semantic metadata | `program`, `strategic_theme`, `objective`, `policy_driver`, `expected_outcome`, semantic tags |
| Geography/context | `region`, `district`, `county`, `route` |
| Project/asset context | `project_type`, `asset_category` |
| Refinement context | refinement confidence, source status |

Distinctions:

- Source text is evidence content or excerpted source language.
- Refined metadata describes the refinement process and eligibility status.
- Semantic metadata classifies supported executive concepts.
- Contextual metadata locates or scopes evidence but does not itself create a conclusion.

## 11. Evidence Types

| Evidence type | Business meaning | Producing stage | Eligible use | Limitations |
|---|---|---|---|---|
| `SOURCE_SECTION` | Evidence at the source-section grain. | Section creation. | Supporting or direct evidence when status and source text are certified. | Stage not evidenced in this repository. |
| `REFINED_SECTION` | Refined evidence derived from a source section. | Refinement. | Candidate canonical direct evidence when identity, lineage, status, and text are certified. | Stage not evidenced in this repository. |
| `CONTEXT_SECTION` | Section retained for context rather than direct evidence. | Section creation/refinement. | Contextual evidence only. | Must not be promoted as direct evidence. |
| `TABLE_CONTEXT` | Table-derived context associated with a document or section. | Table extraction/context processing. | Contextual or supporting evidence only when lineage is certified. | No table extraction stage evidenced. |
| `DOCUMENT_CONTEXT` | Document-level context. | Document registration/context processing. | Contextual evidence only. | Risk of over-applying document facts to sections. |
| `SEMANTIC_RECORD` | Semantic metadata record attached to evidence. | Semantic assembly. | Metadata enrichment only when grain and joins are certified. | No semantic-generation code evidenced. |

These types are a **proposed vocabulary** for Program 100 review. None is certified for production consumption until 010A/010B evidence proves the producing stages, grains, lineage, and eligibility behavior.

## 12. Status and Eligibility Contract

The current Executive refinement model has observed status values `USABLE`, `USABLE_WITH_LIMITATION`, `CONTEXT_ONLY`, `REVIEW_REQUIRED`, and `EXCLUDED`. Observation does not equal certification: the meanings, physical source fields, distributions, and enforcement checks remain **Pending Certification** until Program 100 review accepts them. Unknown or additional statuses are not certified.

| Status | Observation status | Certification status | Meaning | Direct evidence | Supporting evidence | Contextual evidence | Exclusion |
|---|---|---|---|---:|---:|---:|---:|
| `USABLE` | Observed | Pending Certification | Evidence is eligible without known limitation when certified. | Yes | Yes | Yes | No |
| `USABLE_WITH_LIMITATION` | Observed | Pending Certification | Evidence is eligible with explicit limitations when certified. | Yes, with limitations | Yes | Yes | No |
| `CONTEXT_ONLY` | Observed | Pending Certification | Evidence provides context but is not direct proof. | No | No | Yes | No |
| `REVIEW_REQUIRED` | Observed | Pending Certification | Evidence requires human or governed review before use. | No | No | No | Yes |
| `EXCLUDED` | Observed | Pending Certification | Evidence is rejected from certified output. | No | No | No | Yes |
| Unknown/additional | Unknown | Not certified | Any status not in the certified vocabulary. | No | No | No | Yes until certified |

Unknown statuses must not be silently classified. They must fail certification or be routed to a governed exception path.

## 13. Certification Rules

An ExecutiveEvidence record is certified for downstream consumption only when all of the following are true:

1. Stable identity is present and unique within the certified product version.
2. Source-document lineage is present.
3. Source-section lineage is present.
4. Status is eligible for the requested use.
5. Evidence content is non-null and non-empty for direct or supporting evidence.
6. Evidence type is valid for the requested use.
7. Source relation and source key values are recorded.
8. There is no unresolved key ambiguity.
9. Joins do not cause uncontrolled many-to-many multiplication.
10. `EXCLUDED`, `REVIEW_REQUIRED`, and unknown statuses cannot leak into certified direct or supporting output.

Explicit rejection conditions:

- Missing evidence identity.
- Missing source document lineage.
- Missing source section lineage.
- Missing or empty evidence content for direct/supporting evidence.
- Unknown evidence type.
- Unknown or ineligible status.
- Ambiguous source key resolution.
- Uncontrolled many-to-many join multiplication.
- Reliance on a diagnostic-only name match as business meaning.
- Physical field rename that converts source text into `governed_finding` without certification.

## 14. Semantic Metadata Contract

No semantic concept has a certified source relation or field in the Initiative 101 review contract. The warehouse semantic map is empty and not generated; 010B found concept occurrences but no producer/transformation/output column contract.

| Concept | Source relation | Source field | Producer | Grain | Coverage | Confidence or limitation | Status |
|---|---|---|---|---|---|---|---|
| Program | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Name evidence only. | Pending Certification |
| Objective | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Name evidence only. | Pending Certification |
| Strategic theme | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Name evidence only. | Pending Certification |
| Policy driver | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Name evidence only. | Pending Certification |
| Expected outcome | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Name evidence only. | Pending Certification |
| Geography | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Name evidence only. | Pending Certification |
| District | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Appears in other project/market contexts, not certified for Executive evidence. | Pending Certification |
| County | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Not certified for Executive evidence. | Pending Certification |
| Route | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Not certified for Executive evidence. | Pending Certification |
| Project linkage | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Unsupported for certified Executive evidence until lineage and grain are proven. | Unsupported / Pending Certification |
| Asset category | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Not certified for Executive evidence. | Pending Certification |
| Time horizon | Pending Certification | Pending Certification | Pending Certification | Pending Certification | Unknown | Not certified for Executive evidence. | Pending Certification |

Unsupported concepts must be null or absent. They must not be invented from document titles, free text, or unrelated project tables.

## 15. Physical Implementation Mapping

Physical storage may change without changing the business contract. Consumers depend on the Certified Data Product contract; they do not depend on DuckDB, relation names, column names, or version suffixes. Schema compatibility and certified lineage take precedence over version suffixes.

| Physical area | Current mapping | Role | Contract rule |
|---|---|---|---|
| Accepted implementation mapping | Supplied explicitly to the Executive Evidence Engine as a schema-qualified relation with CDP-001 product identifier, accepted/current certification status, and certified-current role. | Runtime implementation boundary. | Exactly one accepted/current mapping is required; absence, duplicates, non-schema-qualified relations, missing relations, or prohibited roles must fail governed validation. |
| Configuration source | `CDP001_EXECUTIVE_EVIDENCE_RELATION`, `CDP001_EXECUTIVE_EVIDENCE_STATUS`, and optional `CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE`, or an equivalent application-composition dependency. | Mapping mechanism. | These values identify storage only for adapters; they do not change the storage-independent CDP-001 business contract. |
| Producer scripts | None found for production Executive warehouse materialization in this repository. | Pending producer evidence. | Producer must be the Executive Processing Pipeline, not DuckDB. |
| Diagnostic warehouse profiler | `scripts/warehouse/reverse_engineer_executive_warehouse.py`. | Read-only discovery. | Cannot certify business meaning by itself. |
| Diagnostic pipeline scanner | `scripts/pipeline/reverse_engineer_executive_pipeline.py`. | Static repository scan. | Cannot produce warehouse truth. |
| Supported joins | None certified for multi-relation assembly. | Pending lineage. | Joins require measured overlap, coverage, cardinality, and declared lineage intent. |
| Unsupported/rejected relations | Staging, candidate, history, archive, quarantine, diagnostic, temporary, exception, and name-only relations. | Not consumable. | Exclude unless promoted through an accepted/current CDP-001 implementation mapping with certified-current role. |
| Version selection | Governed by the explicit accepted/current mapping. | Runtime selection rule. | Consumers must not choose by latest suffix or relation-name similarity. |

### Runtime Mapping Boundary

The CDP-001 business contract remains independent of DuckDB schemas and table names. The
Executive Evidence Engine may use physical storage only after application composition supplies
exactly one accepted/current implementation mapping for product `CDP-001`. The mapping must name a
schema-qualified relation and a non-prohibited certified-current role. The adapter validates that
relation exists and that the required ExecutiveEvidence concepts resolve before projecting
canonical evidence rows. Relation-name similarity is never certification evidence.

## 16. Consumer Guarantees

When CDP-001 reaches certification through the Program 100 review gate, the Executive Evidence Engine may safely assume:

- Evidence IDs are stable within the certified product version.
- Source-document lineage is preserved.
- Source-section lineage is preserved.
- Status eligibility is governed.
- Unsupported concepts are null or absent, not invented.
- Physical relation names are not part of the consumer contract.
- Direct evidence excludes `EXCLUDED`, `REVIEW_REQUIRED`, and unknown statuses.
- Every exposed limitation travels with the evidence object.

Consumers may not assume:

- A physical table name is stable.
- A version suffix identifies the certified current relation.
- Name-matched columns are semantically certified.
- Document-level facts apply to every section.
- Semantic metadata is complete.
- Project linkage exists.
- Context-only evidence supports a strategic conclusion by itself.
- Missing values can be inferred from unrelated fields.

## 17. Known Limitations

- The Executive Warehouse was unavailable for 010A; relation, join, semantic, ERD, topology, and lineage evidence are not generated.
- 010B found no production Executive warehouse build pipeline in this repository.
- No current or certified Executive relation is identified.
- Canonical business grain is unresolved and Pending Certification.
- Canonical evidence identity is unresolved and Pending Certification.
- Source-text coverage is unknown.
- Semantic coverage is incomplete/unknown.
- Producer and transformation stages are not evidenced.
- Document, page, section, refined-section, and semantic-record grains cannot be safely joined from current evidence.
- Context-only evidence is defined by contract but not observed in data.
- Project linkage is unsupported for certified Executive evidence.
- Versioned relations without a formal current alias are not safe for consumption.
- `governed_finding` is not a certified field or semantic equivalent.

## 18. Pending Certification

| Question | Why it matters | Evidence currently available | Required next action | Owner / initiative |
|---|---|---|---|---|
| What is the canonical certified output relation or view? | Consumers need one governed source of evidence. | No certified relation inventory. | Run 010A against the Executive warehouse and obtain owner certification metadata. | Executive Processing Pipeline / CDP-001 certification |
| What is the canonical business grain? | Prevents duplicate evidence and false many-to-many multiplication. | Contract target is refined evidence record, but not proven. | Certify relation grain, row identity, and join cardinalities. | CDP-001 certification |
| What is the canonical evidence identity? | Required for stable consumer references. | Candidate keys named in task; none certified. | Prove uniqueness and stability for `evidence_id` or `refined_section_key`. | Executive Processing Pipeline |
| Which fields carry source text or excerpt? | Direct evidence requires non-null content. | `governed_finding` is not certified; source text fields are unresolved. | Certify source-text field, null behavior, and excerpt rules. | Executive Processing Pipeline |
| Which lineage keys identify document and source section? | Evidence without lineage cannot support conclusions. | Required concepts are documented, but no certified source fields. | Certify source-document and source-section keys and lineage path. | Executive Processing Pipeline |
| Which observed statuses are certified and how are they enforced? | Eligibility depends on governed status meanings and rejection behavior. | `USABLE`, `USABLE_WITH_LIMITATION`, `CONTEXT_ONLY`, `REVIEW_REQUIRED`, and `EXCLUDED` are observed in the current Executive refinement model. | Certify source fields, observed distributions, enforcement checks, and exception handling. | Program 100 Initiative 101 review |
| Which semantic concepts are supported? | Prevents invented metadata. | Name evidence only; semantic map not generated. | Certify source relation, field, grain, coverage, and limitations per concept. | Executive Processing Pipeline |
| How is current/certified promotion performed? | Consumers must avoid staging/candidate data. | No promotion command or metadata found. | Define and implement certification command and current alias/rule. | Executive Processing Pipeline |
| Is actual `CI_DATABASE` evidence population nonzero? | Certified product must expose real evidence. | No database was available to 010A. | Validate against configured `CI_DATABASE` read-only. | CDP-001 certification |

## 19. Acceptance Criteria for Version 1.0

CDP-001 may move from IN REVIEW to Certified 1.0 only after the Program 100 review gate confirms all criteria are met:

- Canonical business grain is certified.
- Canonical evidence identity is certified.
- Source-text contract is certified.
- Source-document lineage is certified.
- Source-section lineage is certified.
- Status eligibility is certified with observed values and distributions.
- Semantic metadata contract is certified for each supported concept.
- Consumer guarantees are validated by automated checks.
- Certification command is implemented.
- Actual `CI_DATABASE` evidence population is nonzero.
- `EXCLUDED`, `REVIEW_REQUIRED`, and unknown-status evidence cannot enter certified direct or supporting output.
- Current/certified promotion path is documented and tested.
- Version-selection rule is explicit and does not rely on suffix guessing.
- Many-to-many join multiplication is controlled or rejected.
- Unsupported concepts remain null or absent.

## 20. Recommended Next Initiative

The recommended next initiative is the **Executive Evidence Engine**.

Initiative 102 consumes the CDP-001 business contract, returns ExecutiveEvidence business objects, exposes lineage and limitations, and rejects uncertified or ineligible evidence. Runtime access is through exactly one explicit accepted/current schema-qualified physical implementation mapping; the mapping is not the business contract. The engine must not implement Strategic Context, make pursuit recommendations, or query physical Executive warehouse tables outside the certified contract.
