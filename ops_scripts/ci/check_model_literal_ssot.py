#!/usr/bin/env python3
"""Guard provider model literals against drifting outside SSOT files."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

APPROVED_MODEL_SSOT_PATHS = {
    Path("config/model_catalog.json"),
    Path("apps_rg/config/provider_profiles.yaml"),
}

SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".playwright-mcp",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "artifacts",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
}

PRODUCTION_PREFIXES = (
    Path("agentic_core"),
    Path("apps_rg"),
    Path("apps_qna"),
    Path("tools"),
)

PRODUCTION_SUFFIXES = {".py", ".yaml", ".yml", ".json", ".toml"}
STALE_OPENAI_RE = re.compile(r"\bgpt[-_ ]?5[.]4(?:-mini)?\b", re.IGNORECASE)


def _rel(path: Path) -> Path:
    return path.relative_to(REPO_ROOT)


def _skip(path: Path) -> bool:
    rel = _rel(path)
    return any(part in SKIP_PARTS for part in rel.parts)


def _text_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=True,
        )
        return [
            REPO_ROOT / line
            for line in result.stdout.splitlines()
            if line and (REPO_ROOT / line).is_file() and not _skip(REPO_ROOT / line)
        ]
    except (subprocess.SubprocessError, OSError):
        pass

    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or _skip(path):
            continue
        if path.stat().st_size > 5_000_000:
            continue
        files.append(path)
    return files


def _is_production_path(path: Path) -> bool:
    rel = _rel(path)
    return path.suffix.lower() in PRODUCTION_SUFFIXES and any(
        rel == prefix or rel.is_relative_to(prefix) for prefix in PRODUCTION_PREFIXES
    )


def _catalog_openai_models() -> tuple[str, ...]:
    catalog = json.loads((REPO_ROOT / "config" / "model_catalog.json").read_text(encoding="utf-8"))
    openai = catalog.get("openai") or {}
    models: list[str] = []
    for value in openai.values():
        if isinstance(value, str):
            models.append(value)
        elif isinstance(value, list):
            models.extend(item for item in value if isinstance(item, str))
    return tuple(sorted(set(models)))


def _line_violations(path: Path, pattern: re.Pattern[str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    hits: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            hits.append(f"{_rel(path).as_posix()}:{lineno}: {line.strip()}")
    return hits


def main() -> int:
    violations: list[str] = []
    files = _text_files()

    for path in files:
        violations.extend(_line_violations(path, STALE_OPENAI_RE))

    current_models = _catalog_openai_models()
    if current_models:
        current_literal_re = re.compile(
            "|".join(rf"['\"]{re.escape(model)}['\"]" for model in current_models)
        )
        for path in files:
            rel = _rel(path)
            if rel in APPROVED_MODEL_SSOT_PATHS or not _is_production_path(path):
                continue
            violations.extend(_line_violations(path, current_literal_re))

    if violations:
        print("[MODEL-LITERAL-SSOT] FAIL - provider model literals outside SSOT")
        for item in violations:
            print(f"  {item}")
        return 1

    print("[MODEL-LITERAL-SSOT] PASS - provider model literals are SSOT-contained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
