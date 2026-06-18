"""The agent-leash relay server.

Holds pending approval requests in memory, notifies the phone, serves a mobile
approval page, and hands the decision back to the polling hook.

Endpoints:
  POST /request          (hook)  -> create a request, notify phone, return {id}
  GET  /decision/{id}    (hook)  -> poll current decision
  GET  /r/{id}           (phone) -> mobile approval page
  POST /r/{id}           (phone) -> submit allow/deny [+ reason | edited input]
"""
from __future__ import annotations

import html
import json
import time
import uuid

from fastapi import FastAPI, Form, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

from . import config, notify

app = FastAPI(title="agent-leash relay")

# request_id -> { tool, input, cwd, status, decision, reason, updated_input, ts }
_REQUESTS: dict[str, dict] = {}


def _check_token(provided: str | None) -> None:
    """Enforce the shared secret when one is configured."""
    if config.TOKEN and provided != config.TOKEN:
        raise HTTPException(401, "invalid or missing token")


def _token_qs() -> str:
    return f"?t={config.TOKEN}" if config.TOKEN else ""


@app.post("/request")
async def create_request(
    payload: dict,
    x_agent_leash_token: str | None = Header(default=None),
) -> JSONResponse:
    """Called by the hook. Registers a pending approval and pings the phone."""
    _check_token(x_agent_leash_token)
    rid = uuid.uuid4().hex[:12]
    _REQUESTS[rid] = {
        "tool": payload.get("tool", "?"),
        "input": payload.get("input", {}),
        "cwd": payload.get("cwd", ""),
        "status": "pending",   # pending | decided
        "decision": None,      # allow | deny
        "reason": "",
        "updated_input": None,
        "ts": time.time(),
    }
    approve_url = f"{config.PUBLIC_URL}/r/{rid}{_token_qs()}"
    notify.send(
        title=f"Approve: {_REQUESTS[rid]['tool']}",
        body=_summary(_REQUESTS[rid]),
        approve_url=approve_url,
    )
    return JSONResponse({"id": rid, "approve_url": approve_url})


@app.get("/decision/{rid}")
async def get_decision(
    rid: str,
    x_agent_leash_token: str | None = Header(default=None),
) -> JSONResponse:
    """Called by the hook in a poll loop until status == decided."""
    _check_token(x_agent_leash_token)
    req = _REQUESTS.get(rid)
    if not req:
        raise HTTPException(404, "unknown request")
    return JSONResponse({
        "status": req["status"],
        "decision": req["decision"],
        "reason": req["reason"],
        "updated_input": req["updated_input"],
    })


@app.get("/r/{rid}", response_class=HTMLResponse)
async def approval_page(rid: str, t: str | None = Query(default=None)) -> str:
    _check_token(t)
    req = _REQUESTS.get(rid)
    if not req:
        return "<h2>Request not found or expired.</h2>"
    if req["status"] == "decided":
        return f"<h2>Already decided: {req['decision']}</h2>"
    return _PAGE.format(
        rid=rid,
        token_qs=_token_qs(),
        tool=html.escape(req["tool"]),
        details=html.escape(json.dumps(req["input"], indent=2)),
        cwd=html.escape(req["cwd"]),
    )


@app.post("/r/{rid}", response_class=HTMLResponse)
async def submit_decision(
    rid: str,
    action: str = Form(...),          # "allow" | "deny"
    reason: str = Form(""),            # correction / guidance when denying
    edited_input: str = Form(""),      # optional rewritten tool input (JSON)
    t: str | None = Query(default=None),
) -> str:
    _check_token(t)
    req = _REQUESTS.get(rid)
    if not req:
        return "<h2>Request not found or expired.</h2>"
    req["decision"] = "allow" if action == "allow" else "deny"
    req["reason"] = reason.strip()
    if edited_input.strip():
        try:
            req["updated_input"] = json.loads(edited_input)
        except json.JSONDecodeError:
            req["reason"] = (req["reason"] + " (note: edited input was not valid JSON)").strip()
    req["status"] = "decided"
    return f"<h2>✅ Sent: {req['decision']}</h2><p>You can return to your terminal.</p>"


def _summary(req: dict) -> str:
    inp = json.dumps(req["input"])
    return f"{req['tool']}: {inp[:160]}"


_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>agent-leash</title>
<style>
 body{{font-family:-apple-system,system-ui,sans-serif;margin:0;background:#0d1117;color:#c9d1d9;padding:18px}}
 h1{{font-size:18px}} pre{{background:#161b22;padding:12px;border-radius:8px;overflow:auto;font-size:13px}}
 textarea{{width:100%;box-sizing:border-box;background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:8px;padding:10px;font-size:15px}}
 button{{font-size:17px;padding:14px;border:0;border-radius:10px;color:#fff;width:100%;margin-top:10px}}
 .allow{{background:#238636}} .deny{{background:#da3633}} label{{font-size:13px;color:#8b949e}}
 .muted{{color:#8b949e;font-size:13px}}
</style></head><body>
 <h1>🐕 agent-leash — approve tool</h1>
 <p class="muted">cwd: {cwd}</p>
 <h2 style="font-size:16px">{tool}</h2>
 <pre>{details}</pre>
 <form method="post" action="/r/{rid}{token_qs}">
   <label>Correction / instruction (sent to Claude on reject)</label>
   <textarea name="reason" rows="3" placeholder="e.g. don't delete that — update it instead"></textarea>
   <label>Edited tool input (optional JSON — runs this instead)</label>
   <textarea name="edited_input" rows="3" placeholder='{{"command": "ls -la"}}'></textarea>
   <button class="allow" name="action" value="allow" type="submit">✅ Approve</button>
   <button class="deny"  name="action" value="deny"  type="submit">❌ Reject / Correct</button>
 </form>
</body></html>"""


def main() -> None:
    import uvicorn
    if not config.TOKEN:
        print(
            "[agent-leash] ⚠️  AGENT_LEASH_TOKEN is not set — relay is OPEN. "
            "Fine for localhost, but set a token before exposing it via a tunnel/VPS.",
            flush=True,
        )
    host = config.RELAY_URL.split("//")[-1].split(":")[0] or "127.0.0.1"
    port = int(config.RELAY_URL.rsplit(":", 1)[-1]) if ":" in config.RELAY_URL.split("//")[-1] else 8787
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
