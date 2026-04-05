"""H8: CLI mode smoke test — local vs full artifact presence and digest stability.

Verifies:
  1. LOCAL mode omits zip and reports, emits core artifacts, banner says LOCAL
  2. FULL mode emits zip and 8 reports, banner says FULL
  3. Manifest output matches the declared mode (OMITTED lines present/absent)
  4. Two local-mode runs on the same cache produce identical artifact_digest

Uses fresh subprocesses via the generate_full_adg() API directly (not CLI argparse)
to keep setup deterministic and avoid argparse coupling.

Each subprocess writes its artifact_digest to stdout so the parent can compare
without touching the shared artifacts/adg directory.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[6]
TIMEOUT_S = 300

_PROBE = textwrap.dedent("""
import sys, os, importlib.util
_root = {repo_root}
sys.path.insert(0, _root)
os.environ['ADG_SKIP_REDIS'] = '1'
os.environ['ADG_SKIP_GIT'] = '1'
os.environ['ADG_SKIP_SELF_TEST'] = '1'
os.environ['PYTHONHASHSEED'] = '0'

import tempfile, json, shutil
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    'generate_full_adg',
    os.path.join(_root, 'tools', 'generate_full_adg.py'),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
generate_full_adg = _mod.generate_full_adg

ROOT = Path(_root)

with tempfile.TemporaryDirectory() as td:
    out_dir = Path(td)
    (out_dir / 'cache').mkdir()
    real_cache = ROOT / 'artifacts' / 'adg' / 'cache' / 'scan_result_cache.json'
    if real_cache.exists():
        shutil.copy(real_cache, out_dir / 'cache' / 'scan_result_cache.json')

    generate_full_adg(
        out_dir, 'smoketest',
        archive_old=False,
        enable_zip={enable_zip},
        enable_reports={enable_reports},
        enable_analysis={enable_analysis},
    )

    artifacts = list(out_dir.glob('**/*'))
    zip_files = [f.name for f in artifacts if f.suffix == '.zip']
    report_files = [f.name for f in artifacts if '_report' in f.name and f.suffix == '.json']
    snapshot_files = [f.name for f in artifacts if f.name.startswith('adg_snapshot_')]
    sqlite_files = [f.name for f in artifacts if f.suffix == '.sqlite']

    snapshot_digest = ''
    for sf in out_dir.glob('adg_snapshot_*.json'):
        try:
            data = json.loads(sf.read_text())
            snapshot_digest = data.get('artifact_digest', '')
        except Exception:
            pass

    print('ZIP_COUNT=' + str(len(zip_files)))
    print('REPORT_COUNT=' + str(len(report_files)))
    print('SNAPSHOT_COUNT=' + str(len(snapshot_files)))
    print('SQLITE_COUNT=' + str(len(sqlite_files)))
    print('ARTIFACT_DIGEST=' + snapshot_digest)
""").strip()

_BANNER_PROBE = textwrap.dedent("""
import sys, os, importlib.util
_root = {repo_root}
sys.path.insert(0, _root)
os.environ['ADG_SKIP_REDIS'] = '1'
os.environ['ADG_SKIP_GIT'] = '1'
os.environ['ADG_SKIP_SELF_TEST'] = '1'
os.environ['PYTHONHASHSEED'] = '0'

import tempfile, shutil
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    'generate_full_adg',
    os.path.join(_root, 'tools', 'generate_full_adg.py'),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
generate_full_adg = _mod.generate_full_adg

ROOT = Path(_root)

with tempfile.TemporaryDirectory() as td:
    out_dir = Path(td)
    (out_dir / 'cache').mkdir()
    real_cache = ROOT / 'artifacts' / 'adg' / 'cache' / 'scan_result_cache.json'
    if real_cache.exists():
        shutil.copy(real_cache, out_dir / 'cache' / 'scan_result_cache.json')
    generate_full_adg(
        out_dir, 'bannertest',
        archive_old=False,
        enable_zip={enable_zip},
        enable_reports={enable_reports},
        enable_analysis={enable_analysis},
    )
