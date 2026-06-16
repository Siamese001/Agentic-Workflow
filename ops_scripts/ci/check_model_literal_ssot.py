#!/usr/bin/env python3
"""Guard provider model literals against drifting outside SSOT files."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

APPROVED_MODEL_SSOT_PATHS = {
    Path("config/model_catalog.json"),
    Path("agentic_core/config/model_catalog.py"),
    Path("agentic_core/L0_routing/config/model_catalog.py"),
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
    Path("apps_lic"),
    Path("apps_qna"),
    Path("apps_rg"),
    Path("apps_research"),
    Path("apps_shared"),
    Path("apps_underwriting_ai"),
    Path("ops_scripts"),
    Path("tools"),
)

PRODUCTION_SUFFIXES = {".py"}
STALE_OPENAI_RE = re.compile(r"\bgpt[-_ ]?5[.]4(?:-mini)?\b", re.IGNORECASE)
MODEL_LITERAL_RE = re.compile(
    r"\b(?:gpt-(?:\d|5-mini|5[.]\d)[A-Za-z0-9_.-]*|"
    r"claude-(?:\d|sonnet|haiku|opus|instant|fable)[A-Za-z0-9_.-]*|"
    r"gemini-(?:\d|pro)[A-Za-z0-9_.-]*|"
    r"Qwen/[A-Za-z0-9_.-]+|BAAI/[A-Za-z0-9_.-]+)\b"
)
ENV_MODEL_LITERAL_RE = re.compile(
    r"(?i)(?:"
    r"gpt[-_ ]?5|gpt-|claude-|claude\s+(?:sonnet|haiku|opus)|"
    r"gemini-|qwen|bge-m3|models--BAAI--bge|BAAI[/\\-]bge"
    r")"
)
ENV_ASSIGNMENT_RE = re.compile(r"^\s*#?\s*([A-Z][A-Z0-9_]*)\s*=")
ENV_LLM_CONFIG_KEY_PARTS = (
    "MODEL",
    "MAX_OUTPUT_TOKENS",
    "MAX_TOKENS",
    "MAX_MODEL_LEN",
    "TEMPERATURE",
    "REASONING_EFFORT",
    "PROVIDER_PROFILE",
    "TARGET_PROVIDER",
    "MODULAR_LANE_PROVIDER",
    "L2_PROVIDER_MODE",
)
ENV_SECRET_KEY_SUFFIXES = (
    "_API_KEY",
    "_ACCESS_TOKEN",
    "_REFRESH_TOKEN",
    "_AUTH_TOKEN",
    "_PAT",
    "_SECRET",
    "_PASSWORD",
)


def _rel(path: Path) -> Path:
    return path.relative_to(REPO_ROOT)


def _display_path(path: Path) -> str:
    try:
        return _rel(path).as_posix()
    except ValueError:
        return str(path)


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


def _env_files() -> list[Path]:
    candidates: list[Path] = [REPO_ROOT / ".env", REPO_ROOT / ".env.example"]
    seen: set[Path] = set()
    files: list[Path] = []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen or not path.is_file():
            continue
        seen.add(resolved)
        files.append(path)
    return files


def _is_production_path(path: Path) -> bool:
    rel = _rel(path)
    return path.suffix.lower() in PRODUCTION_SUFFIXES and any(
        rel == prefix or rel.is_relative_to(prefix) for prefix in PRODUCTION_PREFIXES
    )


def _catalog_models() -> tuple[str, ...]:
    catalog = json.loads((REPO_ROOT / "config" / "model_catalog.json").read_text(encoding="utf-8"))
    models: list[str] = []
    def visit(value: object) -> None:
        if isinstance(value, str):
            models.append(value)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)
    visit(catalog)
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


def _is_secret_env_key(key: str) -> bool:
    return key == "API_KEY" or key.endswith(ENV_SECRET_KEY_SUFFIXES)


def _is_llm_env_config_key(key: str) -> bool:
    if not key or _is_secret_env_key(key):
        return False
    return any(part in key for part in ENV_LLM_CONFIG_KEY_PARTS)


def _env_llm_config_violations(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    hits: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = ENV_ASSIGNMENT_RE.match(line)
        key = match.group(1) if match else ""
        if _is_llm_env_config_key(key):
            hits.append(f"{_display_path(path)}:{lineno}: env LLM config key {key}=<redacted>")
            continue
        if ENV_MODEL_LITERAL_RE.search(line) and not _is_secret_env_key(key):
            hits.append(f"{_display_path(path)}:{lineno}: env model/provider literal <redacted>")
    return hits


def _docstring_locations(tree: ast.AST) -> set[tuple[int, int]]:
    locations: set[tuple[int, int]] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                value = body[0].value
                if isinstance(value.value, str):
                    locations.add((value.lineno, value.col_offset))
    return locations


def _attribute_docstring_locations(tree: ast.AST) -> set[tuple[int, int]]:
    """Return locations for PEP-257 attribute docstrings after assignments."""

    locations: set[tuple[int, int]] = set()

    def scan_body(body: list[ast.stmt]) -> None:
        for previous, current in zip(body, body[1:]):
            if not isinstance(previous, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                continue
            if not isinstance(current, ast.Expr) or not isinstance(current.value, ast.Constant):
                continue
            if isinstance(current.value.value, str):
                locations.add((current.value.lineno, current.value.col_offset))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            scan_body(getattr(node, "body", []))
    return locations


def _python_model_literal_violations(path: Path, catalog_models: set[str]) -> list[str]:
    rel = _rel(path)
    if rel in APPROVED_MODEL_SSOT_PATHS:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return _line_violations(path, MODEL_LITERAL_RE)
    docstrings = _docstring_locations(tree) | _attribute_docstring_locations(tree)
    lines = text.splitlines()
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if (node.lineno, node.col_offset) in docstrings:
            continue
        if MODEL_LITERAL_RE.search(node.value):
            preview = lines[node.lineno - 1].strip() if 0 < node.lineno <= len(lines) else node.value
            catalog_note = "" if node.value in catalog_models else " [not in catalog]"
            hits.append(f"{rel.as_posix()}:{node.lineno}: {preview}{catalog_note}")
    return hits


def main() -> int:
    violations: list[str] = []
    files = _text_files()

    for path in files:
        violations.extend(_line_violations(path, STALE_OPENAI_RE))

    catalog_models = set(_catalog_models())
    for path in files:
        if not _is_production_path(path):
            continue
        violations.extend(_python_model_literal_violations(path, catalog_models))

    for path in _env_files():
        violations.extend(_env_llm_config_violations(path))

    if violations:
        print("[MODEL-LITERAL-SSOT] FAIL - provider model literals outside SSOT")
        for item in violations:
            safe_item = item.encode("ascii", errors="backslashreplace").decode("ascii")
            print(f"  {safe_item}")
        return 1

    print("[MODEL-LITERAL-SSOT] PASS - provider model literals are SSOT-contained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
