#!/usr/bin/env python3
"""Gate D1 — layer doc-to-code binding (plan W3.4).

Warns when a canonical layer documentation directory under
`docs/reference/` has no corresponding active pipeline declared in
`config/canonical_pipelines.yaml`. This closes the doc → code loop:
every architectural doc folder must have at least one pipeline that
exercises code in its layer.

Tier: W (warn). Initially most layer folders will warn until the
canonical pipeline manifest grows to cover them. Add waivers or pipelines
to silence specific entries.

Layer-folder pattern:
    docs/reference/NN_L<digit>_<title>/
    e.g. docs/reference/03_L0_Routing/, 04_L1_Cognition/, ...

A pipeline 'covers' a layer folder when any of its stages has a module
whose resolved_path contains the layer id, OR `pipeline.ingress_layer`
matches.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

DOCS_ROOT = REPO_ROOT / "docs" / "reference"
MANIFEST = REPO_ROOT / "config" / "canonical_pipelines.yaml"
LAYER_DIR_PATTERN = re.compile(r"^\d+_L\d+_", re.IGNORECASE)


class LayerDocBindingGate(WiringGate):
    gate_id = "D1_layer_doc_binding"
    tier = "W"

    def run(self, conn) -> list[Violation]:  # conn unused
        _ = conn
        if not DOCS_ROOT.is_dir():
            return []
        manifest = _load_manifest()
        covered = _covered_layers(manifest)

        violations: list[Violation] = []
        for entry in sorted(DOCS_ROOT.iterdir()):
            if not entry.is_dir():
                continue
            if not LAYER_DIR_PATTERN.match(entry.name):
                continue
            layer_id = _extract_layer_id(entry.name)
            if not layer_id:
                continue
            if layer_id in covered:
                continue
            rel = entry.relative_to(REPO_ROOT).as_posix()
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=rel,
                    rule="layer_doc_unbound",
                    detail=(
                        f"docs folder for {layer_id} has no canonical pipeline "
                        f"in {MANIFEST.relative_to(REPO_ROOT).as_posix()}; "
                        "add a pipeline or waive"
                    ),
                    severity="warn",
                    extra={"layer_id": layer_id, "doc_dir": rel},
                )
            )
        return violations


def _load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"pipelines": []}
    try:
        return yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {"pipelines": []}


def _covered_layers(manifest: dict) -> set[str]:
    out: set[str] = set()
    for pipeline in manifest.get("pipelines", []) or []:
        ingress = pipeline.get("ingress_layer")
        if ingress:
            out.add(ingress)
        for stage in pipeline.get("stages", []) or []:
            if stage.get("status") != "active":
                continue
            module = stage.get("module") or ""
            for layer in _layers_from_path(module):
                out.add(layer)
    return out


def _layers_from_path(module: str) -> list[str]:
    # Extract L<digit> segments from resolved paths like
    # 'agentic_core/L0_routing/...', 'agentic_core/L1_cognition/...'.
    hits: list[str] = []
    for part in module.split("/"):
        m = re.match(r"^L(\d+)_", part)
        if m:
            hits.append(f"L{m.group(1)}")
    return hits


def _extract_layer_id(dir_name: str) -> str | None:
    m = re.match(r"^\d+_L(\d+)_", dir_name, re.IGNORECASE)
    if not m:
        return None
    return f"L{m.group(1)}"


def main() -> int:
    return cli_exit(LayerDocBindingGate().execute())


if __name__ == "__main__":
    sys.exit(main())
