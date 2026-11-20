#!/usr/bin/env python3
"""
Automated Verification & Evaluation Runner.
Executes Deep Evaluator test suites with optional LangSmith Free Tier telemetry.
Zero-cost CI/CD verification engine for Agent Development Factory.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent_factory.evals.runner import EvaluationRunner
from agent_factory.evals.langsmith_adapter import LangSmithAdapter


def find_candidate_workspaces(deployments_dir: Path):
    """Locate deployed candidate agents or workspaces to evaluate."""
    candidates = []
    if not deployments_dir.exists():
        return candidates

    for item in deployments_dir.iterdir():
        if item.is_dir() and (item / "src").exists() and (item / "fixtures").exists():
            candidates.append(item)
    return candidates


def run_evaluation_suite(target_dir: Path = None, output_json: Path = None):
    """Run verification evaluation across candidate agents."""
    print("=" * 70)
    print("AGENT DEVELOPMENT FACTORY — ZERO-COST VERIFICATION EVALUATOR")
    print("=" * 70)

    adapter = LangSmithAdapter()
    status = adapter.get_status()
    print(f"Evaluation Mode: {status['mode']}")
    print(f"Telemetry Tier:  {status['tier']}")
    print(f"Project Target:  {status['project']}")
    print(f"Cost Estimate:   ${status['cost']:.4f} USD (Zero-Cost Software Architecture)")
    print("-" * 70)

    deployments_dir = target_dir or (ROOT_DIR / "deployments")
    candidates = find_candidate_workspaces(deployments_dir)

    if not candidates:
        print(f"[WARNING] No candidate deployments found in {deployments_dir}")
        return True, {"candidates_evaluated": 0, "status": "NO_CANDIDATES"}

    all_passed = True
    results = {}

    for candidate in candidates:
        agent_name = candidate.name
        print(f"\n[EVALUATING AGENT]: {agent_name}")
        ws_dirs = {
            "root": candidate,
            "src": candidate / "src",
            "fixtures": candidate / "fixtures",
            "artifacts": candidate / "artifacts",
        }
        ws_dirs["artifacts"].mkdir(parents=True, exist_ok=True)

        runner = EvaluationRunner()
        start = time.perf_counter()
        score = runner.evaluate_candidate(ws_dirs)
        elapsed = (time.perf_counter() - start) * 1000

        score_dict = score.model_dump()
        telemetry = adapter.record_evaluation(agent_name, score_dict)

        passed = score_dict.get("passed", False)
        if not passed:
            all_passed = False

        status_symbol = "PASSED [OK]" if passed else "FAILED [X]"
        print(f"  Result:     {status_symbol} ({score_dict.get('verdict')})")
        print(f"  Efficacy:   {score_dict.get('efficacy'):.4f} (Threshold >= 0.95)")
        print(f"  Safety:     {score_dict.get('safety'):.4f} (Zero-Tolerance = 1.00)")
        print(f"  Wall Time:  {score_dict.get('efficiency', {}).get('wall_time_ms', 0):.2f} ms")
        print(f"  Cost (USD): ${score_dict.get('efficiency', {}).get('cost_usd', 0):.4f}")
        print(f"  Telemetry:  {telemetry.get('mode')} -> {telemetry.get('status')}")

        print("  Quality Gates Checklist:")
        for name, details in score_dict.get("grader_details", {}).items():
            g_sym = "[x]" if details.get("passed") else "[ ]"
            print(f"    {g_sym} {name}: {details.get('details')}")

        results[agent_name] = {
            "score": score_dict,
            "telemetry": telemetry,
            "elapsed_ms": elapsed,
        }

    # Write summary report
    reports_dir = ROOT_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_json or (reports_dir / "eval_results.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "all_passed": all_passed,
                "evaluator": status["mode"],
                "results": results,
            },
            f,
            indent=2,
        )
    print(f"\n[REPORT] Saved evaluation results to: {summary_path}")

    # GitHub Step Summary integration
    gh_summary = os.getenv("GITHUB_STEP_SUMMARY")
    if gh_summary:
        try:
            with open(gh_summary, "a", encoding="utf-8") as gf:
                gf.write("## 🚀 Agent Development Factory — Evaluation Verification Report\n\n")
                gf.write(f"- **Mode:** `{status['mode']}`\n")
                gf.write(f"- **Tier:** `{status['tier']}`\n")
                gf.write(f"- **Overall Status:** `{'PASSED' if all_passed else 'FAILED'}`\n\n")
                gf.write("| Agent | Efficacy | Safety | Wall Time (ms) | Cost ($) | Verdict |\n")
                gf.write("|---|---|---|---|---|---|\n")
                for ag, r in results.items():
                    sc = r["score"]
                    eff = sc.get("efficiency", {})
                    gf.write(
                        f"| `{ag}` | **{sc.get('efficacy'):.2f}** | **{sc.get('safety'):.2f}** | "
                        f"{eff.get('wall_time_ms', 0):.1f} | ${eff.get('cost_usd', 0):.4f} | "
                        f"`{sc.get('verdict')}` |\n"
                    )
                gf.write("\n")
        except Exception as err:
            print(f"[NOTE] Could not write to GITHUB_STEP_SUMMARY: {err}")

    print("=" * 70)
    print(f"VERIFICATION SUITE COMPLETE: {'ALL GATES PASSED' if all_passed else 'VERIFICATION FAILED'}")
    print("=" * 70)
    return all_passed, results


def main():
    parser = argparse.ArgumentParser(description="Agent Development Factory Evaluation Runner")
    parser.add_argument("--deployments-dir", type=Path, default=None, help="Path to deployments directory")
    parser.add_argument("--output", type=Path, default=None, help="Path to output JSON summary report")
    args = parser.parse_args()

    passed, _ = run_evaluation_suite(target_dir=args.deployments_dir, output_json=args.output)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
