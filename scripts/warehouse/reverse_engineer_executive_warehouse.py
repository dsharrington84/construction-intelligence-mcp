#!/usr/bin/env python3
"""Profile the executive warehouse without modifying it.

The generated inventories are evidence snapshots: all relations are discovered from
the catalog, selection is based on both relation and column semantics, and joins are
measured rather than inferred from naming alone.
"""

from __future__ import annotations

import argparse
import datetime as dt
import decimal
import json
import os
from pathlib import Path
from typing import Any

import duckdb

TERMS = (
    "executive",
    "artifact",
    "document",
    "section",
    "knowledge",
    "semantic",
    "source",
    "region",
    "profile",
    "inventory",
    "page",
    "table",
    "candidate",
    "refined",
    "finding",
    "objective",
    "theme",
    "policy",
    "outcome",
    "program",
)
KEY_TERMS = (
    "artifact_id",
    "document_id",
    "section_key",
    "section_id",
    "knowledge_record_id",
    "project_id",
    "district",
    "program_id",
    "region_id",
    "source_document",
)
SEMANTIC_CONCEPTS = {
    "governed_finding": ("governed_finding", "finding"),
    "source_document": ("source_document", "document_name", "document_title"),
    "source_heading": ("source_heading", "heading", "section_heading"),
    "source_section_key": ("source_section_key", "section_key"),
    "artifact_id": ("artifact_id",),
    "knowledge_record_id": ("knowledge_record_id", "knowledge_id"),
    "project linkage": ("project_id", "project_number"),
    "district linkage": ("district", "district_id", "district_number"),
    "program": ("program", "program_id", "program_name"),
    "objective": ("objective", "strategic_objective"),
    "theme": ("theme", "strategic_theme"),
    "policy driver": ("policy_driver",),
    "expected outcome": ("expected_outcome", "outcome"),
}


def quoted(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def qualified(schema: str, relation: str) -> str:
    return f"{quoted(schema)}.{quoted(relation)}"


def json_value(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime, dt.time, decimal.Decimal, bytes)):
        return str(value)
    return value


def fetch_dicts(
    connection: duckdb.DuckDBPyConnection, sql: str, params: list[Any] | None = None
) -> list[dict[str, Any]]:
    cursor = connection.execute(sql, params or [])
    names = [item[0] for item in cursor.description]
    return [
        {name: json_value(value) for name, value in zip(names, row, strict=True)}
        for row in cursor.fetchall()
    ]


