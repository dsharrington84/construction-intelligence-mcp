# Operational Runtime Contract

## 1. Purpose

This document defines the operational runtime prerequisites required to execute Program 100 Business Certification for the Construction Intelligence Platform. It governs how the platform is configured at execution time so certified business contracts can be consumed safely, repeatably, and with explainable failure behavior.

Runtime configuration is separate from business contracts. The Constitution establishes that Certified Data Products, Business Contracts, evidence requirements, and lineage requirements govern platform meaning. Runtime configuration identifies the physical, environment-specific resources that implement those contracts for a particular execution. A runtime value can point to an accepted implementation, but it cannot redefine the Certified Data Product, weaken a Business Contract, or certify business meaning by itself.

This contract supports Program 100 and CDP-001 Executive Certified Data Product execution only within constitutional boundaries. It does not authorize applications, MCP tools, services, or diagnostics to bypass the Intelligence Layer, infer missing facts, or consume physical warehouse structures as business contracts.

## 2. Runtime Architecture

Program 100 runtime execution follows this governed operational path:

```text
Construction Intelligence Platform
        ↓
Runtime Configuration
        ↓
Certified Data Products
        ↓
Evidence Engines
        ↓
Intelligence
        ↓
Applications
```

The Construction Intelligence Platform remains governed by the Constitution and Program roadmap. Runtime Configuration supplies environment-specific values, such as the database path and accepted/current Executive evidence relation. Certified Data Products define the business-ready contract that the runtime values must implement. Evidence Engines validate the runtime mapping and project certified rows into governed evidence objects. Intelligence consumes those evidence objects to produce explainable business context. Applications consume the Intelligence Layer rather than querying physical storage directly.

Runtime configuration is therefore an operational prerequisite, not an architectural authority. If runtime configuration conflicts with the Constitution, CDP-001, Program 100, or accepted decision records, execution must fail rather than adapting around the conflict.

## 3. Required Environment Variables

### `CI_DATABASE`

| Field | Contract |
|---|---|
| Purpose | Identifies the DuckDB database file containing the certified physical implementations used by Construction Intelligence runtime adapters. |
| Required | Yes for Program 100 certification and any runtime path that reads certified Executive evidence. |
| Example | `CI_DATABASE=/mnt/c/Users/dshar/Desktop/Caltrans_Pricing_Data/database/caltrans_pricing.duckdb` |
| Validation | The value must be present, non-empty, resolve to an existing filesystem path, and open as a readable DuckDB database through read-only runtime access. |
| Failure Behavior | Missing, empty, nonexistent, inaccessible, or unreadable database values must produce a governed runtime error that names the failed prerequisite without substituting another database path. |

### `CDP001_EXECUTIVE_EVIDENCE_RELATION`

| Field | Contract |
|---|---|
| Purpose | Identifies the accepted/current schema-qualified physical relation that implements CDP-001 ExecutiveEvidence for this runtime. The relation is an implementation mapping, not the CDP-001 business contract. |
| Required | Yes for Program 100 certification and Executive Evidence Engine execution. |
| Example | `CDP001_EXECUTIVE_EVIDENCE_RELATION=executive.certified_executive_evidence_current` |
| Validation | The value must be present, non-empty, schema-qualified, mapped to CDP-001, and resolvable in `CI_DATABASE`. Relation-name similarity, latest suffixes, staging names, candidates, history, archives, diagnostics, temporary objects, quarantine objects, and exception objects are not valid substitutes. |
| Failure Behavior | Missing, unqualified, ambiguous, prohibited, or nonexistent relations must fail governed validation. Runtime must not search for similar table names or choose a relation by version suffix. |

### `CDP001_EXECUTIVE_EVIDENCE_STATUS`

| Field | Contract |
|---|---|
| Purpose | Declares the certification status of the configured CDP-001 Executive evidence implementation mapping. |
| Required | Yes for Program 100 certification and Executive Evidence Engine execution. |
| Example | `CDP001_EXECUTIVE_EVIDENCE_STATUS=accepted_current` |
| Validation | The value must identify an accepted/current mapping status recognized by the CDP-001 runtime contract. It must not indicate draft, staging, candidate, review-only, archived, expired, diagnostic, or otherwise uncertified runtime use. |
| Failure Behavior | Missing, unknown, stale, non-current, or non-accepted statuses must fail governed validation before evidence rows are consumed. Runtime must not downgrade certification requirements to continue execution. |

### `CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE`

