"""Send the approval notification to the user's phone.

Pluggable backends; ntfy (push app with no account) and Telegram are supported.
Both just deliver a message + a link to the relay's approval page — the actual
Approve/Reject/Correct happens on that mobile web page, so we don't depend on a
specific app's button capabilities.
"""
from __future__ import annotations

import json
import urllib.request

from . import config


def _post(url: str, data: bytes, headers: dict[str, str]) -> None:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as exc:  # noqa: BLE001 - notification failure must not crash the hook
        print(f"[steerd] notification failed: {exc}", flush=True)


def send(title: str, body: str, approve_url: str) -> None:
    """Deliver a notification with a link to the approval page."""
    if config.NTFY_TOPIC:
        _post(
            f"{config.NTFY_SERVER}/{config.NTFY_TOPIC}",
            body.encode("utf-8"),
            {
                "Title": title,
                "Priority": "high",
                "Tags": "robot",
                "Click": approve_url,
                "Actions": f"view, Review & decide, {approve_url}",
            },
        )
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
        _post(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
            json.dumps({
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": f"*{title}*\n{body}\n\n👉 {approve_url}",
                "parse_mode": "Markdown",
            }).encode("utf-8"),
            {"Content-Type": "application/json"},
        )
    if not config.NTFY_TOPIC and not config.TELEGRAM_BOT_TOKEN:
        # No backend configured — at least print the link so the loop still works.
        print(f"[steerd] approve at: {approve_url}", flush=True)
