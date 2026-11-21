"""
Deterministic Automated Test Suite for Generated Agent.
"""

import sys
import json
import pytest
from pathlib import Path

# Add src to sys.path relative to this test file
current_dir = Path(__file__).resolve().parent
agent_dir = current_dir.parent
sys.path.insert(0, str(agent_dir / "src"))

from agent import run_agent, DataAnomalyAnalyzer


@pytest.fixture
def clean_csv():
    return agent_dir / "fixtures" / "clean_sample.csv"


@pytest.fixture
def anomalous_csv():
    return agent_dir / "fixtures" / "anomalous_sample.csv"


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
