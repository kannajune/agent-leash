# Always-on steerd relay + Tailscale (approve from anywhere)

Run the relay as a **persistent service** on a machine that's always on, join
everything to a **Tailscale** tailnet, and you can approve your agent's actions
from your phone **on any network** — home WiFi, cellular, traveling.

## The setup (3 devices, 1 tailnet)

```
┌─ Relay PC (always-on) ──────────┐      ┌─ Work PC (runs Claude Code) ─┐
│  steerd-relay as a service      │◀────▶│  steerd-hook                  │
│  Tailscale IP: 100.x.x.x:8787   │ tnet │  STEERD_RELAY_URL = relay's   │
└─────────────────────────────────┘      │  Tailscale IP:8787            │
              ▲ tailnet                   └──────────────────────────────┘
              │
        ┌─ Your phone ─┐  (Tailscale app + ntfy app)
        │ approve/reject│  opens http://100.x.x.x:8787/r/{id}
        └───────────────┘
```

> The relay and the work PC can even be the **same** machine — then
> `STEERD_RELAY_URL` is just `http://127.0.0.1:8787` and only the phone uses the
> Tailscale IP. The multi-machine layout above is for a *dedicated* always-on relay.

## Steps

### 1. Tailscale on all three
Install [Tailscale](https://tailscale.com/download) on the **relay PC**, the
**work PC**, and your **phone**; log all into the same account. Get the relay
PC's tailnet IP: `tailscale ip -4` (e.g. `100.101.102.103`).

### 2. Install + run the relay as a service (relay PC)
```bash
pipx install steerd
```
- **macOS:** edit `deploy/com.steerd.relay.plist` (token, ntfy topic,
  `STEERD_PUBLIC_URL=http://100.101.102.103:8787`, and the `which steerd-relay`
  path), then:
  ```bash
  cp deploy/com.steerd.relay.plist ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.steerd.relay.plist
  ```
- **Linux:** edit `deploy/steerd-relay.service` the same way, then:
  ```bash
  cp deploy/steerd-relay.service ~/.config/systemd/user/
  systemctl --user daemon-reload && systemctl --user enable --now steerd-relay
  ```
It now restarts on reboot and keeps running.

### 3. Point the hook at the relay (work PC)
Install steerd, then in your `settings.json` hook command set:
```
STEERD_TOKEN=<same secret>  STEERD_RELAY_URL=http://100.101.102.103:8787  /abs/path/to/steerd-hook
```
(Use the **same `STEERD_TOKEN`** everywhere. The work PC reaches the relay over Tailscale.)

### 4. Phone
Install **Tailscale** (so it can reach `100.x.x.x`) and **ntfy** (subscribed to
your `STEERD_NTFY_TOPIC`). Done — run your modules/tests via Claude; each shell
command pings your phone, and you approve from anywhere.

## Security checklist
- [ ] Same strong `STEERD_TOKEN` on relay + hook
- [ ] Prefer Tailscale (private) over a public tunnel — no internet exposure
- [ ] Unguessable ntfy topic (or self-host ntfy via `STEERD_NTFY_SERVER`)
- [ ] Keep `STEERD_ON_TIMEOUT=deny` (fail safe if you don't answer in time)