def discover_relations(connection: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    catalog = fetch_dicts(
        connection,
        """
        SELECT t.table_schema, t.table_name, t.table_type, c.column_name, c.data_type,
               c.ordinal_position
        FROM information_schema.tables t
        JOIN information_schema.columns c USING (table_catalog, table_schema, table_name)
        WHERE t.table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY t.table_schema, t.table_name, c.ordinal_position
    """,
    )
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for item in catalog:
        key = (item["table_schema"], item["table_name"])
        relation = grouped.setdefault(
            key, {"schema": key[0], "name": key[1], "type": item["table_type"], "columns": []}
        )
        relation["columns"].append(
            {
                "name": item["column_name"],
                "type": item["data_type"],
                "ordinal": item["ordinal_position"],
            }
        )
    return [
        relation
        for relation in grouped.values()
        if any(
            term in " ".join([relation["name"], *(c["name"] for c in relation["columns"])]).lower()
            for term in TERMS
        )
    ]


def profile_relation(
    connection: duckdb.DuckDBPyConnection, relation: dict[str, Any], sample_size: int
) -> dict[str, Any]:
    table = qualified(relation["schema"], relation["name"])
    row_count = connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    columns = [column["name"] for column in relation["columns"]]
    column_profiles = []
    candidate_keys = []
    for column in columns:
        qcol = quoted(column)
        nulls, distinct_values = connection.execute(
            f"SELECT count(*) FILTER (WHERE {qcol} IS NULL), count(DISTINCT {qcol}) FROM {table}"
        ).fetchone()
        non_null = row_count - nulls
        duplicate_rows = max(non_null - distinct_values, 0)
        profile = {
            "column": column,
            "null_count": nulls,
            "null_percentage": round(100 * nulls / row_count, 4) if row_count else 0.0,
            "distinct_count": distinct_values,
            "duplicate_percentage_non_null": round(100 * duplicate_rows / non_null, 4)
            if non_null
            else 0.0,
        }
        column_profiles.append(profile)
        if row_count and nulls == 0 and distinct_values == row_count:
            candidate_keys.append(
                {
                    "columns": [column],
                    "unique": True,
                    "nullable": False,
                    "classification": "candidate; generation, stability, and version semantics require source metadata",
                }
            )
    purpose_evidence = [
        term for term in TERMS if term in " ".join([relation["name"], *columns]).lower()
    ]
    relation.update(
        {
            "qualified_name": f"{relation['schema']}.{relation['name']}",
            "purpose": "Executive-related candidate selected by catalog semantic terms: "
            + ", ".join(purpose_evidence),
            "row_count": row_count,
            "primary_grain": "one row per " + candidate_keys[0]["columns"][0]
            if candidate_keys
            else "not proven",
            "business_grain": "unknown; requires warehouse metadata or source-owner confirmation",
            "candidate_keys": candidate_keys,
            "unique_keys": [key["columns"] for key in candidate_keys],
            "foreign_keys": [],
            "field_groups": {
                term: [column for column in columns if term in column.lower()]
                for term in TERMS
                if any(term in column.lower() for column in columns)
            },
            "representative_records": fetch_dicts(
                connection, f"SELECT * FROM {table} LIMIT ?", [sample_size]
            ),
            "column_profiles": column_profiles,
        }
    )
    return relation


def discover_joins(
    connection: duckdb.DuckDBPyConnection, relations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    joins = []
    for left_index, left in enumerate(relations):
        left_columns = {column["name"].lower(): column["name"] for column in left["columns"]}
        for right in relations[left_index + 1 :]:
            right_columns = {column["name"].lower(): column["name"] for column in right["columns"]}
            for normalized in sorted(set(left_columns) & set(right_columns) & set(KEY_TERMS)):
                lc, rc = left_columns[normalized], right_columns[normalized]
                lt, rt = (
                    qualified(left["schema"], left["name"]),
                    qualified(right["schema"], right["name"]),
                )
                lq, rq = quoted(lc), quoted(rc)
                stats = connection.execute(f"""
                    WITH l AS (SELECT {lq} k, count(*) n FROM {lt} WHERE {lq} IS NOT NULL GROUP BY 1),
                         r AS (SELECT {rq} k, count(*) n FROM {rt} WHERE {rq} IS NOT NULL GROUP BY 1)
                    SELECT (SELECT count(*) FROM l), (SELECT count(*) FROM r),
                           count(*), coalesce(sum(l.n), 0), coalesce(sum(r.n), 0),
                           coalesce(sum(l.n * r.n), 0),
                           count(*) FILTER (WHERE l.n > 1), count(*) FILTER (WHERE r.n > 1)
                    FROM l JOIN r USING (k)
                """).fetchone()
                ld, rd, overlap, matched_left, matched_right, joined_rows, lm, rm = stats
                cardinality = (
                    "many-to-many"
                    if lm and rm
                    else "one-to-many"
                    if rm
                    else "many-to-one"
                    if lm
                    else "one-to-one"
                )
                joins.append(
                    {
                        "left_relation": left["qualified_name"],
                        "left_column": lc,
                        "right_relation": right["qualified_name"],
                        "right_column": rc,
                        "left_distinct_keys": ld,
                        "right_distinct_keys": rd,
                        "overlap_distinct_keys": overlap,
                        "left_key_coverage_percentage": round(100 * overlap / ld, 4) if ld else 0.0,
                        "right_key_coverage_percentage": round(100 * overlap / rd, 4)
                        if rd
                        else 0.0,
                        "matched_left_rows": matched_left,
                        "matched_right_rows": matched_right,
                        "joined_rows": joined_rows,
                        "cardinality": cardinality,
                        "accepted": bool(overlap and overlap == ld == rd),
                        "certification": "measured candidate; not certified without declared constraints or metadata",
                    }
                )
    return joins


def semantic_map(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for concept, aliases in SEMANTIC_CONCEPTS.items():
        matches = []
        for relation in relations:
            profiles = {
                profile["column"].lower(): profile for profile in relation["column_profiles"]
            }
            for alias in aliases:
                if alias in profiles:
                    profile = profiles[alias]
                    matches.append(
                        {
                            "relation": relation["qualified_name"],
                            "column": alias,
                            "business_meaning": "name match only; definition not present in catalog",
                            "grain": relation["business_grain"],
                            "coverage_percentage": round(100 - profile["null_percentage"], 4),
                            "evidence": "exact case-insensitive column-name match",
                        }
                    )
        result.append(
            {
                "concept": concept,
                "status": "located candidate" if matches else "unknown",
                "candidates": matches,
            }
        )
    return result


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=json_value) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=os.getenv("CI_DATABASE"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/output/warehouse"))
    parser.add_argument("--sample-size", type=int, default=3)
    args = parser.parse_args()
    if args.database is None or not args.database.is_file():
        parser.error("a readable DuckDB file is required via --database or CI_DATABASE")
    connection = duckdb.connect(str(args.database), read_only=True)
    try:
        relations = [
            profile_relation(connection, item, args.sample_size)
            for item in discover_relations(connection)
        ]
        joins = discover_joins(connection, relations)
    finally:
        connection.close()
    metadata = {
        "database": str(args.database),
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "read_only": True,
    }
    write_json(
        args.output_dir / "executive_relation_inventory.json",
        {"metadata": metadata, "relations": relations},
    )
    write_json(
        args.output_dir / "executive_join_inventory.json", {"metadata": metadata, "joins": joins}
    )
    write_json(
        args.output_dir / "executive_semantic_map.json",
        {"metadata": metadata, "concepts": semantic_map(relations)},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
