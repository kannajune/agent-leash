# awesome-claude-code submission (ready to paste)

**List:** https://github.com/hesreallyhim/awesome-claude-code (~47k ⭐)
**Submit via:** the GitHub UI issue form → https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml
**⚠️ DO NOT submit before ~2026-06-26** — their rule: resources must be **at least one week old** (steerd published 2026-06-19). And it must be submitted **by a human via the github.com UI** (gh CLI / programmatic submission is auto-closed and violates their Code of Conduct).

## Before submitting — add a demo GIF to the README
Their template: *"if I can see it in action before running it, you're way ahead."* Record the phone-approval loop (phone approves → Claude continues) and embed it in the README first.

---

## Fields to enter in the form

- **Display Name:** `steerd`
- **Category:** `Hooks`
- **Sub-Category:** `General`
- **Primary Link:** `https://github.com/kannajune/steerd`

**Description:**
> A `PreToolUse` hook that relays tool-permission requests to your phone (via ntfy or Telegram) so you can **approve, reject-with-a-correction, or edit** an AI agent's action from anywhere — instead of approving everything blind. Self-hosted relay, auth-token protected, per-project or global scope. Read-only tools auto-approved.

**Network requests (REQUIRED disclosure):**
> The self-hosted relay sends a push notification via **ntfy.sh** (or **Telegram** — user's choice) when approval is needed. The hook only talks to **your local relay** (`localhost`). No calls to any third party besides the push-notification service the user configures; no telemetry.

**Install / Uninstall:**
> Install: `pipx install steerd`, run `steerd-relay`, add the `PreToolUse` hook to `settings.json` (see README/examples). Uninstall: remove the hook block from `settings.json` and `pipx uninstall steerd`.

**Dangerous permissions:** No — steerd *adds* an approval gate; it does **not** use `--dangerously-skip-permissions` (it makes agents safer, not riskier).

**Demo:** link the README demo GIF.

---

## Checklist before submitting
- [ ] steerd is ≥ 1 week old (on/after 2026-06-26)
- [ ] Demo GIF in the README
- [ ] Submitting via the github.com UI form (not gh CLI), logged in as a human
- [ ] Paste the fields above
