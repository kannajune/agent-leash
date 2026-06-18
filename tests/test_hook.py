"""Hook behavior tests — run the hook as a subprocess with piped stdin."""
import json
import os
import subprocess
import sys


def _run_hook(event: dict, env_extra: dict | None = None, timeout: int = 30) -> dict:
    env = {**os.environ, **(env_extra or {})}
    proc = subprocess.run(
        [sys.executable, "-m", "agent_leash.hook"],
        input=json.dumps(event),
        capture_output=True, text=True, env=env, timeout=timeout,
    )
    # The decision JSON is the last non-empty stdout line.
    line = [ln for ln in proc.stdout.splitlines() if ln.strip()][-1]
    return json.loads(line)["hookSpecificOutput"]


def test_auto_allow_safe_tool():
    out = _run_hook({"tool_name": "Read", "tool_input": {"file_path": "x"}, "cwd": "/tmp"})
    assert out["permissionDecision"] == "allow"
    assert "auto-approved" in out["permissionDecisionReason"]


def test_relay_unreachable_falls_back_to_ask():
    out = _run_hook(
        {"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "/tmp"},
        env_extra={"AGENT_LEASH_RELAY_URL": "http://127.0.0.1:9", "AGENT_LEASH_AUTO_ALLOW": ""},
    )
    assert out["permissionDecision"] == "ask"
    assert "unreachable" in out["permissionDecisionReason"]
