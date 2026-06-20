@echo off
REM ── steerd relay launcher for Windows ───────────────────────────────
REM Edit the values below, then run this directly OR register it as an
REM always-on task/service (see deploy/README.md → Windows).
REM
REM Find this PC's Tailscale IP first:  tailscale ip -4
REM ────────────────────────────────────────────────────────────────────

set STEERD_TOKEN=CHANGE_ME_random_secret
set STEERD_HOST=0.0.0.0
set STEERD_NTFY_TOPIC=CHANGE_ME_unique_topic
REM the address your PHONE uses — this PC's Tailscale IP:
set STEERD_PUBLIC_URL=http://YOUR_TAILSCALE_IP:8787

steerd-relay
