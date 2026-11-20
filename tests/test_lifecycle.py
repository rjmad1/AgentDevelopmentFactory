"""
Unit tests for Agent Lifecycle: Deployment, Suspension, Rollback, and Retirement.
"""

from pathlib import Path
from agent_factory.control_plane.lifecycle import AgentLifecycleManager
from agent_factory.workbench.workspace import WorkspaceManager
from agent_factory.workbench.code_generator import CodeGenerator
from agent_factory.workbench.test_generator import TestGenerator
from agent_factory.workbench.packager import ReleasePackager
from agent_factory.control_plane.intake import RequestIntake


def test_agent_lifecycle_flow(tmp_path):
    releases_dir = tmp_path / "releases"
    deploy_dir = tmp_path / "deployments"
    ws_dir = tmp_path / "workspaces"

    mgr = WorkspaceManager(ws_dir)
    dirs = mgr.provision_workspace("proj_lc_01")
    intake = RequestIntake.process_request("CSV Anomaly Analyzer")

    CodeGenerator.generate_agent_code(intake.spec, dirs["src"])
    TestGenerator.generate_fixtures(dirs["fixtures"])
    TestGenerator.generate_test_suite(dirs["tests"], dirs["src"], dirs["fixtures"])

    # Package v1.0.0
    ReleasePackager.package_release(
        spec=intake.spec,
        workspace_dirs=dirs,
        releases_dir=releases_dir,
        approval_token="AUTO_APPROVED_LOW_RISK",
    )

    lc_mgr = AgentLifecycleManager(releases_dir, deploy_dir)

    # 1. Deploy
    dep_res = lc_mgr.deploy_release(intake.spec.agent_id, "1.0.0")
    assert dep_res["success"] is True
    deployed_dir = Path(dep_res["deployed_to"])
    assert (deployed_dir / "src" / "agent.py").exists()

    # 2. Suspend
    sus_res = lc_mgr.suspend(intake.spec.agent_id, reason="Maintenance drill")
    assert sus_res["status"] == "SUSPENDED"
    assert (deployed_dir / "SUSPENDED").exists()

    # 3. Rollback
    rb_res = lc_mgr.rollback(intake.spec.agent_id, "1.0.0")
    assert rb_res["success"] is True

    # 4. Retire
    ret_res = lc_mgr.retire(intake.spec.agent_id)
    assert ret_res["status"] == "RETIRED"
    assert not deployed_dir.exists()
