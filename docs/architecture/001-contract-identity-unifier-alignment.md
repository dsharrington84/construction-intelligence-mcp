# Contract Identity Unifier — Constitutional Alignment Review

Status: **BLOCKED_BY_CONTRACT**

Date: 2026-08-07

## Requested Initial Scope

The requested unifier would establish one canonical contract identity spine across Executive,
Cost History, and Bid-Tab evidence. Its intended first boundary is:

- join only governed warehouse interfaces;
- preserve each warehouse's eligibility and quarantine state without promoting or collapsing it;
- report coverage by district, year, and warehouse;
- restrict competition analysis to the 249 contracts certified for that use;
- prohibit full bid-item matrix analysis while the applicable certification reports zero complete
  matrices;
- keep the nine Cost History contracts with conflicting dates out of date-dependent analysis;
- produce reconciliation totals and explicit unmatched-contract rosters; and
- remain read-only, with no MCP transport or user-interface work.

These constraints are recorded as requested boundaries, not as independently verified certification
facts. In particular, the counts of 249, zero, and nine require accepted Certified Data Product
contracts and mappings before an implementation may rely on them.

## Program Identification

This scope crosses three current programs:

- **Program 100 — Executive Intelligence**, whose Executive Certified Data Product is accepted.
- **Program 200 — Contractor Intelligence**, which owns competition evidence but whose Contractor
  Certified Data Product is only ready for contract development.
- **Program 300 — Cost & Opportunity Intelligence**, which owns Cost History and bid-item cost use
  but is blocked, including its Cost Certified Data Product.

The canonical spine is therefore a cross-program intelligence prerequisite. It cannot be assigned
solely to Program 100 merely because Executive evidence is one input.

## Certified Data Product Identification

The repository currently contains one accepted relevant contract:

- **CDP-001 — Executive Certified Data Product**.

The repository does not contain accepted contracts that authorize the other requested inputs or
analyses:

- Initiative 201 leaves contractor grain, business keys, lineage, eligibility, and certification as
  Pending Contract. Competition analysis is therefore not authorized yet.
- Initiative 301 is blocked and no accepted Cost Certified Data Product defines Cost History or
  Bid-Tab grain, identity, date-conflict handling, matrix completeness, lineage, eligibility, or
  consumer guarantees.
- No accepted cross-product identity contract defines canonical contract keys, matching rules,
  ambiguous-match behavior, reconciliation grain, or unmatched-roster guarantees.

Physical warehouse relations, pull-request observations, and numeric profiling results cannot fill
these contract gaps because physical storage is not the certified boundary.

## Constitutional Alignment

The requested operational safeguards align with the Constitution: certified inputs only,
read-only access, preserved limitations, explicit reconciliation, explainable exclusions, and no
unsupported matrix analysis.

Implementation does **not** currently align. Building the spine now would require the Intelligence
Layer to infer business identity and eligibility from physical warehouse details or uncertified
observations. That would bypass Certified Data Products, invent guarantees that the current
contracts do not make, and make implementation details the architectural authority.

Per the Constitution and repository engineering workflow, implementation stops at this review. No
adapter, model, service, SQL, MCP tool, UI, or warehouse mutation is authorized by this document.

## Required Governance to Unblock Implementation

Before implementation begins, accepted contracts must define:

1. the Contractor/competition evidence grain, stable contract key, lineage, eligible states, and
   the governed basis for the 249-contract competition cohort;
2. the Cost History and Bid-Tab grains, stable contract keys, lineage, eligibility and quarantine
   semantics, date-conflict policy, and the governed basis for the nine exclusions;
3. bid-item matrix completeness semantics and the governed basis for disabling full-matrix analysis;
4. a cross-product identity contract specifying normalization and match rules, source precedence (if
   any), ambiguous and unmatched outcomes, and a prohibition on silently merging identities;
5. coverage and reconciliation contracts, including district/year treatment when values are absent
   or disputed and roster-level lineage back to each certified product; and
6. explicit accepted/current, schema-qualified physical mappings for every certified input.

Once these conditions are accepted, the smallest coherent implementation may add typed business
models, a service, and read-only adapters over only those governed mappings. Until then, the
requested counts and exclusions remain certification claims to be validated upstream rather than
constants to embed in this repository.
