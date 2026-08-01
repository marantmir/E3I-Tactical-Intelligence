"""Dependency-free baseline lint checks for repository Python and text files."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOTS = (ROOT / "backend" / "app", ROOT / "backend" / "tests")
TEXT_ROOTS = (*PYTHON_ROOTS, ROOT / "scripts", ROOT / ".github")
TEXT_PATTERNS = ("*.py", "*.yml", "*.yaml")


def main() -> int:
    errors: list[str] = []
    python_files = [path for root in PYTHON_ROOTS for path in root.rglob("*.py")]
    for path in python_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(str(exc))

    checked: set[Path] = set()
    for text_root in TEXT_ROOTS:
        for pattern in TEXT_PATTERNS:
            for path in text_root.rglob(pattern):
                if path in checked:
                    continue
                checked.add(path)
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if line.rstrip() != line:
                        errors.append(f"{path.relative_to(ROOT)}:{number}: trailing whitespace")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"lint: {len(python_files)} Python files parsed; {len(checked)} text files checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
