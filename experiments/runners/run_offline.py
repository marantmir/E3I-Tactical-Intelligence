#!/usr/bin/env python3
"""Deterministic, standard-library-only offline evaluation runner."""

from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "experiments/fixtures/offline_cases.json"
DEFAULT_OUTPUT = ROOT / "experiments/results"
REQUIRED_FLAGS = {
    "valid", "schema", "grounded", "tool_correct", "fallback", "complete",
    "conflict_signaled",
}


class FixtureError(ValueError):
    """Raised when an offline fixture violates the stable contract."""


def _validate_fixture(data: Any) -> None:
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise FixtureError("fixture must be an object containing a cases array")
    if len(data["cases"]) < 20:
        raise FixtureError("fixture must contain at least 20 cases")
    ids = set()
    for case in data["cases"]:
        if not isinstance(case, dict) or not {"id", "scenario", "variant", "expected", "obtained"} <= case.keys():
            raise FixtureError("every case must contain stable identity and outcomes")
        if case["id"] in ids:
            raise FixtureError(f"duplicate case id: {case['id']}")
        ids.add(case["id"])
        for outcome in (case["expected"], case["obtained"]):
            if not REQUIRED_FLAGS <= outcome.keys() or not isinstance(outcome.get("iterations"), int):
                raise FixtureError(f"invalid outcome contract: {case['id']}")


def _rate(cases: list[dict[str, Any]], key: str) -> float:
    return round(sum(bool(case["obtained"][key]) for case in cases) / len(cases), 4)


def _metrics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    conflicts = [case for case in cases if case["expected"]["conflict_signaled"]]
    return {
        "valid_response_rate": _rate(cases, "valid"),
        "schema_adherence_rate": _rate(cases, "schema"),
        "grounding_rate": _rate(cases, "grounded"),
        "correct_tool_usage_rate": _rate(cases, "tool_correct"),
        "fallback_rate": _rate(cases, "fallback"),
        "average_iterations": round(sum(c["obtained"]["iterations"] for c in cases) / len(cases), 4),
        "offline_latency_ms": 0,
        "errors_by_scenario": {
            scenario: sum(c["obtained"] != c["expected"] for c in cases if c["scenario"] == scenario)
            for scenario in sorted({c["scenario"] for c in cases})
        },
        "completion_rate": _rate(cases, "complete"),
        "correct_conflict_signaling_rate": round(
            sum(c["obtained"]["conflict_signaled"] for c in conflicts) / len(conflicts), 4
        ) if conflicts else 1.0,
    }


def _branch() -> str:
    env_branch = os.getenv("EXPERIMENT_BRANCH")
    if env_branch:
        return env_branch
    try:
        return subprocess.run(
            ["git", "branch", "--show-current"], cwd=ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip() or "detached"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def build_report(fixture: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    try:
        data = json.loads(fixture.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureError(f"cannot load fixture: {exc}") from exc
    _validate_fixture(data)
    if os.getenv("RUN_ONLINE_LLM_EXPERIMENTS", "false").lower() != "false":
        raise RuntimeError("online experiments are intentionally disabled")
    cases = data["cases"]
    return {
        "generated_at": data["generated_at"],
        "branch": _branch(),
        "commit_base": data["commit_base"],
        "configuration": data["configuration"],
        "online_experiments": "Experimentos online: não executados.",
        "cases": cases,
        "metrics": _metrics(cases),
        "duration_ms": 0,
        "limitations": [
            "Resultados medem um modelo determinístico e regras locais, não a qualidade de provedores reais.",
            "Latência é duração lógica offline normalizada; não representa latência de rede.",
        ],
    }


def _write_csv(report: dict[str, Any], path: Path) -> None:
    fields = ["id", "scenario", "variant", "expected", "obtained", "matched"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case in report["cases"]:
            writer.writerow({
                "id": case["id"], "scenario": case["scenario"], "variant": case["variant"],
                "expected": json.dumps(case["expected"], ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                "obtained": json.dumps(case["obtained"], ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                "matched": case["expected"] == case["obtained"],
            })


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Resultado mais recente dos experimentos offline", "",
        f"- Data: `{report['generated_at']}`", f"- Branch: `{report['branch']}`",
        f"- Commit base: `{report['commit_base']}`", f"- Duração: `{report['duration_ms']} ms`",
        f"- {report['online_experiments']}", "", "## Configuração", "",
        "```json", json.dumps(report["configuration"], ensure_ascii=False, sort_keys=True, indent=2), "```", "",
        "## Casos", "", "| ID | Cenário | Variante | Esperado = obtido |", "|---|---|---|---|",
    ]
    lines.extend(
        f"| `{c['id']}` | {c['scenario']} | {c['variant']} | {'sim' if c['expected'] == c['obtained'] else 'não'} |"
        for c in report["cases"]
    )
    lines += ["", "## Métricas", "", "```json", json.dumps(report["metrics"], ensure_ascii=False, sort_keys=True, indent=2), "```", "", "## Limitações", ""]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(fixture: Path = DEFAULT_FIXTURE, output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    report = build_report(fixture)
    output.mkdir(parents=True, exist_ok=True)
    (output / "latest.json").write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    _write_csv(report, output / "latest.csv")
    _write_markdown(report, output / "latest.md")
    return report


if __name__ == "__main__":
    result = run()
    print(f"{len(result['cases'])} casos offline concluídos; {result['online_experiments']}")
