"""ADG Placement Advisor — suggest canonical placement for new files/symbols.

Uses the ADG import graph and layer metadata to:
  - Suggest where a new file/agent/config should be placed
  - Provide structural context for an existing file or symbol
  - Identify nearby config dependencies, tests, and structural risks

Confidence levels:
  EXACT      — path determined from naming convention + existing layer map
  HIGH       — strong signal from territory + neighbors
  MEDIUM     — inferred from kind + related module patterns
  LOW        — weak signal, manual review recommended

No speculative inference beyond structural graph facts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

# Canonical kind → layer/path mapping
_KIND_PLACEMENT_MAP: dict[str, dict] = {
    "agent": {
        "layer": "L1",
        "path_template": "agentic_core/L1_cognition/agents/{name}.py",
        "note": "L1 agents implement cognition/reasoning; must route through L0 gateway",
        "confidence": "HIGH",
    },
    "execution_agent": {
        "layer": "L2",
        "path_template": "agentic_core/L2_execution/{name}.py",
        "note": "L2 handles execution, write side effects, and LLM gateway enforcement",
        "confidence": "HIGH",
    },
    "orchestrator": {
        "layer": "L3",
        "path_template": "agentic_core/L3_orchestration/{name}.py",
        "note": "L3 orchestrates multi-agent workflows; may import L0-L2",
        "confidence": "HIGH",
    },
    "state": {
        "layer": "L4",
        "path_template": "agentic_core/L4_state/{name}.py",
        "note": "L4 manages persistent state; may import L0-L3",
        "confidence": "HIGH",
    },
    "safety": {
        "layer": "L5",
        "path_template": "agentic_core/L5_safety/{name}.py",
        "note": "L5 enforces safety rules; can import L0-L4",
        "confidence": "HIGH",
    },
    "observability": {
        "layer": "L6",
        "path_template": "agentic_core/L6_observability/{name}.py",
        "note": "L6 observability/logging; can import L0-L5",
        "confidence": "HIGH",
    },
    "config": {
        "layer": "L_SHARED",
        "path_template": "agentic_core/config/{name}.py",
        "note": "Config constants and settings; importable from all layers",
        "confidence": "HIGH",
    },
    "mixin": {
        "layer": "L_SHARED",
        "path_template": "agentic_core/mixins/{name}.py",
        "note": "Shared mixins; importable from all layers via L_SHARED",
        "confidence": "HIGH",
    },
    "util": {
        "layer": "L_SHARED",
        "path_template": "agentic_core/utils/{name}.py",
        "note": "Shared utilities; importable from all layers via L_SHARED",
        "confidence": "HIGH",
    },
    "tool": {
        "layer": "L_TOOLS",
        "path_template": "tools/{name}.py",
        "note": "Developer/CI tools; L_TOOLS layer; can import L0-L5 + L_SHARED",
        "confidence": "HIGH",
    },
    "app": {
        "layer": "L_APP",
        "path_template": "apps_rg/{name}.py",
        "note": "Application layer; can import all agentic_core layers",
        "confidence": "MEDIUM",
    },
    "test": {
        "layer": "L_TEST",
        "path_template": "tests/unit/test_{name}.py",
        "note": "Test files; L_TEST can import anything",
        "confidence": "HIGH",
    },
    "router": {
        "layer": "L0",
        "path_template": "agentic_core/L0_routing/{name}.py",
        "note": "L0 routing layer; lowest in hierarchy; no upward imports",
        "confidence": "HIGH",
    },
}


@dataclass
class PlacementSuggestion:
    """Suggested placement for a new file or symbol."""

    kind: str
    name: str
    suggested_path: str
    layer: str
    confidence: str
    note: str
    allowed_importers: list[str] = field(default_factory=list)
    allowed_imports: list[str] = field(default_factory=list)
    similar_existing: list[str] = field(default_factory=list)
    structural_risks: list[str] = field(default_factory=list)
    unresolved_caveats: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "name": self.name,
            "suggested_path": self.suggested_path,
            "layer": self.layer,
            "confidence": self.confidence,
            "note": self.note,
            "allowed_importers": self.allowed_importers,
            "allowed_imports": self.allowed_imports,
            "similar_existing": self.similar_existing[:10],
            "structural_risks": self.structural_risks,
            "unresolved_caveats": self.unresolved_caveats,
        }


@dataclass
class FileContext:
    """Structural context for an existing file or symbol."""

    target: str
    target_type: str  # "file" or "symbol"
    layer: str
    territory: str
    nearest_trusted_neighbors: list[dict] = field(default_factory=list)
    direct_importers: list[str] = field(default_factory=list)
    direct_imports: list[str] = field(default_factory=list)
    config_dependencies: list[str] = field(default_factory=list)
    likely_tests: list[str] = field(default_factory=list)
    structural_risks: list[str] = field(default_factory=list)
    duplicate_definitions: list[str] = field(default_factory=list)
    unresolved_blind_spots: list[str] = field(default_factory=list)
    confidence: str = "HIGH"
    confidence_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "target_type": self.target_type,
            "layer": self.layer,
            "territory": self.territory,
            "confidence": self.confidence,
            "confidence_notes": self.confidence_notes,
            "nearest_trusted_neighbors": self.nearest_trusted_neighbors[:10],
            "direct_importers": self.direct_importers[:20],
            "direct_imports": self.direct_imports[:20],
            "config_dependencies": self.config_dependencies[:10],
            "likely_tests": self.likely_tests[:10],
            "structural_risks": self.structural_risks,
            "duplicate_definitions": self.duplicate_definitions[:5],
            "unresolved_blind_spots": self.unresolved_blind_spots[:5],
        }


class PlacementAdvisor:
    """Suggest placement and provide context using ADG structural signals.

    Usage
    -----
    advisor = PlacementAdvisor(result, repo_root=Path("."))
    suggestion = advisor.suggest_placement(kind="agent", name="NewResumeAgent")
    context = advisor.get_file_context("apps_rg/agents/resume_agent.py")
    """

    def __init__(
        self,
        result: ScanResult,
        repo_root: Path | None = None,
    ) -> None:
        self._result = result
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._reverse_deps: dict[str, set[str]] | None = None
        self._forward_deps: dict[str, set[str]] | None = None
        self._config_reads: dict[str, list[str]] | None = None

    def _build_deps(self) -> None:
        if self._reverse_deps is not None:
            return
        rev: dict[str, set[str]] = {}
        fwd: dict[str, set[str]] = {}
        cfg: dict[str, list[str]] = {}
        for edge in self._result.edges:
            if edge.relation_type == "imports":
                if edge.to_name not in rev:
                    rev[edge.to_name] = set()
                rev[edge.to_name].add(edge.from_name)
                if edge.from_name not in fwd:
                    fwd[edge.from_name] = set()
                fwd[edge.from_name].add(edge.to_name)
            elif edge.relation_type == "reads_from":
                sym = edge.symbol or ""
                if edge.from_name not in cfg:
                    cfg[edge.from_name] = []
                if sym and sym not in cfg[edge.from_name]:
                    cfg[edge.from_name].append(sym)
        self._reverse_deps = rev
        self._forward_deps = fwd
        self._config_reads = cfg

    def suggest_placement(self, kind: str, name: str) -> PlacementSuggestion:
        """Suggest canonical placement for a new file/symbol of the given kind."""
        import uuid  # noqa: PLC0415
        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"PlacementAdvisor.suggest_placement:{kind}/{name}")
        from agentic_core.adg.schema import ALLOWED_LAYER_EDGES, module_path_to_layer

        self._build_deps()
        kind_lower = kind.lower().replace("-", "_").replace(" ", "_")
        placement = _KIND_PLACEMENT_MAP.get(kind_lower)

        if placement is None:
            return PlacementSuggestion(
                kind=kind,
                name=name,
                suggested_path=f"agentic_core/L_UNKNOWN/{name}.py",
                layer="L_UNKNOWN",
                confidence="LOW",
                note=f"Unknown kind '{kind}'. Known kinds: {sorted(_KIND_PLACEMENT_MAP.keys())}",
                structural_risks=[f"Kind '{kind}' not in known placement map — manual review required"],
                unresolved_caveats=[f"No canonical territory for kind='{kind}'"],
            )

        suggested_path = placement["path_template"].format(name=name)
        layer = placement["layer"]

        # Find similar existing modules in same layer
        similar: list[str] = []
        for mod_path in sorted(self._result.modules):
            if module_path_to_layer(mod_path) == layer:
                similar.append(mod_path)

        # Allowed importers and imports per layer rules
        allowed_importers = sorted({fl for (fl, tl) in ALLOWED_LAYER_EDGES if tl == layer} | {layer})
        allowed_imports = sorted({tl for (fl, tl) in ALLOWED_LAYER_EDGES if fl == layer} | {layer})

        # Structural risks
        risks: list[str] = []
        if layer == "L0":
            risks.append("L0 modules CANNOT import upward into L1-L6; violation triggers RULE_C")
        if "gateway" in name.lower() and layer not in ("L2", "L0"):
            risks.append(f"Gateway classes should live in L2; found placement in {layer}")

        return PlacementSuggestion(
            kind=kind,
            name=name,
            suggested_path=suggested_path,
            layer=layer,
            confidence=placement["confidence"],
            note=placement["note"],
            allowed_importers=allowed_importers,
            allowed_imports=allowed_imports,
            similar_existing=similar[:10],
            structural_risks=risks,
        )

    def get_file_context(self, file_path: str) -> FileContext:
        """Get structural context for an existing file."""
        from agentic_core.adg.schema import module_path_to_layer
        from tools.test_coverage_mapper import TestCoverageMapper

        self._build_deps()
        norm_path = file_path.replace("\\", "/")
        layer = module_path_to_layer(norm_path)
        adg = _MODULE_PREFIX + norm_path

        # Direct importers
        importers = sorted(
            adg_name[len(_MODULE_PREFIX) :]
            for adg_name in self._reverse_deps.get(adg, set())  # type: ignore[union-attr]
            if adg_name.startswith(_MODULE_PREFIX)
        )

        # Direct imports
        direct_imports = sorted(
            adg_name[len(_MODULE_PREFIX) :]
            for adg_name in self._forward_deps.get(adg, set())  # type: ignore[union-attr]
            if adg_name.startswith(_MODULE_PREFIX)
        )

        # Config reads
        config_deps = sorted(self._config_reads.get(adg, []))  # type: ignore[union-attr]

        # Likely tests
        mapper = TestCoverageMapper(self._result, repo_root=self._repo_root).build()
        likely_tests = mapper.tests_for_module(norm_path)

        # Nearest trusted neighbors (same layer, shared edges)
        neighbor_paths = set(importers) | set(direct_imports)
        trusted_neighbors: list[dict] = []
        for np in sorted(neighbor_paths):
            np_layer = module_path_to_layer(np)
            trusted_neighbors.append(
                {
                    "path": np,
                    "layer": np_layer,
                    "relation": "importer" if np in importers else "dependency",
                }
            )

        # Structural risks
        risks: list[str] = []
        if layer == "L_UNKNOWN":
            risks.append("Module layer is L_UNKNOWN — add to LAYER_PREFIXES in schema.py")
        if len(importers) > 30:
            risks.append(f"High fan-in ({len(importers)} importers) — changes here are high blast radius")

        # Unresolved blind spots: imports that don't resolve to known modules
        blind_spots: list[str] = []
        for adg_name in self._forward_deps.get(adg, set()):  # type: ignore[union-attr]
            if adg_name.startswith(_SYMBOL_PREFIX):
                sym_name = adg_name[len(_SYMBOL_PREFIX) :]
                blind_spots.append(f"unresolved_symbol:{sym_name}")

        # Confidence notes
        conf_notes: list[str] = []
        if norm_path not in self._result.modules:
            conf_notes.append(f"WARNING: {norm_path} not in ADG index — results may be stale")

        territory = _infer_territory(norm_path, layer)

        return FileContext(
            target=norm_path,
            target_type="file",
            layer=layer,
            territory=territory,
            nearest_trusted_neighbors=trusted_neighbors[:10],
            direct_importers=importers[:20],
            direct_imports=direct_imports[:20],
            config_dependencies=config_deps[:10],
            likely_tests=likely_tests[:10],
            structural_risks=risks,
            unresolved_blind_spots=blind_spots[:5],
            confidence="HIGH" if norm_path in self._result.modules else "LOW",
            confidence_notes=conf_notes,
        )

    def get_symbol_context(self, qualified_name: str) -> FileContext:
        """Get structural context for a qualified symbol name."""
        from agentic_core.adg.schema import module_path_to_layer

        self._build_deps()
        adg = _SYMBOL_PREFIX + qualified_name

        # Find which module this symbol belongs to
        parent_path = ""
        if "." in qualified_name:
            parent_dot = ".".join(qualified_name.split(".")[:-1])
            candidate = parent_dot.replace(".", "/") + ".py"
            if candidate in self._result.modules:
                parent_path = candidate

        # Importers of this symbol
        importers = sorted(
            adg_name[len(_MODULE_PREFIX) :]
            for adg_name in self._reverse_deps.get(adg, set())  # type: ignore[union-attr]
            if adg_name.startswith(_MODULE_PREFIX)
        )

        layer = module_path_to_layer(parent_path) if parent_path else "L_UNKNOWN"
        territory = _infer_territory(parent_path, layer) if parent_path else "UNKNOWN"

        conf_notes: list[str] = []
        if not parent_path:
            conf_notes.append(f"Could not resolve parent module for {qualified_name}")

        return FileContext(
            target=qualified_name,
            target_type="symbol",
            layer=layer,
            territory=territory,
            nearest_trusted_neighbors=[],
            direct_importers=importers[:20],
            direct_imports=[],
            config_dependencies=[],
            likely_tests=[],
            structural_risks=[],
            confidence="MEDIUM" if parent_path else "LOW",
            confidence_notes=conf_notes,
        )


def _infer_territory(path: str, layer: str) -> str:
    """Infer territory label from path and layer."""
    if path.startswith("agentic_core/L0"):
        return "ROUTING"
    if path.startswith("agentic_core/L1"):
        return "COGNITION"
    if path.startswith("agentic_core/L2"):
        return "EXECUTION"
    if path.startswith("agentic_core/L3"):
        return "ORCHESTRATION"
    if path.startswith("agentic_core/L4"):
        return "STATE"
    if path.startswith("agentic_core/L5"):
        return "SAFETY"
    if path.startswith("agentic_core/L6"):
        return "OBSERVABILITY"
    if path.startswith("agentic_core/"):
        return "SHARED"
    if path.startswith("apps_rg"):
        return "APP_RG"
    if path.startswith("apps_lic"):
        return "APP_LIC"
    if path.startswith("apps_shared"):
        return "APP_SHARED"
    if path.startswith("tools"):
        return "TOOLS"
    if path.startswith("tests"):
        return "TESTS"
    if path.startswith("system_learning"):
        return "SYSTEM_LEARNING"
    if path.startswith("ops_scripts"):
        return "OPS"
    return layer


__all__ = [
    "PlacementAdvisor",
    "PlacementSuggestion",
    "FileContext",
]
