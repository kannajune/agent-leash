"""Configuration for agent-leash, read from environment variables.

Keep it dependency-light: just env vars (optionally loaded from a .env by the
caller). Defaults make the local-only loop work out of the box.
"""
from __future__ import annotations

import os


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


# Shared secret protecting the relay. Set the SAME value in the relay's env and
# the hook's env. When empty the relay runs open (fine for localhost-only); set
# it before exposing the relay beyond your machine (tunnel / VPS).
TOKEN = _env("AGENT_LEASH_TOKEN", "")

# Where the hook reaches the relay (the relay runs on your laptop or a small VPS).
RELAY_URL = _env("AGENT_LEASH_RELAY_URL", "http://127.0.0.1:8787")

# Address/port the relay binds to. 127.0.0.1 = localhost only; set HOST=0.0.0.0
# to accept connections from your phone (LAN IP / tunnel). Always set a TOKEN then.
HOST = _env("AGENT_LEASH_HOST", "127.0.0.1")
PORT = int(_env("AGENT_LEASH_PORT", "8787"))

# How long the hook waits for a phone decision before falling back (seconds).
# Must stay under Claude Code's PreToolUse hook timeout (default 600s).
DECISION_TIMEOUT = int(_env("AGENT_LEASH_TIMEOUT", "300"))

# What to do if no decision arrives before the timeout: "deny" (safe) or "allow".
ON_TIMEOUT = _env("AGENT_LEASH_ON_TIMEOUT", "deny")

# Public base URL of the relay used to build the phone approval link.
# For remote phones this must be reachable (e.g., a tunnel or VPS URL).
PUBLIC_URL = _env("AGENT_LEASH_PUBLIC_URL", RELAY_URL)

# --- Notification backend (how the phone gets pinged) ---
# ntfy: set AGENT_LEASH_NTFY_TOPIC (uses ntfy.sh unless NTFY_SERVER overrides).
NTFY_SERVER = _env("AGENT_LEASH_NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = _env("AGENT_LEASH_NTFY_TOPIC", "")

# Telegram: set both to enable.
TELEGRAM_BOT_TOKEN = _env("AGENT_LEASH_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = _env("AGENT_LEASH_TELEGRAM_CHAT_ID", "")

# Tools that are always safe to auto-approve without pinging the phone.
# Comma-separated tool names, e.g. "Read,Glob,Grep".
AUTO_ALLOW_TOOLS = {
    t.strip() for t in _env("AGENT_LEASH_AUTO_ALLOW", "Read,Glob,Grep,LS").split(",") if t.strip()
}
