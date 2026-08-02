import importlib.util
import json
import socket
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "experiments/runners/run_offline.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("offline_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_runner_generates_three_reproducible_formats(tmp_path):
    runner = load_runner()
    output = tmp_path / "results"
    first = runner.run(output=output)
    snapshots = {path.name: path.read_bytes() for path in output.iterdir()}
    second = runner.run(output=output)

    assert first == second
    assert snapshots == {path.name: path.read_bytes() for path in output.iterdir()}
    assert set(snapshots) == {"latest.json", "latest.csv", "latest.md"}
    assert len(first["cases"]) >= 20


def test_output_contract_and_metrics(tmp_path):
    runner = load_runner()
    report = runner.run(output=tmp_path)
    schema = json.loads((ROOT / "experiments/schemas/result.schema.json").read_text())

    assert set(schema["required"]) <= report.keys()
    assert schema["properties"]["online_experiments"]["const"] == report["online_experiments"]
    assert report["configuration"]["online_experiments"] is False
    assert report["metrics"] == runner._metrics(report["cases"])
    assert report["metrics"]["errors_by_scenario"] == {name: 0 for name in sorted({c["scenario"] for c in report["cases"]})}
    assert 0 <= report["metrics"]["valid_response_rate"] <= 1


def test_runner_never_accesses_network(monkeypatch, tmp_path):
    runner = load_runner()

    def forbidden(*_args, **_kwargs):
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    report = runner.run(output=tmp_path)
    assert len(report["cases"]) == 20


def test_invalid_fixture_is_rejected(tmp_path):
    runner = load_runner()
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"cases": [{"id": "broken"}]}', encoding="utf-8")
    with pytest.raises(runner.FixtureError, match="at least 20 cases"):
        runner.run(fixture=invalid, output=tmp_path / "output")


def test_online_mode_is_refused(monkeypatch):
    runner = load_runner()
    monkeypatch.setenv("RUN_ONLINE_LLM_EXPERIMENTS", "true")
    with pytest.raises(RuntimeError, match="intentionally disabled"):
        runner.build_report()
