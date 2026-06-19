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
# Recommended: install globally with pipx (isolated deps, command on PATH)
pipx install agent-leash        # or: pip install --user agent-leash

# 1. run the relay
agent-leash-relay

# 2. register the hook in ~/.claude/settings.json (see examples/)
#    ⚠️ use the ABSOLUTE path to the hook — see note below

# 3. get phone pushes via ntfy (free, no account):
export AGENT_LEASH_NTFY_TOPIC="your-unique-topic-name"
#    install the "ntfy" app and subscribe to that topic
```

> **Use the absolute path for the hook command in `settings.json`.** The Claude
> **Desktop app** spawns hooks with a *limited* `PATH`, so a bare `agent-leash-hook`
> can fail to resolve there. Find the real path with `which agent-leash-hook`
> (e.g. `~/.local/bin/agent-leash-hook` after a pipx install) and use that exact
> path in the hook's `command`.

Now run Claude Code — when it wants to run a tool, your phone buzzes; tap the
link and decide.

> 📱 **Using a real phone (not localhost)?** See **[DEPLOY.md](DEPLOY.md)** for
> exposing the relay via Tailscale / Cloudflare Tunnel / ngrok — and **always set
> `AGENT_LEASH_TOKEN`** when you do.

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

## Where to enable it (scope)

Install once, run **one** relay — then **where you register the hook decides what it guards.** It plugs into Claude Code's `PreToolUse` hook and works with **both the Claude Desktop app and the CLI** (both read these settings).

| Put the hook in… | Guards | Use for |
|---|---|---|
| `~/.claude/settings.json` (**global**) | every session, every project | supervise *all* agent shell commands |
| `<project>/.claude/settings.json` (**project**) | only sessions opened in that project | guard one repo (prod / infra / trading) |
| `<project>/.claude/settings.local.json` (**local**) | that project, just you (uncommitted) | personal, per-repo |

- A session loads hooks **at startup**, and only from its **project root** — *not* subfolders. Open the session in the folder whose settings has the hook, and restart after editing settings.
- Only **Bash** is gated by the example matcher; read-only tools are auto-approved — so you're pinged for shell commands, not every file read.
- **Recommended:** per-project on sensitive repos for day-to-day work; global when you're letting an agent run on its own.

## Gotchas

- **Long-running servers block.** Approving `npm run dev` makes Claude's terminal wait on a process that never exits — that's normal, *not* agent-leash. Ask Claude to start servers **in the background**.
- **Keep the relay up.** If it's down, gated commands fall back to Claude's normal in-app prompt (graceful, not broken). For always-on, run the relay as a service — see [DEPLOY.md](DEPLOY.md).

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
