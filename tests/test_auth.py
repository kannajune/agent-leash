"""Relay auth-token enforcement."""
from fastapi.testclient import TestClient

from agent_leash import config, relay

client = TestClient(relay.app)
_REQ = {"tool": "Bash", "input": {"command": "ls"}, "cwd": "/tmp"}


def test_open_when_no_token(monkeypatch):
    monkeypatch.setattr(config, "TOKEN", "")
    assert client.post("/request", json=_REQ).status_code == 200


def test_request_requires_correct_token(monkeypatch):
    monkeypatch.setattr(config, "TOKEN", "s3cret")
    assert client.post("/request", json=_REQ).status_code == 401            # missing
    assert client.post("/request", json=_REQ,
                       headers={"X-Agent-Leash-Token": "nope"}).status_code == 401  # wrong
    ok = client.post("/request", json=_REQ, headers={"X-Agent-Leash-Token": "s3cret"})
    assert ok.status_code == 200


def test_all_endpoints_protected(monkeypatch):
    monkeypatch.setattr(config, "TOKEN", "s3cret")
    h = {"X-Agent-Leash-Token": "s3cret"}
    rid = client.post("/request", json=_REQ, headers=h).json()["id"]

    assert client.get(f"/decision/{rid}").status_code == 401
    assert client.get(f"/decision/{rid}", headers=h).status_code == 200

    assert client.get(f"/r/{rid}").status_code == 401
    assert client.get(f"/r/{rid}?t=s3cret").status_code == 200

    assert client.post(f"/r/{rid}", data={"action": "allow"}).status_code == 401
    assert client.post(f"/r/{rid}?t=s3cret", data={"action": "allow"}).status_code == 200
