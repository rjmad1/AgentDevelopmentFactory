"""
Unit tests for Local Process Runtime Execution and Sandboxing.
"""

from pathlib import Path
from agent_factory.runtime.local_process import LocalProcessRuntime
from agent_factory.runtime.base import ExecutionLimits


def test_local_process_runtime_success(tmp_path):
    script = tmp_path / "hello.py"
    script.write_text("print('HELLO_FACTORY_TEST')", encoding="utf-8")

    rt = LocalProcessRuntime()
    limits = ExecutionLimits(max_wall_time_seconds=10)
    res = rt.execute(script, [], limits, tmp_path)

    assert res.success is True
    assert res.exit_code == 0
    assert "HELLO_FACTORY_TEST" in res.stdout
    assert res.duration_ms > 0


def test_local_process_runtime_timeout(tmp_path):
    script = tmp_path / "infinite_loop.py"
    script.write_text("import time\ntime.sleep(10)", encoding="utf-8")

    rt = LocalProcessRuntime()
    limits = ExecutionLimits(max_wall_time_seconds=1)
    res = rt.execute(script, [], limits, tmp_path)

    assert res.success is False
    assert res.exit_code == 124
    assert "timed out" in res.stderr
