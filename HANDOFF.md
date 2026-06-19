# agent-leash — Session Handoff / Build Doc

> **Read this first.** This is a fresh-session handoff for continuing the build.
> Project lives at `/Users/kd/Sid/agentic-base/agent-leash/`. Owner GitHub: **kannajune**.

---

## What this is & why

**The problem:** Claude Code (and other AI coding agents) constantly ask for
permission to run tools. Today you must sit at the laptop to approve. People
either babysit it or `--dangerously-skip-permissions` (approve everything).

**The idea:** approve/reject — *and correct* — the agent's actions **from your
phone**, so you can let it run while away from the keyboard without blindly
approving everything.

**Key decision: NOT a native iOS/Android app.** We plug into Claude Code's
built-in **`PreToolUse` hook** and use a tiny relay + a phone-friendly **web
page** (delivered via ntfy or Telegram push). The phone just opens a link.

---

## Verified Claude Code facts (checked vs docs, June 16 2026)

- **No native remote-approval feature exists.** Claude Code has "Remote Control"
  (steer a running session from phone/web) but it does **not** approve permission
  prompts remotely. → our niche is real and unfilled.
- **`PreToolUse` hook can allow/deny/ask.** Output contract:
  ```json
  { "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow" | "deny" | "ask",
      "permissionDecisionReason": "string",
      "updatedInput": { }   // OPTIONAL: rewrite the tool input before it runs
  }}
  ```
- **The hook is blocking/synchronous** — Claude waits for it. So it can
  **long-poll** a relay until the phone responds. **Default timeout: 600s (10 min)**,
  configurable per-hook via `"timeout"`. Keep our wait under that.
- **`deny` + `permissionDecisionReason` is fed BACK to Claude** as guidance →
  this is how "reject with a correction / rewrite" works. `updatedInput` lets the
  phone edit the actual command.
- **Deny rules in `settings.json` always win** over a hook's `allow` (safety floor).
- **`Notification` hook** (matcher `permission_prompt`) can *alert* but **cannot
  approve** — so `PreToolUse` is the right integration point.
- Docs: https://code.claude.com/docs/en/hooks.md · /hooks-guide.md · /permissions.md

---

## Architecture

```
Claude Code (laptop)
  └─ PreToolUse hook = `agent-leash-hook` (reads tool JSON on stdin)
       ├─ auto-allow safe tools (Read/Glob/Grep/LS) -> return allow immediately
       └─ else: POST /request to relay  ──────────────┐
                                                       ▼
                                         agent-leash relay (FastAPI)
                                           ├─ sends push (ntfy / Telegram) with a link
                                           └─ serves mobile approval page  /r/{id}
                                                       ▲
   hook long-polls GET /decision/{id} ────────────────┘   (you tap on phone:
       └─ returns {allow|deny, reason, updatedInput}        Approve / Reject+correct / Edit input)
  └─ Claude proceeds / blocks / adjusts
```

---

## File map (already scaffolded)

```
agent-leash/
├── HANDOFF.md                     ← this file
├── README.md                      ← user-facing
├── LICENSE                        ← MIT
├── pyproject.toml                 ← console scripts: agent-leash-relay, agent-leash-hook
├── examples/claude-settings-snippet.json   ← how to register the hook
├── src/agent_leash/
│   ├── config.py                  ← env-var config (relay url, timeout, ntfy/telegram, auto-allow)
│   ├── notify.py                  ← send push (ntfy + telegram), stdlib-only
│   ├── relay.py                   ← FastAPI relay: /request /decision/{id} /r/{id}
│   └── hook.py                    ← PreToolUse hook: stdin -> relay -> hookSpecificOutput
└── tests/                         ← EMPTY — needs tests
```

---

## Status

### Done (scaffold) — LOCAL LOOP VERIFIED WORKING ✅
- [x] Project structure, pyproject (pip/uvx installable), MIT, .gitignore
- [x] `config.py`, `notify.py` (ntfy + Telegram), `relay.py` (FastAPI + mobile page), `hook.py`
- [x] Example Claude settings snippet
- [x] Verified the Claude Code hook contract
- [x] `python-multipart` added to deps (relay Form endpoints need it)
- [x] **Smoke-tested end-to-end** in a `.venv`: relay starts; hook auto-allows safe tools;
      hook posts→polls; "phone" reject-with-correction returns `deny` + reason to the hook;
      relay-down falls back to `ask`. All confirmed working.

### Also done (in PRs / merged)
- [x] **Tests + CI** (`tests/`, `.github/workflows/ci.yml`) — relay request→decide→poll,
      allow/deny-with-correction, edited-input, 404s, page render; hook auto-allow +
      relay-unreachable fallback. CI on Python 3.10 & 3.12. (branch `feat/tests-ci`)
