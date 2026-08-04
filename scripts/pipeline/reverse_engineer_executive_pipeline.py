#!/usr/bin/env python3
"""Inventory evidence of Executive warehouse production in a source tree.

This is a static, read-only scanner.  It never connects to DuckDB and deliberately
distinguishes executable SQL from documentation and test fixtures.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".py", ".sql", ".duckdb.sql", ".sh"}
EXCLUDED_PARTS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", ".venv"}
SQL_WRITE_PATTERNS = {
    "create_table": re.compile(
        r"\bCREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
        r"(?P<relation>[\w.\"`]+)",
        re.IGNORECASE,
    ),
    "create_view": re.compile(
        r"\bCREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(?P<relation>[\w.\"`]+)",
        re.IGNORECASE,
    ),
    "insert_into": re.compile(r"\bINSERT\s+INTO\s+(?P<relation>[\w.\"`]+)", re.IGNORECASE),
    "merge_into": re.compile(r"\bMERGE\s+INTO\s+(?P<relation>[\w.\"`]+)", re.IGNORECASE),
    "update": re.compile(r"\bUPDATE\s+(?P<relation>[\w.\"`]+)\s+SET\b", re.IGNORECASE),
    "copy_to": re.compile(r"\bCOPY\s+(?P<relation>[\w.\"`]+)\s+TO\b", re.IGNORECASE),
}
READ_PATTERN = re.compile(r"\b(?:FROM|JOIN)\s+(?P<relation>[\w.\"`]+)", re.IGNORECASE)
CONCEPTS = (
    "governed_finding",
    "source_document",
    "source_heading",
    "program",
    "theme",
    "objective",
    "policy_driver",
    "expected_outcome",
    "region",
    "district",
    "project_id",
    "artifact_id",
    "knowledge_record_id",
    "section",
)


@dataclass(frozen=True)
class SqlOperation:
    operation: str
    relation: str
    file: str
    line: int
    context: str
    classification: str


def _classification(path: Path) -> str:
    if "tests" in path.parts:
        return "test_fixture"
    if path.suffix.lower() == ".md":
        return "documentation"
    return "production_candidate"


def _files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not EXCLUDED_PARTS.intersection(path.relative_to(root).parts)
        and path.name != Path(__file__).name
        and (path.suffix.lower() in SOURCE_SUFFIXES or path.suffix.lower() == ".md")
    )


def scan(root: Path) -> dict[str, object]:
    """Return reproducible static pipeline evidence rooted at ``root``."""
    operations: list[SqlOperation] = []
    reads: list[dict[str, object]] = []
    concept_occurrences = {concept: [] for concept in CONCEPTS}
    inspected = _files(root)
    for path in inspected:
        relative = path.relative_to(root).as_posix()
        classification = _classification(path.relative_to(root))
        for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            for operation, pattern in SQL_WRITE_PATTERNS.items():
                for match in pattern.finditer(line):
                    operations.append(
                        SqlOperation(
                            operation,
                            match.group("relation").strip('"`'),
                            relative,
                            line_number,
                            line.strip()[:300],
                            classification,
                        )
                    )
            for match in READ_PATTERN.finditer(line):
                reads.append(
                    {
                        "relation": match.group("relation").strip('"`'),
                        "file": relative,
                        "line": line_number,
                        "classification": classification,
                    }
                )
            lowered = line.lower()
            for concept in CONCEPTS:
                if concept in lowered:
                    concept_occurrences[concept].append(
                        {"file": relative, "line": line_number, "classification": classification}
                    )
    return {
        "root": str(root.resolve()),
        "inspected_files": [path.relative_to(root).as_posix() for path in inspected],
        "operations": [asdict(operation) for operation in operations],
        "reads": reads,
        "concept_occurrences": concept_occurrences,
    }


def write_inventories(scan_result: dict[str, object], output_dir: Path) -> None:
    """Write the three governed pipeline evidence inventories."""
    output_dir.mkdir(parents=True, exist_ok=True)
    operations = scan_result["operations"]
    production_writes = [
        item for item in operations if item["classification"] == "production_candidate"
    ]
    metadata = {
        "method": "static_source_scan",
        "read_only": True,
        "scope_root": scan_result["root"],
        "evidence_limit": "Only files present in the scanned repository are represented.",
    }
    payloads = {
        "executive_pipeline_inventory.json": {
            "metadata": metadata,
            "inspected_files": scan_result["inspected_files"],
            "sql_operations": operations,
            "relation_reads": scan_result["reads"],
        },
        "executive_table_producers.json": {
            "metadata": metadata,
            "production_relation_writes": production_writes,
            "conclusion": (
                "No Executive warehouse producer exists in this repository."
                if not production_writes
                else "Production-candidate relation writes require owner certification."
            ),
        },
        "executive_semantic_generation.json": {
            "metadata": metadata,
            "concept_occurrences": scan_result["concept_occurrences"],
            "governed_finding_conclusion": (
                "not_generated_in_repository"
                if not any(
                    item["classification"] == "production_candidate"
                    and "governed_finding" in item["relation"].lower()
                    for item in operations
                )
                else "production_candidate_write_present"
            ),
        },
    }
    for name, payload in payloads.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path("data/output/pipeline"))
    args = parser.parse_args()
    write_inventories(scan(args.root.resolve()), args.output_dir)


if __name__ == "__main__":
    main()
