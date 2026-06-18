# 🐕 agent-leash

> **Approve, reject — or correct — your AI coding agent's actions from your phone.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

Claude Code keeps asking for permission, so you either babysit the terminal or
approve everything blindly. **agent-leash** lets you hold the reins from your
phone: when the agent wants to run a tool, you get a push notification, tap a
link, and **Approve**, **Reject with a correction**, or even **edit the command** —
then it keeps going.

No native app. No forking Claude Code. It plugs into Claude Code's built-in
**`PreToolUse` hook** and relays the decision through a tiny self-hosted server.

> ⚠️ **Alpha / work in progress.** Core scaffold is in place; see [HANDOFF.md](HANDOFF.md) for status and the build plan.

---

## How it works

```
Claude Code (laptop)
  └─ PreToolUse hook → agent-leash relay → push to your phone
       └─ you tap: ✅ Approve · ❌ Reject (+ correction) · ✏️ Edit command
  └─ decision returns to Claude → it proceeds, stops, or adjusts
```

- **Approve** → the tool runs.
- **Reject + correction** → blocked, and your note is fed back to Claude as guidance.
- **Edit input** → rewrites the command before it runs (`updatedInput`).
- **Auto-allow** read-only tools (Read/Glob/Grep) so you're only pinged for the risky stuff.

---

## Quickstart (local loop)

```bash
pip install agent-leash         # (once published; for now: pip install -e .)

# 1. run the relay
agent-leash-relay

# 2. register the hook in ~/.claude/settings.json
#    (see examples/claude-settings-snippet.json)

# 3. get phone pushes via ntfy (free, no account):
export AGENT_LEASH_NTFY_TOPIC="your-unique-topic-name"
#    install the "ntfy" app and subscribe to that topic
```

Now run Claude Code — when it wants to run a tool, your phone buzzes; tap the
link and decide.

### Config (env vars)
| Var | Default | Purpose |
|---|---|---|
| `AGENT_LEASH_TOKEN` | — | shared secret protecting the relay — **set this before exposing the relay beyond localhost** |
| `AGENT_LEASH_RELAY_URL` | `http://127.0.0.1:8787` | where the hook reaches the relay |
| `AGENT_LEASH_PUBLIC_URL` | = relay url | public link used in the push (use a tunnel/VPS for a remote phone) |
| `AGENT_LEASH_TIMEOUT` | `300` | seconds to wait for a decision (keep < hook's 600s) |
| `AGENT_LEASH_ON_TIMEOUT` | `deny` | fallback if no answer: `deny` or `allow` |
| `AGENT_LEASH_NTFY_TOPIC` | — | ntfy topic for push |
| `AGENT_LEASH_TELEGRAM_BOT_TOKEN` / `_CHAT_ID` | — | Telegram backend (alt to ntfy) |
| `AGENT_LEASH_AUTO_ALLOW` | `Read,Glob,Grep,LS` | tools approved without pinging the phone |

---

## Why not just…
- **`--dangerously-skip-permissions`?** That approves *everything*, blind. This keeps you in control of the risky calls only.
- **Allowlists in settings.json?** Great for known-safe commands — use both. agent-leash covers the *unpredictable* calls you can't pre-list, while away from the keyboard.
- **A mobile app?** Unnecessary — a push + web page does the job and stays installable in seconds.

---

## Status & roadmap

Core relay + hook are scaffolded. Next: tests + CI, a remote-tunnel guide, an
auth token on the relay, and a demo. See **[HANDOFF.md](HANDOFF.md)**.

- [ ] End-to-end tested in Claude Code with phone approval
- [ ] Auth token on relay endpoints
- [ ] Tunnel/VPS guide for remote phones
- [ ] Demo GIF
- [ ] Support more agents (Cursor, Cline) via the same relay

## License

[MIT](LICENSE) © Kannan Dharmalingam