- [x] **Auth token** — `AGENT_LEASH_TOKEN` shared secret guards every relay endpoint
      (header for the hook, `?t=` for the phone link); relay warns if running open.
      (branch `feat/auth-token`)

### Status update (verified)
- ✅ **End-to-end proven** in real Claude Code (CLI `claude -p`) — phone push → approve → command runs. Tested twice incl. the live trading project.
- ✅ Auth token, bind-host (`AGENT_LEASH_HOST/PORT`), tests + CI, scope/usage docs, pipx-install docs — all merged to `main`.
- ✅ Confirmed: hooks load at **session start**, from the **project root only** (not subfolders); works in **both** the Desktop app and CLI; only **Bash** gated.
- ⚠️ Gotcha learned: approving a **long-running server** (`npm run dev`) blocks Claude's terminal (server never exits) — run servers in the background.

### TODO (next session, in order)
1. **Record the demo GIF** — re-run a gated command while screen-recording phone (approve) + terminal (Claude continues). Launch visual.
2. **Publish** — follow `/Users/kd/Sid/agentic-base/PLAYBOOK.md` (PyPI first release = **0.1.0**, then awesome-list + Glama), like mcp-architect. (Release artifacts may already be built in `dist/`.)
3. **Nice-to-haves**: expire old pending requests; optional allow/deny rules by command pattern; launchd service for an always-on relay.

### Future idea — npm port (after the Python version has traction)
Reimplement as an **npm package** so Node users can `npx agent-leash-hook` with **zero Python**:
- Hook = ~30 lines of JS (read stdin → HTTP POST/poll relay → print the `hookSpecificOutput` JSON).
- Relay = a small Express app mirroring `/request`, `/decision/{id}`, `/r/{id}`.
- Why: a huge share of Claude Code users live in Node-land; `npx` is friction-free → wider adoption. Treat as a sister package / v2.

---

## Decisions already made
- **Name:** `agent-leash` (control metaphor; "you hold the reins remotely").
- **Open source, MIT.** Paid is premature; would kill trust/adoption for a
  security-adjacent tool. Future "open-core" monetization = hosted relay / team
  audit logs — NOT now.
- **Start with Claude Code** (its hooks expose the exact integration point).
  Keep the relay + phone side **agent-agnostic** so Cursor/Cline/Aider can be added later.
- **No native app** — phone web page delivered via ntfy/Telegram.
- **Phone actions:** Approve · Reject (with correction text → fed to Claude) · Edit input (JSON → `updatedInput`).
- **Safety:** auto-allow read-only tools; fallback on timeout/relay-down = `deny` (configurable); deny rules in settings still win.

---

## How to run the local loop (quick)
```bash
cd /Users/kd/Sid/agentic-base/agent-leash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
# terminal 1: relay
.venv/bin/agent-leash-relay
# terminal 2: simulate a hook call
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf build"},"cwd":"/tmp"}' \
  | AGENT_LEASH_RELAY_URL=http://127.0.0.1:8787 .venv/bin/agent-leash-hook
# open the printed approve URL in a browser, click Approve/Reject, watch the hook return.
```
Set `AGENT_LEASH_NTFY_TOPIC=<your-unique-topic>` and install the **ntfy** app to get phone pushes.

---

## Risks / open questions
- Claude Code hook API could change — pin to the documented contract; OSS lets community track it.
- 10-min hook timeout bounds how long it can wait for the phone.
- Relay sees tool calls (sensitive) → must add auth + encourage self-host; never log full inputs by default.
- Adoption uncertain — but MVP is cheap; validate with the phone demo before investing more.

---

## agentic-base context (for the new session)
- This is **project #2** under `/Users/kd/Sid/agentic-base/` (project #1 = `mcp-architect`, already published: GitHub + PyPI + Glama).
- **Follow the OSS launch playbook:** `/Users/kd/Sid/agentic-base/PLAYBOOK.md` — it documents the exact, battle-tested steps (build → test → public GitHub repo via SSH → PyPI `twine upload` → awesome-list PR with Glama badge → CI → launch posts). Reuse it.
- **Git/GitHub gotcha (important):** this Mac has a cached HTTPS login for a different account (`git-aman11`). **Always use SSH remotes** (`git@github.com:kannajune/agent-leash.git`) so pushes go out as `kannajune`. SSH key is already set up.
- **PR practice even solo:** branch → PR → CI green → merge (the owner liked this).
- Commit identity: `Kannan Dharmalingam <kannajune@gmail.com>`. **No Claude attribution in commit messages** (owner preference).
- When ready to publish: create an **empty PUBLIC repo** `kannajune/agent-leash` on GitHub (owner does this), then push via SSH.
