# Making the relay reachable from your phone

The hook talks to the relay over `AGENT_LEASH_RELAY_URL` (usually
`http://127.0.0.1:8787` on the same machine). But the **push notification link**
your phone opens uses `AGENT_LEASH_PUBLIC_URL` — and that must be reachable from
your phone. Pick one option below.

> 🔐 **Always set `AGENT_LEASH_TOKEN` to a strong secret before exposing the relay.**
> Without it the relay is open to anyone who can reach the URL.

The relay always listens locally; only the *public URL* differs. Common setup:

```bash
export AGENT_LEASH_TOKEN="$(openssl rand -hex 24)"   # share this with the hook too
export AGENT_LEASH_NTFY_TOPIC="your-unique-topic"
# AGENT_LEASH_RELAY_URL stays http://127.0.0.1:8787 (hook -> relay, local)
# AGENT_LEASH_PUBLIC_URL = the reachable URL below (phone -> relay)
agent-leash-relay
```

Set the **same** `AGENT_LEASH_TOKEN` (and `AGENT_LEASH_PUBLIC_URL` if needed) in
the environment Claude Code runs the hook from.

---

## Option A — Tailscale (most secure, recommended)
Put your laptop and phone on the same [Tailscale](https://tailscale.com) tailnet;
no public exposure at all.

```bash
export AGENT_LEASH_PUBLIC_URL="http://<your-laptop-tailscale-ip>:8787"
agent-leash-relay
```
Your phone opens the link over the private tailnet. Still set a token.

## Option B — Cloudflare Tunnel (quick public HTTPS, no account)
```bash
# terminal 1
agent-leash-relay
# terminal 2 — prints a https://<random>.trycloudflare.com URL
cloudflared tunnel --url http://localhost:8787
```
```bash
export AGENT_LEASH_PUBLIC_URL="https://<random>.trycloudflare.com"
```
Restart the relay so new requests build links with the public URL. **Token is mandatory here** — this URL is on the public internet.

## Option C — ngrok
```bash
ngrok http 8787          # prints https://<id>.ngrok-free.app
export AGENT_LEASH_PUBLIC_URL="https://<id>.ngrok-free.app"
```

## Option D — small VPS
Run `agent-leash-relay` on a VPS, point `AGENT_LEASH_PUBLIC_URL` at its domain,
put it behind HTTPS (caddy/nginx), and set the token. The hook on your laptop
then uses `AGENT_LEASH_RELAY_URL=https://your-vps-domain` too.

---

## Notifications
- **ntfy** (default): set `AGENT_LEASH_NTFY_TOPIC` to something unique/unguessable,
  install the ntfy app, subscribe to that topic. For privacy, self-host ntfy and
  set `AGENT_LEASH_NTFY_SERVER`.
- **Telegram**: set `AGENT_LEASH_TELEGRAM_BOT_TOKEN` + `AGENT_LEASH_TELEGRAM_CHAT_ID`.

## Security checklist
- [ ] `AGENT_LEASH_TOKEN` set to a random secret (shared by relay + hook)
- [ ] Unguessable ntfy topic (or self-hosted ntfy)
- [ ] HTTPS for any public exposure (tunnels do this for you)
- [ ] Prefer Tailscale if you don't need public access
- [ ] Keep `AGENT_LEASH_ON_TIMEOUT=deny` (fail safe)
