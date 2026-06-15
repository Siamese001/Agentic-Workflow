"""
tests/runtime/conftest.py

Session-scoped fixtures for the runtime requirements proof test suite.

These tests deliberately depend on the on-disk artifacts produced by
``python -m agentic_core.runtime.prove_requirements``. If artifacts are
missing, the fixtures invoke the CLI in a subprocess (with a bounded
timeout) so the test suite is self-bootstrapping.
"""

from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.constants import SOURCE_FOLDERS


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def export_dir(repo_root: Path) -> Path:
    return repo_root / "artifacts" / "runtime" / "requirements_proof"


def _artifact_manifest_is_current(repo_root: Path, manifest_path: Path) -> bool:
    """Return True when cached proof artifacts match current source folders."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    expected = set(SOURCE_FOLDERS)
    files = manifest.get("files", [])
    found: set[str] = set()
    for entry in files:
        rel = str(entry.get("relative_path", "")).replace("\\", "/")
        parts = rel.split("/")
        if len(parts) >= 3:
            found.add("/".join(parts[:3]))
        path = Path(str(entry.get("path", "")))
        if path and not path.exists():
            return False
        rel_path = entry.get("relative_path")
        if rel_path and not (repo_root / str(rel_path)).exists():
            return False
    return expected.issubset(found)


def _clear_stale_export_dir(repo_root: Path, export_dir: Path) -> None:
    """Remove the generated proof bundle before rebuilding stale artifacts."""
    expected = (repo_root / "artifacts" / "runtime" / "requirements_proof").resolve()
    resolved = export_dir.resolve()
    if resolved != expected:
        raise RuntimeError(f"refusing to clear unexpected proof export dir: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


@pytest.fixture(scope="session")
def proof_artifacts(repo_root: Path, export_dir: Path) -> Path:
    """
    Ensure source_manifest.json and requirements_index.json exist.

    If either is missing, run the CLI once with a 300s budget. Constitutional
    rule §14 mandates timeout= on every subprocess call.
    """
    manifest = export_dir / "source_manifest.json"
    index = export_dir / "requirements_index.json"
    if manifest.exists() and index.exists() and _artifact_manifest_is_current(repo_root, manifest):
        return export_dir
    _clear_stale_export_dir(repo_root, export_dir)

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "agentic_core.runtime.prove_requirements",
            "--repo-root",
            str(repo_root),
            "--export",
            "artifacts/runtime/requirements_proof",
        ],
        cwd=str(repo_root),
        env=env,
        check=True,
        timeout=300,
        shell=False,
    )
    if not manifest.exists() or not index.exists():
        raise RuntimeError(
            f"prove_requirements CLI did not produce expected artifacts "
            f"(manifest_exists={manifest.exists()}, index_exists={index.exists()})"
        )
    return export_dir


@pytest.fixture(scope="session")
def runtime_traces(proof_artifacts: Path) -> dict[str, dict]:
    """Load all four canonical scenario traces as parsed JSON dicts.

    Shared across the 10 spec-named per-stage contract tests so each test
    pays the parse cost exactly once per session.
    """
    import json as _json
    out: dict[str, dict] = {}
    traces_dir = proof_artifacts / "traces"
    for scen in ("A_grounded_read", "B_managed_workflow", "C_weak_evidence",
                 "D_anti_bypass", "E_authorized_commit"):
        path = traces_dir / f"scenario_{scen}.json"
        if not path.exists():
            raise RuntimeError(f"missing scenario trace at {path}")
        out[scen] = _json.loads(path.read_text(encoding="utf-8"))
    return out


@pytest.fixture(scope="session")
def spans_by_name(runtime_traces: dict[str, dict]) -> dict[str, dict[str, dict]]:
    """Index every trace's spans by name, for ergonomic per-stage lookups.

    Returns: {scenario_name: {span_name: span_dict}}
    """
    out: dict[str, dict[str, dict]] = {}
    for scen, trace in runtime_traces.items():
        out[scen] = {s["name"]: s for s in trace["spans"]}
    return out
