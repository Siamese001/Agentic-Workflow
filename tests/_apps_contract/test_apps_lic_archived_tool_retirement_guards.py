"""W8 quarantine guard tests for 7 retired archived ADG-dead apps_lic tools.

Plan: apps-lic-quarantine-u0-coverage-review-d9f4a2
Wave: W8 — Retirement Receipts + Quarantine Guard Tests

These tests prove that the 7 archived tools with RETIRE_WITH_RECEIPT disposition
are not importable, not referenced, and not exposed through any active runtime path.

Hard rules:
- Tests do NOT import archived tools as executable modules.
- Tests inspect paths and text only.
- Artifact/doc/test references are allowed and excluded from scans.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

ARCHIVED_TOOL_PATHS = {
    "AggregateCampaignState": REPO_ROOT / "archives/adg_dead_code/2026-04-23/apps_lic/tools/AggregateCampaignState.py",
    "ComputePersonalizationMatch": REPO_ROOT / "archives/adg_dead_code/2026-04-23/apps_lic/tools/ComputePersonalizationMatch.py",
    "DiagnosePersonalizationIssues": REPO_ROOT / "archives/adg_dead_code/2026-04-23/apps_lic/tools/DiagnosePersonalizationIssues.py",
    "LogCampaignMetrics": REPO_ROOT / "archives/adg_dead_code/2026-04-23/apps_lic/tools/LogCampaignMetrics.py",
    "SearchSimilarMessages": REPO_ROOT / "archives/adg_dead_code/2026-04-23/apps_lic/tools/SearchSimilarMessages.py",
    "SnapshotCampaignState": REPO_ROOT / "archives/adg_dead_code/2026-04-23/apps_lic/tools/SnapshotCampaignState.py",
    "UpdateRecipientProfiles": REPO_ROOT / "archives/adg_dead_code/2026-04-23/apps_lic/tools/UpdateRecipientProfiles.py",
}

ACTIVE_RUNTIME_ROOTS = [
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "agentic_core",
]

ALLOWED_REFERENCE_DIRS = {
    "artifacts",
    "tests",
    "__pycache__",
    ".git",
}

ALLOWED_REFERENCE_FILENAMES = {
    "golden_baseline.json",
}

ACTIVE_TEXT_SUFFIXES = {".py", ".yaml", ".yml", ".json", ".toml"}


def _iter_active_runtime_files() -> list[Path]:
    """Collect all text files under active runtime roots, excluding allowed dirs."""
    files: list[Path] = []
    for root in ACTIVE_RUNTIME_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in ACTIVE_TEXT_SUFFIXES:
                continue
            if any(part in ALLOWED_REFERENCE_DIRS for part in path.parts):
                continue
            if path.name in ALLOWED_REFERENCE_FILENAMES:
                continue
            files.append(path)
    return files


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# ── Test 1: archived files remain in archive only ──────────────────────


def test_archived_retirement_tool_files_remain_in_archive_only() -> None:
    """Each retired tool file exists in archives/ and nowhere else."""
    for tool_name, path in ARCHIVED_TOOL_PATHS.items():
        assert path.exists(), f"{tool_name} archive file missing: {path}"
        rel = path.relative_to(REPO_ROOT).as_posix()
        assert rel.startswith("archives/adg_dead_code/2026-04-23/apps_lic/tools/"), (
            f"{tool_name} not under expected archive path: {rel}"
        )


# ── Test 2: not exposed by apps_lic entrypoint ─────────────────────────


def test_archived_retirement_tools_are_not_exposed_by_apps_lic_entrypoint() -> None:
    """No archived tool class name appears in apps_lic/__main__.py."""
    entrypoint = REPO_ROOT / "apps_lic/__main__.py"
    assert entrypoint.exists()
    content = _text(entrypoint)

    for tool_name in ARCHIVED_TOOL_PATHS:
        assert tool_name not in content, (
            f"Archived tool {tool_name} found in apps_lic/__main__.py"
        )


# ── Test 3: not exposed by spine manifest ───────────────────────────────


def test_archived_retirement_tools_are_not_exposed_by_spine_manifest() -> None:
    """No archived tool class name appears in apps_lic/spine_manifest.yaml."""
    manifest = REPO_ROOT / "apps_lic/spine_manifest.yaml"
    assert manifest.exists()
    content = _text(manifest)

    for tool_name in ARCHIVED_TOOL_PATHS:
        assert tool_name not in content, (
            f"Archived tool {tool_name} found in apps_lic/spine_manifest.yaml"
        )


# ── Test 4: not imported by active runtime ──────────────────────────────


def test_archived_retirement_tools_are_not_imported_by_active_runtime() -> None:
    """No active runtime file imports any archived tool by name."""
    active_files = _iter_active_runtime_files()
    assert active_files, "active runtime files should be discoverable"

    forbidden_fragments = []
    for tool_name in ARCHIVED_TOOL_PATHS:
        forbidden_fragments.extend(
            [
                f"from archives.adg_dead_code",
                f"from apps_lic.tools import {tool_name}",
                f"from apps_lic.tools.{tool_name}",
                f"apps_lic.tools.{tool_name}",
            ]
        )

    offenders: list[str] = []
    for path in active_files:
        content = _text(path)
        for fragment in forbidden_fragments:
            if fragment in content:
                rel = path.relative_to(REPO_ROOT).as_posix()
                offenders.append(f"{rel} contains {fragment!r}")

    assert offenders == [], (
        "Active runtime files import archived tools:\n"
        + "\n".join(offenders)
    )


# ── Test 5: tool names absent from active runtime sources ───────────────


def test_archived_retirement_tool_names_do_not_appear_in_active_runtime_sources() -> None:
    """No active runtime .py/.yaml/.json file references an archived tool class name."""
    active_files = _iter_active_runtime_files()

    offenders: list[str] = []
    for path in active_files:
        content = _text(path)
        for tool_name in ARCHIVED_TOOL_PATHS:
            if tool_name in content:
                rel = path.relative_to(REPO_ROOT).as_posix()
                offenders.append(f"{rel} contains archived tool name {tool_name}")

    assert offenders == [], (
        "Active runtime files reference archived tool names:\n"
        + "\n".join(offenders)
    )
