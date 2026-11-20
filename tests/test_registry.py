"""
Unit tests for Unified Capability Registry and Environment Discovery.
"""

from pathlib import Path
from agent_factory.registry.capability_registry import (
    CapabilityRegistry,
    CapabilityRecord,
    CapabilityKind,
    CapabilityStatus,
)
from agent_factory.registry.discovery import EnvironmentDiscovery


def test_registry_registration_and_query(tmp_path):
    reg_file = tmp_path / "test_reg.json"
    reg = CapabilityRegistry(reg_file)

    rec = CapabilityRecord(
        id="cap_tool_test",
        kind=CapabilityKind.TOOL,
        name="test_tool",
        status=CapabilityStatus.ACTIVE,
        permissions_required=["READ_PUBLIC"],
        metadata={"category": "testing"},
    )
    reg.register(rec)

    fetched = reg.get("cap_tool_test")
    assert fetched is not None
    assert fetched.name == "test_tool"
    assert fetched.status == CapabilityStatus.ACTIVE

    # Query by kind
    tools = reg.list_all(kind=CapabilityKind.TOOL)
    assert len(tools) == 1
    assert tools[0].id == "cap_tool_test"

    # Resolve with criteria
    resolved = reg.resolve(CapabilityKind.TOOL, {"category": "testing"})
    assert len(resolved) == 1

    # Deprecate
    reg.deprecate("cap_tool_test", reason="replaced")
    dep = reg.get("cap_tool_test")
    assert dep.status == CapabilityStatus.DEPRECATED

    # Persistence reload test
    reg_reloaded = CapabilityRegistry(reg_file)
    assert reg_reloaded.get("cap_tool_test") is not None


def test_environment_discovery(tmp_path):
    reg = CapabilityRegistry(tmp_path / "live_reg.json")
    discovery = EnvironmentDiscovery(reg)
    summary = discovery.discover_and_register_all()

    assert "python" in summary["runtimes"]
    assert "git" in summary["tools"] or "local_process" in summary["runtimes"]

    # Check local process runtime capability
    local_rt = reg.get("cap_runtime_local_process")
    assert local_rt is not None
    assert local_rt.status == CapabilityStatus.ACTIVE
