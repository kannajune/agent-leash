"""Claude Code PreToolUse hook entry point.

Reads the tool-call JSON from stdin, asks for remote approval via the relay, and
prints a PreToolUse `hookSpecificOutput` decision to stdout.

Register in ~/.claude/settings.json:

  "hooks": {
    "PreToolUse": [
      { "matcher": "*", "hooks": [
        { "type": "command", "command": "agent-leash-hook", "timeout": 600 }
      ]}
    ]
  }

Decision contract (per Claude Code docs):
  { "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow" | "deny" | "ask",
      "permissionDecisionReason": "...",
      "updatedInput": { ... }   # optional, rewrites the tool input
  }}
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request

from . import config


def _decision(kind: str, reason: str = "", updated_input: dict | None = None) -> None:
    out: dict = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": kind,
            "permissionDecisionReason": reason,
        }
    }
    if updated_input is not None:
        out["hookSpecificOutput"]["updatedInput"] = updated_input
    print(json.dumps(out))
    sys.exit(0)


def _http_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read() or "{}")


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        _decision("ask")  # malformed input -> fall back to the normal prompt

    tool = event.get("tool_name", "?")
    tool_input = event.get("tool_input", {})

    # Auto-approve known-safe tools without bothering the phone.
    if tool in config.AUTO_ALLOW_TOOLS:
        _decision("allow", "auto-approved by agent-leash policy")

    # Register the request with the relay.
    try:
        created = _http_json(
            f"{config.RELAY_URL}/request",
            {"tool": tool, "input": tool_input, "cwd": event.get("cwd", "")},
        )
        rid = created["id"]
    except Exception as exc:  # noqa: BLE001 - relay down -> fall back to normal prompt
        _decision("ask", f"agent-leash relay unreachable ({exc}); falling back")

    # Poll for the phone decision.
    deadline = time.time() + config.DECISION_TIMEOUT
    while time.time() < deadline:
        try:
            d = _http_json(f"{config.RELAY_URL}/decision/{rid}")
        except Exception:
            time.sleep(2)
            continue
        if d.get("status") == "decided":
            if d["decision"] == "allow":
                _decision("allow", "approved from phone", d.get("updated_input"))
            else:
                reason = d.get("reason") or "rejected from phone"
                _decision("deny", reason)
        time.sleep(2)

    # No decision in time -> configured fallback.
    if config.ON_TIMEOUT == "allow":
        _decision("allow", "agent-leash timeout -> auto-allow")
    _decision("deny", "agent-leash timeout -> no approval received")


if __name__ == "__main__":
    main()
