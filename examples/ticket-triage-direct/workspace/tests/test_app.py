import json
import socket
from pathlib import Path

import httpx
import pytest

from ticket_triage.app import main
from ticket_triage.chain import classify
from ticket_triage.sources import fetch_status


TICKET = Path(__file__).parents[1] / "data/tickets/t-101.json"


def test_shape_and_citation():
    result = classify(json.loads(TICKET.read_text()), fake_model=True)
    assert result.ticket_id == "T-101"
    assert result.category == "technical"
    assert result.summary


def test_status_transport():
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text="operational"))
    assert fetch_status("https://status.example.invalid", transport) == "operational"


def test_fake_cli_has_no_network_or_webhook(monkeypatch, capsys):
    def denied(*args, **kwargs):
        raise AssertionError("unexpected network")
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr("ticket_triage.app.post_summary", denied)
    main(["--ticket", str(TICKET), "--fake-model"])
    assert json.loads(capsys.readouterr().out)["ticket_id"] == "T-101"


def test_network_failure_is_clean(monkeypatch, capsys):
    monkeypatch.setenv("TRIAGE_STATUS_URL", "https://status.example.invalid")
    def denied(url):
        raise httpx.ConnectError("private detail")
    monkeypatch.setattr("ticket_triage.app.fetch_status", denied)
    with pytest.raises(SystemExit) as failure:
        main(["--ticket", str(TICKET), "--fake-model", "--status"])
    assert failure.value.code == 2
    assert "private detail" not in capsys.readouterr().err
