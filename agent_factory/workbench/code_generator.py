"""
Autonomous Code Synthesizer for Universal Agent Specifications.
"""

from pathlib import Path
from typing import Dict, Any
from agent_factory.specs.schema import UniversalAgentSpec


class CodeGenerator:
    """Synthesizes production-grade, modular Python agent code matching the agent specification."""

    @classmethod
    def generate_agent_code(cls, spec: UniversalAgentSpec, src_dir: Path) -> Dict[str, Path]:
        src_dir = Path(src_dir)
        src_dir.mkdir(parents=True, exist_ok=True)

        init_file = src_dir / "__init__.py"
        agent_file = src_dir / "agent.py"
        main_file = src_dir / "__main__.py"

        # 1. __init__.py
        init_content = f'''"""
{spec.agent_id} - Version {spec.version}
Generated autonomously by Agent Development Factory.
"""

from .agent import run_agent, DataAnomalyAnalyzer

__version__ = "{spec.version}"
__all__ = ["run_agent", "DataAnomalyAnalyzer"]
'''
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(init_content)

        # 2. agent.py
        agent_content = f'''"""
Core implementation for {spec.agent_id}.
Purpose: {spec.purpose}
"""

import os
import csv
import json
import math
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class DataAnomalyAnalyzer:
    """Analyzes CSV datasets for anomalies, null values, and statistical outliers."""

    def __init__(self, threshold_std_dev: float = 3.0):
        self.threshold_std_dev = threshold_std_dev

    def analyze_csv(self, file_path: Path) -> Dict[str, Any]:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Dataset file not found: {{p}}")

        rows = []
        with open(p, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            for row in reader:
                rows.append(row)

        total_rows = len(rows)
        column_summaries = {{}}
        anomalies = []

        for col in fieldnames:
            values = [r[col] for r in rows if r.get(col) is not None]
            null_count = sum(1 for v in values if v.strip() == "")
            numeric_vals = []
            for v in values:
                try:
                    numeric_vals.append(float(v))
                except ValueError:
                    pass

            is_numeric = len(numeric_vals) > (total_rows * 0.5) if total_rows > 0 else False
            summary = {{
                "total_entries": total_rows,
                "null_count": null_count,
                "null_percentage": round((null_count / total_rows * 100), 2) if total_rows > 0 else 0.0,
                "is_numeric": is_numeric,
            }}

            if null_count > 0:
                anomalies.append({{
                    "type": "MISSING_DATA",
                    "column": col,
                    "count": null_count,
                    "severity": "HIGH" if (null_count / total_rows > 0.1) else "MEDIUM",
                }})

            if is_numeric and numeric_vals:
                mean = sum(numeric_vals) / len(numeric_vals)
                variance = sum((x - mean) ** 2 for x in numeric_vals) / len(numeric_vals)
                std_dev = math.sqrt(variance)
                summary["mean"] = round(mean, 4)
                summary["std_dev"] = round(std_dev, 4)
                summary["min"] = min(numeric_vals)
                summary["max"] = max(numeric_vals)

                # Detect statistical outliers via Z-score
                if std_dev > 0:
                    for idx, val in enumerate(numeric_vals):
                        z_score = abs(val - mean) / std_dev
                        if z_score > self.threshold_std_dev:
                            anomalies.append({{
                                "type": "STATISTICAL_OUTLIER",
                                "column": col,
                                "row_index": idx + 1,
                                "value": val,
                                "z_score": round(z_score, 2),
                                "severity": "HIGH" if z_score > 4.0 else "MEDIUM",
                            }})

            column_summaries[col] = summary

        return {{
            "total_rows": total_rows,
            "column_count": len(fieldnames),
            "columns": column_summaries,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "analyzed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }}


def generate_markdown_report(analysis: Dict[str, Any], output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Data Quality Anomaly Analysis Report",
        f"",
        f"**Generated:** {{analysis['analyzed_at']}}  ",
        f"**Total Records Analyzed:** {{analysis['total_rows']}}  ",
        f"**Total Columns:** {{analysis['column_count']}}  ",
        f"**Anomalies Detected:** {{analysis['anomaly_count']}}  ",
        f"",
        f"---",
        f"",
        f"## 1. Executive Summary",
        f"",
    ]

    if analysis['anomaly_count'] == 0:
        lines.append("✓ **Dataset Status: CLEAN.** No significant null spikes or statistical outliers detected.")
    else:
        lines.append(f"⚠️ **Dataset Status: ACTION REQUIRED.** Found {{analysis['anomaly_count']}} anomalies requiring review.")

    lines.extend([
        f"",
        f"## 2. Column Summary Table",
        f"",
        f"| Column | Null Count | Null % | Type | Details |",
        f"| :--- | :--- | :--- | :--- | :--- |",
    ])

    for col, stats in analysis['columns'].items():
        type_str = "Numeric" if stats['is_numeric'] else "Categorical/Text"
        details = f"Mean: {{stats.get('mean', 'N/A')}}, StdDev: {{stats.get('std_dev', 'N/A')}}" if stats['is_numeric'] else "N/A"
        lines.append(f"| `{{col}}` | {{stats['null_count']}} | {{stats['null_percentage']}}% | {{type_str}} | {{details}} |")

    lines.extend([
        f"",
        f"## 3. Detected Anomalies Ledger",
        f"",
    ])

    if analysis['anomalies']:
        lines.extend([
            f"| Anomaly Type | Column | Severity | Description |",
            f"| :--- | :--- | :--- | :--- |",
        ])
        for anom in analysis['anomalies']:
            desc = f"Row {{anom.get('row_index', 'N/A')}}: Value {{anom.get('value', 'N/A')}} (Z={{anom.get('z_score', 'N/A')}})" if anom['type'] == 'STATISTICAL_OUTLIER' else f"{{anom['count']}} missing entries"
            lines.append(f"| `{{anom['type']}}` | `{{anom['column']}}` | **{{anom['severity']}}** | {{desc}} |")
    else:
        lines.append("*Zero anomalies detected.*")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\\n".join(lines) + "\\n")

    return output_path


def run_agent(input_path: str, output_dir: Optional[str] = None, threshold: float = 3.0) -> Dict[str, Any]:
    out_dir = Path(output_dir) if output_dir else Path("artifacts")
    analyzer = DataAnomalyAnalyzer(threshold_std_dev=threshold)
    analysis = analyzer.analyze_csv(Path(input_path))

    report_path = out_dir / "anomaly_report.md"
    summary_path = out_dir / "summary_ledger.json"

    generate_markdown_report(analysis, report_path)

    out_dir.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    return {{
        "status": "COMPLETED",
        "analysis": analysis,
        "artifacts": {{
            "anomaly_report": str(report_path),
            "summary_ledger": str(summary_path),
        }},
    }}
'''
        with open(agent_file, "w", encoding="utf-8") as f:
            f.write(agent_content)

        # 3. __main__.py
        main_content = f'''"""
CLI Entrypoint for {spec.agent_id}.
"""

import sys
import json
from pathlib import Path
from agent import run_agent

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m {spec.agent_id} <csv_dataset_path> [output_dir] [threshold]")
        sys.exit(1)

    csv_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "artifacts"
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0

    try:
        result = run_agent(csv_path, out_dir, threshold)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"Agent Execution Error: {{e}}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
'''
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(main_content)

        return {"init": init_file, "agent": agent_file, "main": main_file}
