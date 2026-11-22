import asyncio

import pytest

from gemini_tool import official


class FakeError(Exception):
    def __init__(self, code):
        self.code = code


class FakeModels:
    def __init__(self, outcomes):
        self.outcomes = outcomes
        self.calls = []

    async def generate_content(self, model, contents):
        self.calls.append(model)
        outcome = self.outcomes.get(model)
        if isinstance(outcome, Exception):
            raise outcome
        return type("R", (), {"text": outcome})()


def _install(monkeypatch, outcomes):
    models = FakeModels(outcomes)
    fake = type("C", (), {"aio": type("A", (), {"models": models})()})()
    monkeypatch.setattr(official, "_client", lambda: fake)
    monkeypatch.setattr(official, "BACKOFF_BASE_SEC", 0)
    monkeypatch.delenv(official.ENV_MODEL, raising=False)
    monkeypatch.delenv(official.ENV_FALLBACKS, raising=False)
    return models


def test_falls_back_on_503(monkeypatch):
    models = _install(monkeypatch, {"gemini-3.8-flash": FakeError(503), "gemini-3.5-flash": "OK"})
    assert asyncio.run(official.ask("hi")) == "OK"
    assert models.calls == ["gemini-3.8-flash"] * (official.RETRIES_PER_MODEL + 1) + ["gemini-3.5-flash"]


def test_non_retryable_raises_immediately(monkeypatch):
    models = _install(monkeypatch, {"gemini-3.8-flash": FakeError(400)})
    with pytest.raises(FakeError):
        asyncio.run(official.ask("hi"))
    assert models.calls == ["gemini-3.8-flash"]


def test_explicit_model_has_no_fallback(monkeypatch):
    _install(monkeypatch, {})
    assert official.candidate_models("x") == ["x"]
    assert official.candidate_models(None)[0] == official.DEFAULT_MODEL