| Field | Contract |
|---|---|
| Purpose | Declares the role of the configured relation in the CDP-001 runtime mapping so adapters can reject prohibited implementation roles. |
| Required | Yes when the runtime composition distinguishes relation roles; otherwise the composition must provide an equivalent governed role assertion. |
| Example | `CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE=certified_current` |
| Validation | The value must identify a certified-current consumption role and must not identify staging, candidate, history, archive, quarantine, diagnostic, temporary, exception, or name-only relations. |
| Failure Behavior | Missing required role assertions, unknown roles, or prohibited roles must fail governed validation. Runtime must not reinterpret an implementation role from the relation name alone. |

## 4. Runtime Validation Rules

Program 100 Business Certification requires all runtime validation rules below to pass before intelligence execution can be treated as certified.

1. **Database exists** — `CI_DATABASE` must resolve to an existing database file. A missing file is a runtime failure, not an empty certified product.
2. **DuckDB readable** — the configured database must open through read-only DuckDB access. Failure to open or read the database must stop execution.
3. **Relation schema-qualified** — `CDP001_EXECUTIVE_EVIDENCE_RELATION` must include an explicit schema and relation name. Unqualified names are not accepted because they obscure lineage and mapping intent.
4. **Mapping accepted/current** — the configured relation status and role must prove exactly one accepted/current CDP-001 implementation mapping. Draft, stale, duplicate, candidate, staging, diagnostic, or name-matched mappings are invalid.
5. **Relation exists** — the schema-qualified relation must exist in `CI_DATABASE`. Runtime must not substitute another relation if the configured relation is absent.
6. **Required concepts resolve** — the relation must resolve every required ExecutiveEvidence business concept defined by CDP-001, including stable evidence identity, source-document lineage, source-section lineage, eligible status, evidence content for direct or supporting evidence, evidence type, source relation, and source key values.
7. **ExecutiveEvidence returns rows** — Program 100 Business Certification requires nonzero eligible ExecutiveEvidence rows from the accepted/current mapping. Zero rows may be a valid operational result for some diagnostic calls, but it does not satisfy Program 100 Business Certification.

## 5. Failure Philosophy

Runtime failures must favor governed failure over convenience. A failed runtime prerequisite means the platform cannot safely prove that the execution is using certified data and preserving business meaning.

Runtime failures must:

- never invent data;
- never infer missing business values from unrelated fields;
- never silently continue after a failed prerequisite;
- never choose alternate physical relations by name similarity, latest suffix, or convenience;
- always produce governed error messages that identify the failed prerequisite and the affected contract;
- always preserve constitutional boundaries between Processing Pipelines, Certified Data Products, Intelligence, and Applications;
- always protect evidence, lineage, and explainability from ambiguous or uncertified runtime state.

A runtime error is preferable to an unexplained answer, an invented conclusion, or an application-visible result that cannot be traced to a certified product.

## 6. Business Certification Requirements

Program 100 Business Certification requires a valid runtime plus governed business outputs. Runtime validation is necessary but not sufficient; it proves the platform is connected to the correct accepted/current implementation, while business certification proves that the resulting intelligence satisfies Program 100 review criteria.

Program 100 certification requires:

- **Valid runtime** — all environment variables and runtime validation rules in this contract pass.
- **Executive Evidence** — canonical ExecutiveEvidence objects are produced from CDP-001 through the Executive Evidence Engine, with ineligible statuses excluded.
- **Strategic Context** — Strategic Context consumes governed ExecutiveEvidence rather than physical warehouse tables and explains why Caltrans is investing in a project.
- **Project Intelligence** — Project Intelligence integrates Strategic Context without bypassing ProjectService or the governed evidence path.
- **Southern California demonstration** — at least one Southern California project receives explainable context from eligible Executive evidence.
- **Explainability** — every conclusion exposes supporting evidence and limitations; empty or `NONE` results remain valid when no defensible evidence exists.
- **Lineage** — every material fact preserves the Certified Data Product basis, source-document lineage, source-section lineage, and source relation/key diagnostics required by CDP-001.

## 7. Future Programs

Programs 200 and higher inherit this Operational Runtime Contract unless a future governed decision records a stricter or program-specific extension. Future programs may add certified data products, evidence engines, environment variables, and validation rules, but they may not weaken the baseline runtime philosophy defined here.

No program may bypass runtime validation. No application, service, MCP tool, adapter, CLI, diagnostic, or future API may treat uncertified physical storage as a business contract, silently substitute missing runtime configuration, or consume Certified Data Products without validating the accepted/current implementation mapping required for that program.
