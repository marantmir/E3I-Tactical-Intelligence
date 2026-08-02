"""Dependency-free repository checks for local links, secrets, and sensitive files."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = (
    re.compile(r"(?i)(?:api[_-]?key|secret|token|password)\s*[=:]\s*['\"](?!example|changeme)[A-Za-z0-9_./+=-]{16,}['\"]"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:sk|xox[baprs])-[A-Za-z0-9_-]{16,}\b"),
)
SENSITIVE_NAMES = re.compile(r"(^|/)(?:\.env(?:\..+)?|.*credentials.*\.json|.*secrets.*\.json|.*\.(?:pem|p12|pfx|sqlite3?|db|token|log|mp4|mov|avi|mkv|webm))$", re.I)
LINK = re.compile(r"\[[^]]*]\(([^)]+)\)")


def tracked() -> list[str]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
    )
    return [item.decode() for item in output.split(b"\0") if item]


def secrets() -> list[str]:
    findings = []
    for name in tracked():
        path = ROOT / name
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for number, line in enumerate(text.splitlines(), 1):
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                findings.append(f"{name}:{number}: possible secret")
    return findings


def sensitive() -> list[str]:
    return [name for name in tracked() if name != ".env.example" and SENSITIVE_NAMES.search(name)]


def links() -> list[str]:
    findings = []
    for name in tracked():
        if not name.endswith(".md"):
            continue
        for target in LINK.findall((ROOT / name).read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith(("mailto:", "#")):
                continue
            if not ((ROOT / name).parent / target).resolve().exists():
                findings.append(f"{name}: missing local link {target}")
    return findings


CHECKS = {"secrets": secrets, "sensitive": sensitive, "links": links}
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("check", choices=CHECKS)
    args = parser.parse_args()
    problems = CHECKS[args.check]()
    print("\n".join(problems) if problems else f"{args.check}: ok")
    sys.exit(bool(problems))
