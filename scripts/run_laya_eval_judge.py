#!/usr/bin/env python3
"""Execute LLM-as-a-Judge Evaluation Harness calibrated via Laya RLCD.

Evaluates codebase and deployment artifacts against the 3 rubrics:
1. Hallucination & Factual Grounding
2. Instruction Following & Spec Adherence
3. Security Boundaries & Containment
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent_factory.evals.judge import LLMJudgeHarness


def run_benchmark(target_dir: Path, revision_id: str = "rev-001") -> int:
    print("=" * 72)
    print("AGENT DEVELOPMENT FACTORY — LLM-AS-A-JUDGE & LAYA RLCD BENCHMARK")
    print("=" * 72)

    harness = LLMJudgeHarness()

    # Locate artifacts in target deployment
    artifacts_dir = target_dir / "artifacts"
    report_file = artifacts_dir / "anomaly_report.md"
    ledger_file = artifacts_dir / "summary_ledger.json"
    
    code_file = target_dir / "src" / "agent.py"
    if not code_file.exists():
        code_file = target_dir / "agent.py"
    if not code_file.exists():
        code_file = PROJECT_ROOT / "deployments" / "develop_an_agent_that_analyzes" / "src" / "agent.py"

    output_text = ""
    if report_file.exists():
        output_text += report_file.read_text(encoding="utf-8")
    if ledger_file.exists():
        output_text += "\n" + ledger_file.read_text(encoding="utf-8")

    code_str = code_file.read_text(encoding="utf-8") if code_file.exists() else ""

    # Ground truth source inputs from fixtures
    fixtures_dir = target_dir / "fixtures"
    source_inputs = ""
    if (fixtures_dir / "anomalous_sample.csv").exists():
        source_inputs += (fixtures_dir / "anomalous_sample.csv").read_text(encoding="utf-8")
    if (fixtures_dir / "clean_sample.csv").exists():
        source_inputs += "\n" + (fixtures_dir / "clean_sample.csv").read_text(encoding="utf-8")
    if not source_inputs:
        source_inputs = "id,value,category\n1,10.5,A\n2,11.2,A\n3,9.8,A\n4,105.0,B\n5,12.1,A\n6,10.9,A\n7,11.5,A\n8,-45.0,C\n9,10.2,A\n10,999.0,B"

    # Confirmed requirements
    requirements = [
        {"id": "REQ-01", "statement": "Analyze incoming CSV tabular payloads for numerical anomalies", "status": "CONFIRMED"},
        {"id": "REQ-02", "statement": "Enforce zero-spend paid spend ceiling 0.0", "status": "CONFIRMED"},
        {"id": "REQ-03", "statement": "Write markdown anomaly report into artifacts directory", "status": "CONFIRMED"},
    ]

    constraints = [
        "must not delete existing records",
        "zero spend cloud API models",
    ]

    print(f"Target Directory: {target_dir}")
    print(f"Code Artifact:   {code_file.name if code_file.exists() else 'N/A'}")
    print(f"Output Artifact: {report_file.name if report_file.exists() else 'N/A'}")
    print("-" * 72)

    report = harness.evaluate_candidate(
        revision_id=revision_id,
        output_text=output_text,
        source_inputs=source_inputs,
        requirements=requirements,
        code_str=code_str,
        constraints=constraints,
        spend_usd=0.00,
    )

    # Print Scorecard
    print("\n[RUBRIC 1] Hallucination & Factual Grounding")
    hg = report.rubrics["hallucination"]
    print(f"  Score:      {hg.score:.2f} / 1.00  (Threshold: {hg.passing_threshold:.2f}) -> {'PASS' if hg.passed else 'FAIL'}")
    for f in hg.findings:
        print(f"  Finding:    {f}")

    print("\n[RUBRIC 2] Instruction Following & Specification Adherence")
    if_res = report.rubrics["instruction"]
    print(f"  Score:      {if_res.score:.2f} / 1.00  (Threshold: {if_res.passing_threshold:.2f}) -> {'PASS' if if_res.passed else 'FAIL'}")
    for f in if_res.findings:
        print(f"  Finding:    {f}")

    print("\n[RUBRIC 3] Security Boundaries & Containment")
    sb = report.rubrics["security"]
    print(f"  Score:      {sb.score:.2f} / 1.00  (Threshold: {sb.passing_threshold:.2f}) -> {'PASS' if sb.passed else 'FAIL'}")
    for f in sb.findings:
        print(f"  Finding:    {f}")

    print("\n" + "=" * 72)
    print("LAYA RLCD CALIBRATED DECISION")
    print("=" * 72)
    dec = report.decision
    print(f"  RLCD Weights Applied: Hallucination={dec.weights_applied.weight_hallucination:.3f}, Instruction={dec.weights_applied.weight_instruction:.3f}, Security={dec.weights_applied.weight_security:.3f}")
    print(f"  RLCD Prior Source:   {dec.weights_applied.source}")
    print(f"  Composite Score:     {dec.composite_score:.3f}  (Passing Threshold: {dec.threshold_applied:.2f})")
    print(f"  Quality Gate Verdict:{dec.verdict} {'(PROMOTED)' if report.promoted else '(HELD)'}")
    print(f"  Laya Audit Logged:   {'YES' if dec.laya_feedback_logged else 'NO'}")
    print(f"  Rationale:           {dec.rationale}")

    # Write JSON report
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_json_path = reports_dir / "laya_rlcd_eval_report.json"
    report_data = {
        "revision_id": report.revision_id,
        "promoted": report.promoted,
        "summary": report.summary,
        "timestamp": report.timestamp,
        "decision": {
            "verdict": dec.verdict,
            "composite_score": dec.composite_score,
            "threshold": dec.threshold_applied,
            "weights": {
                "hallucination": dec.weights_applied.weight_hallucination,
                "instruction": dec.weights_applied.weight_instruction,
                "security": dec.weights_applied.weight_security,
                "source": dec.weights_applied.source,
            },
            "rationale": dec.rationale,
        },
        "rubrics": {
            "hallucination": {"score": hg.score, "passed": hg.passed, "findings": hg.findings},
            "instruction": {"score": if_res.score, "passed": if_res.passed, "findings": if_res.findings},
            "security": {"score": sb.score, "passed": sb.passed, "findings": sb.findings},
        },
    }
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"\n[REPORT SAVED] -> {report_json_path}")
    print("=" * 72)

    return 0 if report.promoted else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Laya RLCD Judge Benchmark")
    parser.add_argument(
        "--target",
        type=Path,
        default=PROJECT_ROOT / "deployments" / "develop_an_agent_that_analyzes",
        help="Path to deployment directory",
    )
    parser.add_argument("--revision", type=str, default="rev-001", help="Revision ID")
    args = parser.parse_args()
    sys.exit(run_benchmark(args.target, args.revision))
