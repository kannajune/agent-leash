"""Relay request -> decide -> poll cycle (FastAPI TestClient, no network)."""
from fastapi.testclient import TestClient

from steerd.relay import app

client = TestClient(app)


def _make_request():
    r = client.post("/request", json={
        "tool": "Bash", "input": {"command": "rm -rf build"}, "cwd": "/tmp",
    })
    assert r.status_code == 200
    return r.json()["id"]


def test_request_starts_pending():
    rid = _make_request()
    d = client.get(f"/decision/{rid}").json()
    assert d["status"] == "pending"
    assert d["decision"] is None


def test_allow_flow():
    rid = _make_request()
    r = client.post(f"/r/{rid}", data={"action": "allow"})
    assert r.status_code == 200
    d = client.get(f"/decision/{rid}").json()
    assert d["status"] == "decided" and d["decision"] == "allow"


def test_deny_with_correction_flow():
    rid = _make_request()
    client.post(f"/r/{rid}", data={"action": "deny", "reason": "use a scoped path"})
    d = client.get(f"/decision/{rid}").json()
    assert d["decision"] == "deny"
    assert d["reason"] == "use a scoped path"


def test_edited_input_is_parsed():
    rid = _make_request()
    client.post(f"/r/{rid}", data={
        "action": "allow", "edited_input": '{"command": "ls -la"}',
    })
    d = client.get(f"/decision/{rid}").json()
    assert d["updated_input"] == {"command": "ls -la"}


def test_invalid_edited_input_is_noted_not_fatal():
    rid = _make_request()
    r = client.post(f"/r/{rid}", data={"action": "allow", "edited_input": "{not json"})
    assert r.status_code == 200
    d = client.get(f"/decision/{rid}").json()
    assert d["decision"] == "allow"          # still works
    assert d["updated_input"] is None        # bad JSON ignored
    assert "not valid JSON" in d["reason"]


def test_unknown_request_404():
    assert client.get("/decision/nope").status_code == 404


def test_approval_page_renders():
    rid = _make_request()
    html = client.get(f"/r/{rid}").text
    assert "Approve" in html and "Reject" in html
