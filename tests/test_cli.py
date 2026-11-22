import json

import pytest

from gemini_tool import cli, client, official


def test_missing_credentials_exit_code(monkeypatch, capsys):
    monkeypatch.delenv(client.ENV_PSID, raising=False)
    monkeypatch.delenv(official.ENV_API_KEY, raising=False)
    assert cli.main(["hello"]) == cli.EXIT_NO_CREDS
    assert client.ENV_PSID in capsys.readouterr().err


def test_load_credentials(monkeypatch):
    monkeypatch.setenv(client.ENV_PSID, "abc")
    monkeypatch.delenv(client.ENV_PSIDTS, raising=False)
    assert client.load_credentials() == ("abc", None)


def test_json_output(monkeypatch, capsys):
    async def fake_ask(prompt, files=None, model=None, temporary=True):
        return f"echo:{prompt}"

    monkeypatch.setattr(client, "ask", fake_ask)
    monkeypatch.delenv(official.ENV_API_KEY, raising=False)
    assert cli.main(["hi", "--json"]) == cli.EXIT_OK
    assert json.loads(capsys.readouterr().out) == {"text": "echo:hi"}


def test_api_error_exit_code(monkeypatch, capsys):
    async def boom(*a, **k):
        raise ConnectionError("blocked")

    monkeypatch.setattr(client, "ask", boom)
    monkeypatch.delenv(official.ENV_API_KEY, raising=False)
    assert cli.main(["hi"]) == cli.EXIT_API_ERROR
    assert "ConnectionError" in capsys.readouterr().err


def test_auto_prefers_official_when_key_set(monkeypatch, capsys):
    async def fake_official(prompt, files=None, model=None):
        return "official:" + prompt

    monkeypatch.setenv(official.ENV_API_KEY, "k")
    monkeypatch.setattr(official, "ask", fake_official)
    assert cli.main(["yo"]) == cli.EXIT_OK
    assert capsys.readouterr().out.strip() == "official:yo"


def test_forced_official_without_key(monkeypatch, capsys):
    monkeypatch.delenv(official.ENV_API_KEY, raising=False)
    assert cli.main(["x", "--backend", "official"]) == cli.EXIT_NO_CREDS
    assert official.ENV_API_KEY in capsys.readouterr().err
