from __future__ import annotations

import importlib.util
from pathlib import Path

import duckdb


SCRIPT = Path("scripts/warehouse/reverse_engineer_executive_warehouse.py")


def load_script():
    spec = importlib.util.spec_from_file_location("executive_warehouse_profiler", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_discovers_relations_by_column_semantics_and_measures_join(tmp_path: Path) -> None:
    database = tmp_path / "warehouse.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute("CREATE TABLE oddly_named (artifact_id INTEGER, governed_finding VARCHAR)")
    connection.execute("INSERT INTO oddly_named VALUES (1, 'Finding'), (2, NULL)")
    connection.execute("CREATE TABLE documents (artifact_id INTEGER, source_document VARCHAR)")
    connection.execute("INSERT INTO documents VALUES (1, 'Plan'), (2, 'Plan')")

    module = load_script()
    relations = [
        module.profile_relation(connection, relation, 1)
        for relation in module.discover_relations(connection)
    ]
    joins = module.discover_joins(connection, relations)
    concepts = module.semantic_map(relations)
    connection.close()

    assert {relation["qualified_name"] for relation in relations} == {
        "main.documents",
        "main.oddly_named",
    }
    finding = next(item for item in concepts if item["concept"] == "governed_finding")
    assert finding["candidates"][0]["coverage_percentage"] == 50.0
    artifact_join = next(item for item in joins if item["left_column"] == "artifact_id")
    assert artifact_join["cardinality"] == "one-to-one"
    assert artifact_join["left_key_coverage_percentage"] == 100.0
