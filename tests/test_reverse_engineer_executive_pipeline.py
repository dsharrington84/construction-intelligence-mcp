import importlib.util
import sys
from pathlib import Path


SCRIPT = Path("scripts/pipeline/reverse_engineer_executive_pipeline.py")


def load_module():
    spec = importlib.util.spec_from_file_location("executive_pipeline_scanner", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_scan_separates_production_writes_from_test_fixtures(tmp_path: Path) -> None:
    module = load_module()
    (tmp_path / "pipeline.py").write_text(
        'sql = "CREATE TABLE executive_section AS SELECT * FROM raw"\n'
    )
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_fixture.py").write_text('sql = "CREATE TABLE governed_finding (id INT)"\n')

    result = module.scan(tmp_path)

    assert [(item["relation"], item["classification"]) for item in result["operations"]] == [
        ("executive_section", "production_candidate"),
        ("governed_finding", "test_fixture"),
    ]


def test_write_inventories_reports_absent_producer(tmp_path: Path) -> None:
    module = load_module()
    (tmp_path / "README.md").write_text("governed_finding is a proposed concept\n")
    output = tmp_path / "output"

    module.write_inventories(module.scan(tmp_path), output)

    producers = (output / "executive_table_producers.json").read_text()
    semantics = (output / "executive_semantic_generation.json").read_text()
    assert "No Executive warehouse producer exists" in producers
    assert '"governed_finding_conclusion": "not_generated_in_repository"' in semantics
