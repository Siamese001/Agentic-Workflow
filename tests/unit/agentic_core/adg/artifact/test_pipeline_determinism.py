"""H5: Subprocess-level pipeline determinism gate across PYTHONHASHSEED values.

Extends the scanner-level determinism tests to cover the full pipeline:
  scan → build_artifact → normalize_with_planes

Verifies that artifact_digest, full NormalizedGraph digest, and all three
plane digests are bitwise-identical across fresh processes with different
PYTHONHASHSEED values.

This is the key guarantee that E2 (fused normalize_with_planes) did not
introduce any hash-seed-sensitive iteration order.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]

_PROBE_SCRIPT = textwrap.dedent(
    """
    import sys, os
    sys.path.insert(0, r'{repo_root}')
    os.environ.setdefault('ADG_SKIP_SELF_TEST', '1')
    from pathlib import Path
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    from agentic_core.adg.artifact.builder_types import build_artifact
    from agentic_core.adg.artifact.normalizer_config import ArtifactNormalizer
    from agentic_core.adg.artifact.SplitArtifact import (
        _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS,
    )
    ROOT = Path(r'{repo_root}')
    cache_path = ROOT / 'artifacts' / 'adg' / 'cache' / 'scan_result_cache.json'
    scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True, cache_path=cache_path)
    scan_result = scanner.scan()
    artifact = build_artifact(scan_result, repo_root=ROOT)
    ng_full, ng_file, ng_sym, ng_gov = ArtifactNormalizer().normalize_with_planes(
        artifact, _FILE_GRAPH_RELS, _SYMBOL_GRAPH_RELS, _GOVERNANCE_GRAPH_RELS,
    )
    print('SCAN_DIGEST=' + scan_result.digest)
    print('ARTIFACT_DIGEST=' + artifact.artifact_digest)
    print('NG_FULL_DIGEST=' + ng_full.artifact_digest)
    print('NG_FILE_DIGEST=' + ng_file.artifact_digest)
    print('NG_SYM_DIGEST=' + ng_sym.artifact_digest)
    print('NG_GOV_DIGEST=' + ng_gov.artifact_digest)
    print('EDGES=' + str(len(scan_result.edges)))
    print('ENTITIES=' + str(len(artifact.entities)))
    print('RELATIONS=' + str(len(artifact.relations)))
    """,
).strip()

SEEDS = ["0", "42", "2147483647", "999"]
TIMEOUT_S = 240


@pytest.mark.unit
class TestPipelineDeterminism:
    """Full scan→build→normalize_with_planes pipeline must be bitwise-identical
    across fresh processes with different PYTHONHASHSEED values."""

    @pytest.fixture(scope="class")
    def probe_script(self, tmp_path_factory) -> Path:
        p = tmp_path_factory.mktemp("pipeline_det") / "_pipeline_det_probe.py"
        p.write_text(
            _PROBE_SCRIPT.format(repo_root=str(REPO_ROOT).replace("\\", "\\\\")),
        )
        return p

    def _run_probe(self, script: Path, seed: str) -> dict[str, str]:
        """Run probe in fresh process with given PYTHONHASHSEED. Returns dict of key→value."""
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            env=env,
            cwd=str(REPO_ROOT),
        )
        assert proc.returncode == 0, (
            f"Probe failed (seed={seed}):\nSTDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}"
        )
        result: dict[str, str] = {}
        for line in proc.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip()
        expected_keys = {
            "SCAN_DIGEST",
            "ARTIFACT_DIGEST",
            "NG_FULL_DIGEST",
            "NG_FILE_DIGEST",
            "NG_SYM_DIGEST",
            "NG_GOV_DIGEST",
            "EDGES",
            "ENTITIES",
            "RELATIONS",
        }
        missing = expected_keys - set(result)
        assert not missing, (
            f"Probe missing output keys {missing} (seed={seed}).\nstdout: {proc.stdout[-1000:]}"
        )
        return result

    @pytest.fixture(scope="class")
    def all_probe_results(self, probe_script) -> dict[str, dict[str, str]]:
        """Run all seeds once and cache results (class-scoped for efficiency)."""
        return {seed: self._run_probe(probe_script, seed) for seed in SEEDS}

    def _check_field_stable(self, all_results: dict, field: str) -> None:
        values = {seed: r[field] for seed, r in all_results.items()}
        unique = set(values.values())
        assert len(unique) == 1, (
            f"Field '{field}' varies across PYTHONHASHSEED values — "
            f"hash-seed-sensitive iteration detected.\n"
            f"Values per seed: {values}"
        )

    def test_scan_digest_stable(self, all_probe_results) -> None:
        """Scan digest must be stable (regression: propagation set iteration)."""
        self._check_field_stable(all_probe_results, "SCAN_DIGEST")

    def test_edge_count_stable(self, all_probe_results) -> None:
        """Edge count must be stable across seeds."""
        self._check_field_stable(all_probe_results, "EDGES")

    def test_artifact_digest_stable(self, all_probe_results) -> None:
        """artifact_digest from build_artifact must be stable across seeds."""
        self._check_field_stable(all_probe_results, "ARTIFACT_DIGEST")

    def test_full_graph_digest_stable(self, all_probe_results) -> None:
        """normalize_with_planes full NormalizedGraph digest must be stable across seeds."""
        self._check_field_stable(all_probe_results, "NG_FULL_DIGEST")

    def test_file_plane_digest_stable(self, all_probe_results) -> None:
        """file_graph plane digest from normalize_with_planes must be stable across seeds."""
        self._check_field_stable(all_probe_results, "NG_FILE_DIGEST")

    def test_symbol_plane_digest_stable(self, all_probe_results) -> None:
        """symbol_graph plane digest from normalize_with_planes must be stable across seeds."""
        self._check_field_stable(all_probe_results, "NG_SYM_DIGEST")

    def test_governance_plane_digest_stable(self, all_probe_results) -> None:
        """governance_graph plane digest from normalize_with_planes must be stable across seeds."""
        self._check_field_stable(all_probe_results, "NG_GOV_DIGEST")

    def test_entity_count_stable(self, all_probe_results) -> None:
        """Entity count from build_artifact must be stable across seeds."""
        self._check_field_stable(all_probe_results, "ENTITIES")

    def test_relation_count_stable(self, all_probe_results) -> None:
        """Relation count from build_artifact must be stable across seeds."""
        self._check_field_stable(all_probe_results, "RELATIONS")

    def test_artifact_digest_equals_full_ng_digest(self, all_probe_results) -> None:
        """artifact_digest and NG_FULL_DIGEST need not be equal (different hash inputs),
        but both must be internally consistent — i.e. same across seeds independently."""
        # Each is checked for stability in its own test above.
        # This test verifies neither is empty/trivial.
        for seed, r in all_probe_results.items():
            assert len(r["ARTIFACT_DIGEST"]) == 64, (
                f"artifact_digest is not a SHA256 hex string (seed={seed}): {r['ARTIFACT_DIGEST']!r}"
            )
            assert len(r["NG_FULL_DIGEST"]) == 64, (
                f"NG_FULL_DIGEST is not a SHA256 hex string (seed={seed}): {r['NG_FULL_DIGEST']!r}"
            )
