"""Regression gate: ADG scanner determinism across PYTHONHASHSEED values.

Catches two classes of non-determinism that were found and fixed:
  1. set-iteration order in _propagate_violations (caused variable edge counts)
  2. non-total _EDGE_SORT_KEY that didn't cover all canonical_edge_text() fields
     (caused same edge set to produce different digests across processes)

Strategy: spawn N fresh subprocesses with different PYTHONHASHSEED values,
collect edge count + final digest from each, assert all agree.

This test is intentionally placed in the scanner extraction unit suite so it
runs with the normal test collection.  It uses subprocess (not threading) to
guarantee each run gets an independent hash seed.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

_PROBE_SCRIPT = textwrap.dedent(
    r"""
    import sys, os
    sys.path.insert(0, r'{repo_root}')
    os.environ.setdefault('ADG_SKIP_SELF_TEST', '1')
    from pathlib import Path
    from agentic_core.adg.extraction.static_scanner import (
        ADGStaticScanner, _propagate_violations, _EDGE_SORT_KEY,
        ScanResult, ScanManifest,
    )
    ROOT = Path(r'{repo_root}')
    cache_path = ROOT / 'artifacts' / 'adg' / 'cache' / 'scan_result_cache.json'
    scanner = ADGStaticScanner(
        repo_root=ROOT,
        include_tests=True,
        cache_path=cache_path,
    )
    result = scanner.scan()
    print(f'EDGES={{len(result.edges)}}')
    print(f'DIGEST={{result.digest}}')
    """,
).strip()

SEEDS = ["0", "1", "42", "2147483647"]
TIMEOUT_S = 180


@pytest.mark.unit
class TestScannerDeterminism:
    """Scanner must produce identical edge count and digest regardless of PYTHONHASHSEED."""

    @pytest.fixture(scope="class")
    def probe_script(self, tmp_path_factory) -> Path:
        p = tmp_path_factory.mktemp("det") / "_det_probe.py"
        p.write_text(
            _PROBE_SCRIPT.format(repo_root=str(REPO_ROOT).replace("\\", "\\\\")),
        )
        return p

    def _run_probe(self, script: Path, seed: str) -> tuple[int, str]:
        """Run probe in fresh process with given PYTHONHASHSEED. Returns (edge_count, digest)."""
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        proc = subprocess.run(  # noqa: S603
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            env=env,
            cwd=str(REPO_ROOT),
        )
        assert proc.returncode == 0, (
            f"Probe failed (seed={seed}):\nSTDOUT:\n{proc.stdout[-2000:]}\n"
            f"STDERR:\n{proc.stderr[-2000:]}"
        )
        edges = digest = None
        for line in proc.stdout.splitlines():
            if line.startswith("EDGES="):
                edges = int(line.split("=", 1)[1])
            elif line.startswith("DIGEST="):
                digest = line.split("=", 1)[1].strip()
        assert edges is not None, f"No EDGES line in output (seed={seed}): {proc.stdout}"
        assert digest is not None, f"No DIGEST line in output (seed={seed}): {proc.stdout}"
        return edges, digest

    def test_edge_count_stable_across_hash_seeds(self, probe_script):
        """Edge count must be identical across all PYTHONHASHSEED values.

        Regression for: set-iteration nondeterminism in _propagate_violations
        causing variable propagation edge counts per process.
        """
        results = {}
        for seed in SEEDS:
            edge_count, digest = self._run_probe(probe_script, seed)
            results[seed] = (edge_count, digest)

        counts = {seed: v[0] for seed, v in results.items()}
        unique_counts = set(counts.values())
        assert len(unique_counts) == 1, (
            f"Edge count varies across PYTHONHASHSEED values — set-iteration nondeterminism detected.\n"
            f"Counts per seed: {counts}"
        )

    def test_digest_stable_across_hash_seeds(self, probe_script):
        """Final digest must be identical across all PYTHONHASHSEED values.

        Regression for: _EDGE_SORT_KEY covering only 5 of the 7 canonical_edge_text()
        fields, leaving edge_kind and symbol as tie-breakers resolved by set() iteration
        order (PYTHONHASHSEED-dependent).
        """
        results = {}
        for seed in SEEDS:
            edge_count, digest = self._run_probe(probe_script, seed)
            results[seed] = (edge_count, digest)

        digests = {seed: v[1] for seed, v in results.items()}
        unique_digests = set(digests.values())
        assert len(unique_digests) == 1, (
            f"Digest varies across PYTHONHASHSEED values — sort key is not total over canonical fields.\n"
            f"Digests per seed: {digests}"
        )

    def test_sort_key_covers_canonical_text_fields(self):
        """_EDGE_SORT_KEY tuple length must be >= number of fields in canonical_edge_text().

        canonical_edge_text uses: from_name, relation_type, to_name, edge_kind,
        source_file, line_no, symbol  (7 fields).
        Sort key must include all of them to be a total order.
        """
        from agentic_core.adg.extraction.static_scanner import _EDGE_SORT_KEY, Edge

        e = Edge(
            from_name="ADG::Module::a.py",
            relation_type="imports",
            to_name="ADG::Module::b.py",
            edge_kind="static",
            source_file="a.py",
            line_no=1,
            symbol="foo",
            semantic_type="structural",
            confidence=1.0,
        )
        key = _EDGE_SORT_KEY(e)
        assert len(key) >= 7, (
            f"_EDGE_SORT_KEY returns only {len(key)} elements; "
            f"needs >= 7 to be total over canonical_edge_text() fields.\n"
            f"Current key: {key}"
        )
        assert e.from_name in key, "from_name must be in sort key"
        assert e.relation_type in key, "relation_type must be in sort key"
        assert e.to_name in key, "to_name must be in sort key"
        assert e.edge_kind in key, "edge_kind must be in sort key"
        assert e.source_file in key, "source_file must be in sort key"
        assert e.line_no in key, "line_no must be in sort key"

    def test_propagation_uses_sorted_iteration(self):
        """_propagate_violations must not iterate bare sets.

        Exercises the fixed code path with a minimal synthetic ScanResult
        containing two violation edges with shared importers, verifying the
        output list is in stable sorted order regardless of internal set state.
        """
        from agentic_core.adg.extraction.static_scanner import (
            Edge,
            ScanManifest,
            ScanResult,
            _propagate_violations,
        )

        def _make_edge(fr, rel, to, kind="static"):
            return Edge(
                from_name=fr, relation_type=rel, to_name=to,
                edge_kind=kind, source_file="", line_no=0,
            )

        mod_a = "ADG::Module::apps_rg/bad.py"
        mod_b = "ADG::Module::apps_rg/good.py"
        mod_c = "ADG::Module::apps_lic/consumer.py"
        sym_a = "ADG::Symbol::apps_rg.bad"
        sym_b = "ADG::Symbol::apps_rg.good"

        result = ScanResult()
        result.manifest = ScanManifest()
        result.modules = []
        result.edges = [
            _make_edge(mod_a, "violates", "ADG::Layer::L5"),
            _make_edge(mod_c, "imports", sym_a),
            _make_edge(mod_c, "imports", sym_b),
            _make_edge(mod_b, "violates", "ADG::Layer::L5"),
        ]

        prop = _propagate_violations(result)

        from_names = [e.from_name for e in prop]
        to_names = [e.to_name for e in prop]

        assert all(e.relation_type == "violation_propagates_through" for e in prop)
        assert all(fn in (mod_a, mod_b) for fn in from_names)
        assert all(tn == mod_c for tn in to_names)

        pairs = [(e.from_name, e.to_name) for e in prop]
        assert pairs == sorted(pairs), (
            f"Propagation edges are not in sorted order — set iteration leak.\n"
            f"Got: {pairs}\nExpected sorted: {sorted(pairs)}"
        )
