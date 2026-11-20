"""
Production CLI for the Agent Development Factory.
"""

import sys
import os
import argparse
import json
from pathlib import Path

from agent_factory.registry.capability_registry import CapabilityRegistry
from agent_factory.registry.discovery import EnvironmentDiscovery
from agent_factory.control_plane.task_ledger import TaskLedger
from agent_factory.control_plane.intake import RequestIntake
from agent_factory.control_plane.orchestrator import FactoryOrchestrator, FactoryStage
from agent_factory.control_plane.lifecycle import AgentLifecycleManager
from agent_factory.workbench.workspace import WorkspaceManager
from agent_factory.workbench.code_generator import CodeGenerator
from agent_factory.workbench.test_generator import TestGenerator
from agent_factory.workbench.packager import ReleasePackager
from agent_factory.evals.runner import EvaluationRunner
from agent_factory.remediation.engine import RemediationEngine
from agent_factory.runtime.local_process import LocalProcessRuntime
from agent_factory.runtime.base import ExecutionLimits
from agent_factory.specs.schema import load_spec_from_yaml, save_spec_to_yaml, RiskClassification


FACTORY_ROOT = Path("D:/1_Hermes Working Folder_Directory/1_Projects/Agent Development Factory")
DATA_DIR = FACTORY_ROOT / "data"
WORKSPACES_DIR = FACTORY_ROOT / "workspaces"
RELEASES_DIR = FACTORY_ROOT / "releases"
DEPLOYMENT_DIR = FACTORY_ROOT / "deployments"
EVIDENCE_DIR = FACTORY_ROOT / "evidence"


def get_factory_context():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    DEPLOYMENT_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    registry = CapabilityRegistry(DATA_DIR / "capability_registry.json")
    ledger = TaskLedger(DATA_DIR / "factory_state.db", DATA_DIR / "task_events.jsonl")
    discovery = EnvironmentDiscovery(registry)
    ws_mgr = WorkspaceManager(WORKSPACES_DIR)
    lifecycle_mgr = AgentLifecycleManager(RELEASES_DIR, DEPLOYMENT_DIR)
    orchestrator = FactoryOrchestrator(WORKSPACES_DIR, ledger)

    return {
        "registry": registry,
        "ledger": ledger,
        "discovery": discovery,
        "ws_mgr": ws_mgr,
        "lifecycle_mgr": lifecycle_mgr,
        "orchestrator": orchestrator,
    }


def cmd_status(args):
    ctx = get_factory_context()
    reg = ctx["registry"]
    discovery = ctx["discovery"]

    # Discover capabilities if empty
    if not reg.list_all():
        discovery.discover_and_register_all()

    caps = reg.list_all()
    active_caps = [c for c in caps if c.status == "ACTIVE"]

    status_data = {
        "factory_status": "OPERATIONAL",
        "database": str(ctx["ledger"].db_path),
        "total_capabilities": len(caps),
        "active_capabilities": len(active_caps),
        "omniroute_port_20128": discovery.check_tcp_port("127.0.0.1", 20128),
        "freellmapi_port_31415": discovery.check_tcp_port("127.0.0.1", 31415),
    }

    if args.json:
        print(json.dumps(status_data, indent=2))
    else:
        print("==================================================")
        print("         Agent Development Factory Status         ")
        print("==================================================")
        print(f"Status:               {status_data['factory_status']}")
        print(f"Database:             {status_data['database']}")
        print(f"Active Capabilities:  {status_data['active_capabilities']} / {status_data['total_capabilities']}")
        print(f"OmniRoute (20128):    {'ONLINE' if status_data['omniroute_port_20128'] else 'OFFLINE'}")
        print(f"FreeLLMAPI (31415):   {'ONLINE' if status_data['freellmapi_port_31415'] else 'OFFLINE'}")
        print("==================================================")