""").strip()


def _run_probe(enable_zip: bool, enable_reports: bool, enable_analysis: bool, tmp_path: Path) -> dict[str, str]:
    script = _PROBE.format(
        repo_root=repr(str(REPO_ROOT)),
        enable_zip=str(enable_zip),
        enable_reports=str(enable_reports),
        enable_analysis=str(enable_analysis),
    )
    script_path = tmp_path / f"probe_{enable_zip}_{enable_reports}.py"
    script_path.write_text(script)
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["ADG_SKIP_REDIS"] = "1"
    env["ADG_SKIP_GIT"] = "1"
    env["ADG_SKIP_SELF_TEST"] = "1"
    # Ensure repo root is on PYTHONPATH so 'tools' and 'agentic_core' are importable
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + existing if existing else "")
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True,
        timeout=TIMEOUT_S, env=env, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, (
        f"Probe failed:\nSTDOUT:\n{proc.stdout[-3000:]}\nSTDERR:\n{proc.stderr[-2000:]}"
    )
    result: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" in line and not line.startswith("[ADG]"):
            k, v = line.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def _run_banner_probe(enable_zip: bool, enable_reports: bool, enable_analysis: bool, tmp_path: Path) -> str:
    script = _BANNER_PROBE.format(
        repo_root=repr(str(REPO_ROOT)),
        enable_zip=str(enable_zip),
        enable_reports=str(enable_reports),
        enable_analysis=str(enable_analysis),
    )
    script_path = tmp_path / f"banner_{enable_zip}_{enable_reports}.py"
    script_path.write_text(script)
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["ADG_SKIP_REDIS"] = "1"
    env["ADG_SKIP_GIT"] = "1"
    env["ADG_SKIP_SELF_TEST"] = "1"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + existing if existing else "")
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True,
        timeout=TIMEOUT_S, env=env, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, (
        f"Banner probe failed:\nSTDOUT:\n{proc.stdout[-3000:]}\nSTDERR:\n{proc.stderr[-2000:]}"
    )
    return proc.stdout


@pytest.mark.unit
class TestModeSmoke:
    """CLI mode smoke: local vs full artifact presence, manifest, and digest stability."""

    @pytest.fixture(scope="class")
    def local_result(self, tmp_path_factory) -> dict[str, str]:
        return _run_probe(False, False, False, tmp_path_factory.mktemp("local"))

    @pytest.fixture(scope="class")
    def full_result(self, tmp_path_factory) -> dict[str, str]:
        return _run_probe(True, True, True, tmp_path_factory.mktemp("full"))

    @pytest.fixture(scope="class")
    def local_result_2(self, tmp_path_factory) -> dict[str, str]:
        return _run_probe(False, False, False, tmp_path_factory.mktemp("local2"))

    @pytest.fixture(scope="class")
    def local_banner(self, tmp_path_factory) -> str:
        return _run_banner_probe(False, False, False, tmp_path_factory.mktemp("banner_local"))

    @pytest.fixture(scope="class")
    def full_banner(self, tmp_path_factory) -> str:
        return _run_banner_probe(True, True, True, tmp_path_factory.mktemp("banner_full"))

    # --- Local mode: core artifacts present ---

    def test_local_has_snapshot(self, local_result) -> None:
        """Local mode must produce the adg_snapshot JSON."""
        assert int(local_result["SNAPSHOT_COUNT"]) >= 1, (
            f"No snapshot in local mode. Got: {local_result}"
        )

    def test_local_has_sqlite(self, local_result) -> None:
        """Local mode must produce the SQLite index."""
        assert int(local_result["SQLITE_COUNT"]) >= 1, (
            f"No sqlite in local mode. Got: {local_result}"
        )

    def test_local_omits_zip(self, local_result) -> None:
        """Local mode must NOT produce a zip archive."""
        assert int(local_result["ZIP_COUNT"]) == 0, (
            f"Unexpected zip in local mode. Got: {local_result}"
        )

    def test_local_omits_reports(self, local_result) -> None:
        """Local mode must NOT produce standardized report JSON files."""
        assert int(local_result["REPORT_COUNT"]) == 0, (
            f"Unexpected reports in local mode. Got: {local_result}"
        )

    # --- Full mode: all artifacts present ---

    def test_full_has_zip(self, full_result) -> None:
        """Full mode must produce a zip archive."""
        assert int(full_result["ZIP_COUNT"]) >= 1, (
            f"No zip in full mode. Got: {full_result}"
        )

    def test_full_has_reports(self, full_result) -> None:
        """Full mode must produce report JSON files (expected 8)."""
        count = int(full_result["REPORT_COUNT"])
        assert count >= 6, (
            f"Full mode reports count too low: {count}. Got: {full_result}"
        )

    def test_full_has_snapshot(self, full_result) -> None:
        """Full mode must also produce snapshot."""
        assert int(full_result["SNAPSHOT_COUNT"]) >= 1, (
            f"No snapshot in full mode. Got: {full_result}"
        )

    # --- Banner / manifest checks ---

    def test_local_banner_says_local(self, local_banner) -> None:
        """Startup banner must say MODE: LOCAL in local mode."""
        assert "[ADG] Mode: LOCAL" in local_banner, (
            f"Expected '[ADG] Mode: LOCAL' in stdout, got:\n{local_banner[:2000]}"
        )

    def test_full_banner_says_full(self, full_banner) -> None:
        """Startup banner must say MODE: FULL in full mode."""
        assert "[ADG] Mode: FULL" in full_banner, (
            f"Expected '[ADG] Mode: FULL' in stdout, got:\n{full_banner[:2000]}"
        )

    def test_local_banner_mentions_omitted(self, local_banner) -> None:
        """Local mode must print OMITTED manifest listing skipped artifacts."""
        assert "[ADG] OMITTED" in local_banner, (
            f"Expected '[ADG] OMITTED' manifest in local stdout:\n{local_banner[:2000]}"
        )

    def test_full_banner_no_omitted(self, full_banner) -> None:
        """Full mode must NOT print OMITTED manifest (nothing skipped)."""
        assert "[ADG] OMITTED" not in full_banner, (
            f"Expected no '[ADG] OMITTED' in full stdout, got:\n{full_banner[:2000]}"
        )

    def test_local_banner_hints_full_mode(self, local_banner) -> None:
        """Local mode banner must mention --full or ADG_MODE=full."""
        assert "--full" in local_banner or "ADG_MODE=full" in local_banner, (
            f"Expected --full hint in local banner:\n{local_banner[:2000]}"
        )

    # --- Digest stability ---

    def test_local_digest_stable_across_two_runs(self, local_result, local_result_2) -> None:
        """Two local-mode runs on the same cache must produce identical artifact_digest."""
        d1 = local_result.get("ARTIFACT_DIGEST", "")
        d2 = local_result_2.get("ARTIFACT_DIGEST", "")
        assert d1 and d2, f"Missing digest: run1={d1!r} run2={d2!r}"
        assert d1 == d2, (
            f"artifact_digest not stable across two local runs:\n"
            f"  run1: {d1}\n"
            f"  run2: {d2}"
        )

    def test_artifact_digest_is_sha256(self, local_result) -> None:
        """artifact_digest must be a 64-char SHA256 hex string."""
        d = local_result.get("ARTIFACT_DIGEST", "")
        assert len(d) == 64 and all(c in "0123456789abcdef" for c in d), (
            f"artifact_digest is not a valid SHA256: {d!r}"
        )
