# Core pytest configuration
import pytest

# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path
    return Path(__file__).parent / "test_data"

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"

# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")

"""Root conftest.py — ADG-accelerated pytest integration.

Adds two opt-in capabilities controlled by environment variables:

1. **ADG_SCOPE** — scoped test selection.
   Set ``ADG_SCOPE=a/b/c.py,d/e/f.py`` (comma-separated changed files) and
   pytest will deselect any test that does NOT cover any of those modules
   (or their transitive importers) according to the live ADG scan.

   Example::

       ADG_SCOPE=agentic_core/L0_routing/config/path_constants.py pytest tests/

2. **ADG_GROUPS** — parallel worker assignment hint printed to stderr.
   Set ``ADG_GROUPS=4`` to print a layer-balanced partition of test files
   for use with ``pytest-xdist``.  Does not affect collection.

Both variables are optional.  When neither is set the conftest is a no-op
and adds zero overhead.
"""

from __future__ import annotations

import logging
import os
import pathlib
import sys
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

_ROOT = pathlib.Path(__file__).resolve().parent


def _build_adg_index():
    """Lazy-build the ADGIndex only when ADG features are requested."""
    try:
        if str(_ROOT) not in sys.path:
            sys.path.insert(0, str(_ROOT))
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
        from tools.adg_test_accelerator import ADGIndex

        scanner = ADGStaticScanner(include_tests=True)
        result = scanner.scan()
        return ADGIndex(result)
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"[ADG conftest] index build failed: {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# ADG_SCOPE — scoped test deselection
# ---------------------------------------------------------------------------


def pytest_collection_modifyitems(config, items):
    scope_env = os.environ.get("ADG_SCOPE", "").strip()
    if not scope_env:
        return

    changed = [c.strip() for c in scope_env.split(",") if c.strip()]
    if not changed:
        return

    print(
        f"\n[ADG_SCOPE] Building ADG index for {len(changed)} changed file(s)…",
        file=sys.stderr,
    )
    idx = _build_adg_index()
    if idx is None:
        print("[ADG_SCOPE] Falling back to full suite (index unavailable).", file=sys.stderr)
        return

    impacted_tests = idx.tests_for_changed(changed)
    if not impacted_tests:
        print(
            "[ADG_SCOPE] No ADG coverage signal found — running full suite.",
            file=sys.stderr,
        )
        return

    # Normalise to forward-slash relative paths for comparison
    norm_impacted = {p.replace("\\", "/") for p in impacted_tests}

    selected, deselected = [], []
    for item in items:
        item_path = str(item.fspath).replace("\\", "/")
        # make relative to repo root
        try:
            rel = str(pathlib.Path(item_path).relative_to(_ROOT)).replace("\\", "/")
        except ValueError as e:
            # TODO: Add proper input validation
            logger.warning(f"Invalid input: {e}")
            # Item path is outside repo root, use absolute path
            rel = item_path

        if any(rel == t or rel.startswith(t.rstrip(".py")) for t in norm_impacted):
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
        print(
            f"[ADG_SCOPE] Selected {len(selected)}/{len(selected) + len(deselected)} tests "
            f"covering {len(changed)} changed file(s).",
            file=sys.stderr,
        )


# ---------------------------------------------------------------------------
# ADG_GROUPS — parallel worker hint
# ---------------------------------------------------------------------------


def pytest_sessionstart(session):
    groups_env = os.environ.get("ADG_GROUPS", "").strip()
    if not groups_env:
        return
    try:
        n = int(groups_env)
    except ValueError:
        # Invalid ADG_GROUPS value - default to single worker
        print(f"[WARNING] Invalid ADG_GROUPS value: {groups_env}, using single worker", file=sys.stderr)
        return

    print(f"\n[ADG_GROUPS] Building layer-balanced partition for {n} workers…", file=sys.stderr)
    idx = _build_adg_index()
    if idx is None:
        return

    from collections import defaultdict

    all_test_files = sorted(
        {
            e.source_file.replace("\\", "/")
            for e in idx.result.edges
            if "tests/" in e.source_file.replace("\\", "/")
        }
    )

    by_layer: dict[str, list[str]] = defaultdict(list)
    for tf in all_test_files:
        by_layer[idx.layer_of(tf)].append(tf)

    workers: list[list[str]] = [[] for _ in range(n)]
    sizes = [0] * n
    for layer in sorted(by_layer, key=lambda l: -len(by_layer[l])):
        target = min(range(n), key=lambda i: sizes[i])
        workers[target].extend(by_layer[layer])
        sizes[target] += len(by_layer[layer])

    print("[ADG_GROUPS] Layer distribution:", file=sys.stderr)
    for layer, files in sorted(by_layer.items(), key=lambda kv: -len(kv[1])):
        print(f"  {layer:<12} {len(files):4d} files", file=sys.stderr)

    print("\n[ADG_GROUPS] Worker assignments:", file=sys.stderr)
    for i, group in enumerate(workers):
        print(f"  worker_{i}: {len(group)} files", file=sys.stderr)