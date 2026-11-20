"""
Autonomous Test Synthesizer and Deterministic Fixture Generator.
"""

from pathlib import Path
from typing import Dict, Any


class TestGenerator:
    """Synthesizes pytest test suites and frozen synthetic data fixtures."""

    @classmethod
    def generate_fixtures(cls, fixtures_dir: Path) -> Dict[str, Path]:
        fixtures_dir = Path(fixtures_dir)
        fixtures_dir.mkdir(parents=True, exist_ok=True)

        # 1. Clean dataset fixture (no anomalies)
        clean_file = fixtures_dir / "clean_sample.csv"
        clean_data = [
            "id,transaction_amount,account_status,city",
            "1,100.50,active,New York",
            "2,102.20,active,London",
            "3,98.40,active,Tokyo",
            "4,105.10,active,Paris",
            "5,99.80,active,Berlin",
            "6,101.00,active,Singapore",
            "7,103.50,active,Sydney",
            "8,97.90,active,Toronto",
            "9,104.20,active,Amsterdam",
            "10,100.00,active,Seoul",
        ]
        with open(clean_file, "w", encoding="utf-8") as f:
            f.write("\n".join(clean_data) + "\n")

        # 2. Anomalous dataset fixture (contains missing values + extreme outlier)
        anomalous_file = fixtures_dir / "anomalous_sample.csv"
        anomalous_data = [
            "id,transaction_amount,account_status,city",
            "1,100.00,active,New York",
            "2,102.00,active,London",
            "3,98.00,,Tokyo",  # Missing account_status
            "4,101.00,active,Paris",
            "5,99.00,active,",  # Missing city
            "6,103.00,active,Singapore",
            "7,97.00,active,Sydney",
            "8,100.00,active,Toronto",
            "9,102.00,active,Amsterdam",
            "10,15000.00,active,Seoul",  # Massive statistical outlier (15,000 vs ~100)
        ]
        with open(anomalous_file, "w", encoding="utf-8") as f:
            f.write("\n".join(anomalous_data) + "\n")

        return {"clean": clean_file, "anomalous": anomalous_file}

    @classmethod
    def generate_test_suite(cls, tests_dir: Path, src_dir: Path, fixtures_dir: Path) -> Path:
        tests_dir = Path(tests_dir)
        tests_dir.mkdir(parents=True, exist_ok=True)
        test_file = tests_dir / "test_agent.py"

        content = f'''"""
Deterministic Automated Test Suite for Generated Agent.
"""

import sys
import json
import pytest
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(r"{src_dir.resolve()}")))

from agent import run_agent, DataAnomalyAnalyzer


@pytest.fixture
def clean_csv():
    return Path(r"{fixtures_dir.resolve()}") / "clean_sample.csv"


@pytest.fixture
def anomalous_csv():
    return Path(r"{fixtures_dir.resolve()}") / "anomalous_sample.csv"


def test_clean_dataset_analysis(clean_csv):
    """Asserts that clean data produces 0 anomalies and valid column statistics."""
    analyzer = DataAnomalyAnalyzer(threshold_std_dev=3.0)
    res = analyzer.analyze_csv(clean_csv)

    assert res["total_rows"] == 10
    assert res["column_count"] == 4
    assert res["anomaly_count"] == 0
    assert "transaction_amount" in res["columns"]
    assert res["columns"]["transaction_amount"]["is_numeric"] is True
    assert 95.0 < res["columns"]["transaction_amount"]["mean"] < 105.0


def test_anomalous_dataset_analysis(anomalous_csv):
    """Asserts that missing values and extreme outliers are reliably detected."""
    analyzer = DataAnomalyAnalyzer(threshold_std_dev=2.5)
    res = analyzer.analyze_csv(anomalous_csv)

    assert res["total_rows"] == 10
    assert res["anomaly_count"] >= 2

    # Check for missing data detection
    missing_anomalies = [a for a in res["anomalies"] if a["type"] == "MISSING_DATA"]
    assert len(missing_anomalies) >= 2

    # Check for statistical outlier detection
    outlier_anomalies = [a for a in res["anomalies"] if a["type"] == "STATISTICAL_OUTLIER"]
    assert len(outlier_anomalies) == 1
    assert outlier_anomalies[0]["value"] == 15000.0


def test_artifact_generation(tmp_path, anomalous_csv):
    """Asserts that executing run_agent creates both report.md and summary.json losslessly."""
    out_dir = tmp_path / "artifacts"
    res = run_agent(str(anomalous_csv), str(out_dir), threshold=2.5)

    assert res["status"] == "COMPLETED"
    report_file = out_dir / "anomaly_report.md"
    summary_file = out_dir / "summary_ledger.json"

    assert report_file.exists()
    assert report_file.stat().st_size > 100
    report_text = report_file.read_text(encoding="utf-8")
    assert "# Data Quality Anomaly Analysis Report" in report_text
    assert "STATISTICAL_OUTLIER" in report_text

    assert summary_file.exists()
    with open(summary_file, "r", encoding="utf-8") as f:
        summary_json = json.load(f)
    assert summary_json["total_rows"] == 10


def test_missing_dataset_exception(tmp_path):
    """Asserts that non-existent files raise FileNotFoundError."""
    non_existent = tmp_path / "does_not_exist.csv"
    analyzer = DataAnomalyAnalyzer()
    with pytest.raises(FileNotFoundError):
        analyzer.analyze_csv(non_existent)
'''
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        return test_file
