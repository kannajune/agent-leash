# Making the relay reachable from your phone

The hook talks to the relay over `STEERD_RELAY_URL` (usually
`http://127.0.0.1:8787` on the same machine). But the **push notification link**
your phone opens uses `STEERD_PUBLIC_URL` — and that must be reachable from
your phone. Pick one option below.

> 🔐 **Always set `STEERD_TOKEN` to a strong secret before exposing the relay.**
> Without it the relay is open to anyone who can reach the URL.

The relay always listens locally; only the *public URL* differs. Common setup:

```bash
export STEERD_TOKEN="$(openssl rand -hex 24)"   # share this with the hook too
export STEERD_NTFY_TOPIC="your-unique-topic"
# STEERD_RELAY_URL stays http://127.0.0.1:8787 (hook -> relay, local)
# STEERD_PUBLIC_URL = the reachable URL below (phone -> relay)
steerd-relay
```

Set the **same** `STEERD_TOKEN` (and `STEERD_PUBLIC_URL` if needed) in
the environment Claude Code runs the hook from.

---

## Option A — Tailscale (most secure, recommended)
Put your laptop and phone on the same [Tailscale](https://tailscale.com) tailnet;
no public exposure at all.

```bash
export STEERD_PUBLIC_URL="http://<your-laptop-tailscale-ip>:8787"
steerd-relay
```
Your phone opens the link over the private tailnet. Still set a token.

## Option B — Cloudflare Tunnel (quick public HTTPS, no account)
```bash
# terminal 1
steerd-relay
# terminal 2 — prints a https://<random>.trycloudflare.com URL
cloudflared tunnel --url http://localhost:8787
```
```bash
export STEERD_PUBLIC_URL="https://<random>.trycloudflare.com"
```
Restart the relay so new requests build links with the public URL. **Token is mandatory here** — this URL is on the public internet.

## Option C — ngrok
```bash
ngrok http 8787          # prints https://<id>.ngrok-free.app
export STEERD_PUBLIC_URL="https://<id>.ngrok-free.app"
```

## Option D — small VPS
Run `steerd-relay` on a VPS, point `STEERD_PUBLIC_URL` at its domain,
put it behind HTTPS (caddy/nginx), and set the token. The hook on your laptop
then uses `STEERD_RELAY_URL=https://your-vps-domain` too.

---

## Notifications
- **ntfy** (default): set `STEERD_NTFY_TOPIC` to something unique/unguessable,
  install the ntfy app, subscribe to that topic. For privacy, self-host ntfy and
  set `STEERD_NTFY_SERVER`.
- **Telegram**: set `STEERD_TELEGRAM_BOT_TOKEN` + `STEERD_TELEGRAM_CHAT_ID`.

## Security checklist
- [ ] `STEERD_TOKEN` set to a random secret (shared by relay + hook)
- [ ] Unguessable ntfy topic (or self-hosted ntfy)
- [ ] HTTPS for any public exposure (tunnels do this for you)
- [ ] Prefer Tailscale if you don't need public access
- [ ] Keep `STEERD_ON_TIMEOUT=deny` (fail safe)
