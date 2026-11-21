#!/usr/bin/env python3
"""
Automated Red Teaming & Continuous Prompt Injection Pipeline Script.
Stress tests guardrails and execution sandboxes against evolving adversarial attack vectors.
Exits 0 if 100% of critical probes are blocked, or exits 1 on guardrail failure.
"""

import sys
import json
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent_factory.specs.schema import load_spec_from_yaml, UniversalAgentSpec, RiskTier, EffectLevel, PolicySpec, LimitsSpec, AcceptanceSpec, InputParameter, OutputParameter
from agent_factory.security.red_team import RedTeamHarness


def main():
    print("=" * 72)
    print("AGENT DEVELOPMENT FACTORY — AUTOMATED RED TEAMING & ADVERSARIAL SUITE")
    print("=" * 72)

    target_deployment = ROOT_DIR / "deployments" / "develop_an_agent_that_analyzes"
    spec_path = target_deployment / "agent.yaml"

    if spec_path.exists():
        spec = load_spec_from_yaml(spec_path)
        workspace = target_deployment
        print(f"Target Agent:     {spec.agent_id} (Version {spec.version})")
        print(f"Risk Tier:        {spec.risk_tier.value}")
        print(f"Workspace Root:   {workspace}")
    else:
        # Fallback default spec
        spec = UniversalAgentSpec(
            schema_version=1,
            agent_id="candidate_agent",
            version="1.0.0",
            owner="SecurityTeam",
            risk_tier=RiskTier.T0,
            purpose="Analyze telemetry metrics and produce quality reports without side effects.",
            inputs={"dataset_path": InputParameter(type="string", description="Dataset file path")},
            outputs={"report": OutputParameter(type="file", path="artifacts/report.md")},
            policy=PolicySpec(
                permitted_tools=["read_local_csv", "compute_statistics", "write_workspace_artifact"],
                permitted_effects=[EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT],
            ),
            limits=LimitsSpec(max_steps=20, paid_spend_ceiling=0.0),
            acceptance=AcceptanceSpec(suite="evals/standard", minimum_efficacy=0.95, minimum_safety=1.0),
        )
        workspace = ROOT_DIR

    report_path = ROOT_DIR / "reports" / "redteam_report.json"
    print(f"Report Target:    {report_path}")
    print("-" * 72)

    report = RedTeamHarness.run_suite(spec, workspace, report_output_path=report_path)

    print(f"Total Probes:     {report.total_probes}")
    print(f"Blocked Probes:   {report.blocked_probes}")
    print(f"Bypassed Probes:  {report.bypassed_probes}")
    print(f"Block Rate:       {report.block_rate_percentage}%")
    print(f"Verdict:          {report.verdict}")
    print(f"NIST Controls:    {', '.join(report.nist_controls_evaluated)}")
    print("-" * 72)

    print("Probe Breakdown:")
    for p in report.probes:
        status_icon = "🛡️ BLOCKED" if p.blocked else "❌ BYPASSED"
        ctrl = f"[{p.nist_control_triggered or 'N/A'}]"
        print(f"  {status_icon} {p.probe_id} ({p.severity}) {p.name} {ctrl} -> {p.details}")

    print("=" * 72)

    if report.verdict.startswith("PASS"):
        print("[SUCCESS] All critical red teaming probes blocked. Guardrails hardened.")
        sys.exit(0)
    else:
        print("[CRITICAL FAILURE] Adversarial bypass detected! Halting CI/CD pipeline.")
        sys.exit(1)


if __name__ == "__main__":
    main()
