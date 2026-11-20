"""
Unit tests for Workbench: Workspace Provisioning, Code Gen, Test Gen, and Release Packager.
"""

from pathlib import Path
from agent_factory.workbench.workspace import WorkspaceManager
from agent_factory.workbench.code_generator import CodeGenerator
from agent_factory.workbench.test_generator import TestGenerator
from agent_factory.workbench.packager import ReleasePackager
from agent_factory.control_plane.intake import RequestIntake


def test_workspace_provisioning(tmp_path):
    mgr = WorkspaceManager(tmp_path / "workspaces")
    dirs = mgr.provision_workspace("proj_101")

    for key in ["root", "src", "tests", "fixtures", "artifacts", "evidence"]:
        assert key in dirs
        assert dirs[key].exists()


def test_code_and_test_generation(tmp_path):
    mgr = WorkspaceManager(tmp_path / "workspaces")
    dirs = mgr.provision_workspace("proj_102")

    intake = RequestIntake.process_request("CSV Anomaly Analyzer")
    code_res = CodeGenerator.generate_agent_code(intake.spec, dirs["src"])

    assert dirs["src"] / "agent.py" in code_res.values()
    assert (dirs["src"] / "agent.py").exists()

    fixtures = TestGenerator.generate_fixtures(dirs["fixtures"])
    assert fixtures["clean"].exists()
    assert fixtures["anomalous"].exists()

    test_file = TestGenerator.generate_test_suite(dirs["tests"], dirs["src"], dirs["fixtures"])
    assert test_file.exists()
    assert "test_anomalous_dataset_analysis" in test_file.read_text(encoding="utf-8")


def test_release_packager(tmp_path):
    mgr = WorkspaceManager(tmp_path / "workspaces")
    dirs = mgr.provision_workspace("proj_103")

    intake = RequestIntake.process_request("CSV Anomaly Analyzer")
    CodeGenerator.generate_agent_code(intake.spec, dirs["src"])
    TestGenerator.generate_fixtures(dirs["fixtures"])
    TestGenerator.generate_test_suite(dirs["tests"], dirs["src"], dirs["fixtures"])

    releases_dir = tmp_path / "releases"
    pkg = ReleasePackager.package_release(
        spec=intake.spec,
        workspace_dirs=dirs,
        releases_dir=releases_dir,
        approval_token="AUTO_APPROVED_LOW_RISK",
    )

    bundle_path = Path(pkg["bundle_path"])
    assert bundle_path.exists()
    assert pkg["sha256"] is not None
    assert pkg["manifest"]["approval_token"] == "AUTO_APPROVED_LOW_RISK"
