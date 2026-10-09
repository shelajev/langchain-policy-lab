from pathlib import Path
import socket

import pytest

from langchain_enterprise.chain import PolicyAssistant


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Behavioral tests must not access the network")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)


@pytest.fixture
def policies():
    return Path(__file__).resolve().parents[1] / "data" / "policies"


@pytest.fixture
def assistant(policies):
    return PolicyAssistant(policies)