def cmd_intake(args):
    ctx = get_factory_context()
    forced_risk = RiskClassification[args.risk.upper()] if args.risk else None
    res = RequestIntake.process_request(args.prompt, owner=args.owner, forced_risk=forced_risk)

    # Provision project workspace
    ws_dirs = ctx["ws_mgr"].provision_workspace(res.project_id)
    spec_path = ws_dirs["root"] / "agent.yaml"
    save_spec_to_yaml(res.spec, spec_path)

    # Record intake task in ledger
    ctx["ledger"].record_task(
        task_id=f"{res.project_id}_INTAKE",
        project_id=res.project_id,
        stage="INTAKE",
        status="COMPLETED",
        output_hash=res.spec.agent_id,
    )

    print(json.dumps({
        "project_id": res.project_id,
        "agent_id": res.agent_id,
        "risk_level": res.risk_level.value,
        "workspace": str(ws_dirs["root"]),
        "spec_file": str(spec_path),
    }, indent=2))


def cmd_build(args):
    ctx = get_factory_context()
    ws_dirs = ctx["ws_mgr"].provision_workspace(args.project_id)
    spec_path = ws_dirs["root"] / "agent.yaml"
    if not spec_path.exists():
        print(f"Error: agent.yaml not found in workspace: {ws_dirs['root']}", file=sys.stderr)
        sys.exit(1)

    spec = load_spec_from_yaml(spec_path)

    # 1. Synthesize agent source code
    code_res = CodeGenerator.generate_agent_code(spec, ws_dirs["src"])

    # 2. Synthesize test fixtures and test suite
    fix_res = TestGenerator.generate_fixtures(ws_dirs["fixtures"])
    test_file = TestGenerator.generate_test_suite(ws_dirs["tests"], ws_dirs["src"], ws_dirs["fixtures"])

    # Record BUILD stage completion in ledger
    ctx["ledger"].record_task(
        task_id=f"{args.project_id}_BUILD",
        project_id=args.project_id,
        stage="BUILD",
        status="COMPLETED",
        evidence_ref=str(test_file),
    )

    print(json.dumps({
        "project_id": args.project_id,
        "agent_id": spec.agent_id,
        "status": "BUILT",
        "source_files": [str(f) for f in code_res.values()],
        "test_suite": str(test_file),
        "fixtures": [str(f) for f in fix_res.values()],
    }, indent=2))


def cmd_test(args):
    ctx = get_factory_context()
    ws_dirs = ctx["ws_mgr"].provision_workspace(args.project_id)
    test_file = ws_dirs["tests"] / "test_agent.py"
    if not test_file.exists():
        print(f"Error: Test suite not found: {test_file}", file=sys.stderr)
        sys.exit(1)

    import subprocess
    cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ws_dirs["root"]))

    passed = (res.returncode == 0)
    ctx["ledger"].record_task(
        task_id=f"{args.project_id}_TEST",
        project_id=args.project_id,
        stage="TEST",
        status="COMPLETED" if passed else "FAILED",
        evidence_ref=res.stdout,
        error_message="" if passed else res.stderr,
    )

    print(json.dumps({
        "project_id": args.project_id,
        "passed": passed,
        "exit_code": res.returncode,
        "output": res.stdout,
    }, indent=2))
    if not passed:
        sys.exit(res.returncode)


def cmd_eval(args):
    ctx = get_factory_context()
    ws_dirs = ctx["ws_mgr"].provision_workspace(args.project_id)
    eval_runner = EvaluationRunner()
    scores = eval_runner.evaluate_candidate(ws_dirs, ws_dirs["evidence"])

    ctx["ledger"].record_task(
        task_id=f"{args.project_id}_EVALUATE",
        project_id=args.project_id,
        stage="EVALUATE",
        status="COMPLETED" if scores.passed else "FAILED",
        evidence_ref=json.dumps(scores.model_dump(mode="json")),
    )

    print(json.dumps(scores.model_dump(mode="json"), indent=2))


def cmd_package(args):
    ctx = get_factory_context()
    ws_dirs = ctx["ws_mgr"].provision_workspace(args.project_id)
    spec_path = ws_dirs["root"] / "agent.yaml"
    spec = load_spec_from_yaml(spec_path)

    token = args.token or "AUTO_APPROVED_LOW_RISK"
    pkg_res = ReleasePackager.package_release(
        spec=spec,
        workspace_dirs=ws_dirs,
        releases_dir=RELEASES_DIR,
        approval_token=token,
    )

    ctx["ledger"].record_task(
        task_id=f"{args.project_id}_PACKAGE",
        project_id=args.project_id,
        stage="PACKAGE",
        status="COMPLETED",
        output_hash=pkg_res["sha256"],
        evidence_ref=pkg_res["bundle_path"],
    )

    print(json.dumps(pkg_res, indent=2))


def cmd_deploy(args):
    ctx = get_factory_context()
    ws_dirs = ctx["ws_mgr"].provision_workspace(args.project_id)
    spec = load_spec_from_yaml(ws_dirs["root"] / "agent.yaml")

    res = ctx["lifecycle_mgr"].deploy_release(spec.agent_id, spec.version, target=args.target)
    print(json.dumps(res, indent=2))


def cmd_run(args):
    ctx = get_factory_context()
    target_dir = DEPLOYMENT_DIR / args.agent_id / "src"
    entrypoint = target_dir / "__main__.py"
    if not entrypoint.exists():
        print(f"Error: Deployed agent entrypoint not found: {entrypoint}", file=sys.stderr)
        sys.exit(1)

    rt = LocalProcessRuntime()
    limits = ExecutionLimits(max_wall_time_seconds=60)
    res = rt.execute(
        entrypoint_script=entrypoint,
        args=[args.input, args.outdir or "artifacts", str(args.threshold or 3.0)],
        limits=limits,
        workdir=DEPLOYMENT_DIR / args.agent_id,
    )
    print(json.dumps(res.model_dump(mode="json"), indent=2))


def main():
    parser = argparse.ArgumentParser(description="Agent Development Factory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Show factory health and registered capabilities")
    p_status.add_argument("--json", action="store_true")
    p_status.set_defaults(func=cmd_status)

    # intake
    p_intake = subparsers.add_parser("intake", help="Ingest agent requirement")
    p_intake.add_argument("prompt", help="Requirement description")
    p_intake.add_argument("--owner", default="Admin")
    p_intake.add_argument("--risk", choices=["low", "medium", "high"], default="low")
    p_intake.set_defaults(func=cmd_intake)

    # build
    p_build = subparsers.add_parser("build", help="Synthesize agent code and tests")
    p_build.add_argument("project_id")
    p_build.set_defaults(func=cmd_build)

    # test
    p_test = subparsers.add_parser("test", help="Run automated unit tests in workspace")
    p_test.add_argument("project_id")
    p_test.set_defaults(func=cmd_test)

    # eval
    p_eval = subparsers.add_parser("eval", help="Run independent evaluation suite")
    p_eval.add_argument("project_id")
    p_eval.set_defaults(func=cmd_eval)

    # package
    p_package = subparsers.add_parser("package", help="Create reproducible release bundle")
    p_package.add_argument("project_id")
    p_package.add_argument("--token", default=None)
    p_package.set_defaults(func=cmd_package)

    # deploy
    p_deploy = subparsers.add_parser("deploy", help="Deploy release to local target")
    p_deploy.add_argument("project_id")
    p_deploy.add_argument("--target", default="local_process")
    p_deploy.set_defaults(func=cmd_deploy)

    # run
    p_run = subparsers.add_parser("run", help="Execute deployed agent")
    p_run.add_argument("agent_id")
    p_run.add_argument("--input", required=True)
    p_run.add_argument("--outdir", default=None)
    p_run.add_argument("--threshold", type=float, default=3.0)
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
