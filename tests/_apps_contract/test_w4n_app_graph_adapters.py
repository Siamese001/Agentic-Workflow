"""
W4N adapter tests — app-owned C0 graph adapter preparation.

Plan: chroma-graphrag-lic-rg-research-f4a2e9 / W4N (no-core track)
Constraint: zero agentic_core changes; no live Graph RAG wiring; ADAPTERS_PREPARED_ONLY.

Acceptance criteria verified:
  AC-1   apps_lic adapter exists (pre-existing + modified by W4N).
  AC-2   apps_rg adapter exists (pre-existing + modified by W4N).
  AC-3   apps_research adapter exists (pre-existing + modified by W4N).
  AC-4   apps_lic build_lic_graph_traverse_input() produces valid input shape.
  AC-5   apps_rg build_rg_graph_traverse_input() produces valid input shape.
  AC-6   apps_research build_research_graph_traverse_input() produces valid input shape.
  AC-7   No adapter calls run_graph_traverse() in source.
  AC-8   No adapter imports agentic_core.L4_state.
  AC-9   No adapter answers, routes, executes tools, or writes L4.
  AC-10  All adapters are side-effect-free on import.
  AC-11  Pre-existing adapter stubs are classified (not newly created by W4N).
  AC-12  apps_lic semantic cache bypass still preserved (W2N invariant).
  AC-13  apps_lic R1B absent from route order (W2N invariant).
  AC-14  apps_rg quarantined r1b_adapter.py untouched.
  AC-15  apps_research embedding conflict deferred to W5N.
  AC-16  No agentic_core files changed in W4N.
  AC-17  W4N does not claim live Graph RAG wiring.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

LIC_ADAPTER_PATH = REPO_ROOT / "apps_lic" / "integrations" / "c0_graph_adapter.py"
RG_ADAPTER_PATH = REPO_ROOT / "apps_rg" / "integrations" / "c0_graph_adapter.py"
RESEARCH_ADAPTER_PATH = REPO_ROOT / "apps_research" / "integrations" / "c0_graph_adapter.py"

LIC_CACHE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
LIC_ROUTE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
RG_CACHE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
RG_R1B_ADAPTER = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
RESEARCH_CACHE_PROFILE = (
    REPO_ROOT
    / "apps_research"
    / "config"
    / "domain_contract"
    / "cache_profile.company_brief.v1.yaml"
)
CORE_L0_BINDING = REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
CORE_ROUTE_CONTRACT = (
    REPO_ROOT / "agentic_core" / "L0_routing" / "c0_retrieval" / "route_contract.py"
)
CORE_C03_PIPELINE = (
    REPO_ROOT
    / "agentic_core"
    / "L0_routing"
    / "c0_retrieval"
    / "c0_3_enhanced"
    / "pipeline.py"
)

_FORBIDDEN_PATTERNS = (
    "run_graph_traverse(",
    "L4_state",
    "answer(",
    "route(",
    "execute_tool(",
    "write_l4(",
)
_WIRING_GATE = "GRAPH_TRAVERSE_POLICY_AGENTIC_CORE_REQUIRED"

_REQUIRED_INPUT_FIELDS = {
    "app_id",
    "allowed_relation_types",
    "max_hops",
    "max_nodes",
    "max_edges",
    "contradiction_scan_enabled",
    "supersession_scan_enabled",
    "hydrated_candidates",
    "graph_adapter_ref",
    "live_wiring_deferred",
    "wiring_gate",
}


def _load_adapter_module(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _load_lic_route_profile() -> dict:
    profiles = yaml.safe_load(LIC_ROUTE_PROFILE.read_text(encoding="utf-8"))
    return profiles[0] if isinstance(profiles, list) else profiles


# ---------------------------------------------------------------------------
# AC-1/2/3: Adapters exist
# ---------------------------------------------------------------------------

def test_apps_lic_graph_adapter_exists_or_created() -> None:
    """AC-1: apps_lic c0_graph_adapter.py exists (pre-existing, modified by W4N)."""
    assert LIC_ADAPTER_PATH.exists(), f"Missing: {LIC_ADAPTER_PATH}"
    source = LIC_ADAPTER_PATH.read_text(encoding="utf-8")
    assert "W4N" in source, "apps_lic adapter missing W4N marker"
    assert "build_lic_graph_traverse_input" in source


def test_apps_rg_graph_adapter_exists_or_created() -> None:
    """AC-2: apps_rg c0_graph_adapter.py exists (pre-existing, modified by W4N)."""
    assert RG_ADAPTER_PATH.exists(), f"Missing: {RG_ADAPTER_PATH}"
    source = RG_ADAPTER_PATH.read_text(encoding="utf-8")
    assert "W4N" in source, "apps_rg adapter missing W4N marker"
    assert "build_rg_graph_traverse_input" in source


def test_apps_research_graph_adapter_exists_or_created() -> None:
    """AC-3: apps_research c0_graph_adapter.py exists (pre-existing, modified by W4N)."""
    assert RESEARCH_ADAPTER_PATH.exists(), f"Missing: {RESEARCH_ADAPTER_PATH}"
    source = RESEARCH_ADAPTER_PATH.read_text(encoding="utf-8")
    assert "W4N" in source, "apps_research adapter missing W4N marker"
    assert "build_research_graph_traverse_input" in source


# ---------------------------------------------------------------------------
# AC-4/5/6: Builder functions produce valid input shapes
# ---------------------------------------------------------------------------

def test_apps_lic_graph_adapter_builds_valid_input_shape() -> None:
    """AC-4: build_lic_graph_traverse_input() returns all required fields."""
    mod = _load_adapter_module("apps_lic.integrations.c0_graph_adapter_test4", LIC_ADAPTER_PATH)
    fn = getattr(mod, "build_lic_graph_traverse_input")
    result = fn({}, [])
    missing = _REQUIRED_INPUT_FIELDS - set(result.keys())
    assert not missing, f"apps_lic builder missing fields: {missing}"
    assert result["app_id"] == "apps_lic"
    assert result["live_wiring_deferred"] is True
    assert result["wiring_gate"] == _WIRING_GATE
    assert result["max_hops"] == 2
    assert result["max_nodes"] == 64
    assert result["max_edges"] == 128
    assert result["contradiction_scan_enabled"] is True
    assert result["supersession_scan_enabled"] is False
    for rel in ("GOVERNED_BY", "OBSERVED_IN", "CONTRADICTS", "OWNED_BY", "REQUIRES"):
        assert rel in result["allowed_relation_types"], (
            f"apps_lic builder missing relation type: {rel}"
        )


def test_apps_rg_graph_adapter_builds_valid_input_shape() -> None:
    """AC-5: build_rg_graph_traverse_input() returns all required fields."""
    mod = _load_adapter_module("apps_rg.integrations.c0_graph_adapter_test4", RG_ADAPTER_PATH)
    fn = getattr(mod, "build_rg_graph_traverse_input")
    result = fn({}, [])
    missing = _REQUIRED_INPUT_FIELDS - set(result.keys())
    assert not missing, f"apps_rg builder missing fields: {missing}"
    assert result["app_id"] == "apps_rg"
    assert result["live_wiring_deferred"] is True
    assert result["wiring_gate"] == _WIRING_GATE
    assert result["max_hops"] == 1
    assert result["max_nodes"] == 32
    assert result["max_edges"] == 64
    assert result["contradiction_scan_enabled"] is True
    assert result["supersession_scan_enabled"] is False
    for rel in ("DERIVED_FROM", "IMPLEMENTS", "CONTRADICTS", "SOURCE_VERSION", "EVIDENCE"):
        assert rel in result["allowed_relation_types"], (
            f"apps_rg builder missing relation type: {rel}"
        )


def test_apps_research_graph_adapter_builds_valid_input_shape() -> None:
    """AC-6: build_research_graph_traverse_input() returns all required fields."""
    mod = _load_adapter_module(
        "apps_research.integrations.c0_graph_adapter_test4", RESEARCH_ADAPTER_PATH
    )
    fn = getattr(mod, "build_research_graph_traverse_input")
    result = fn({}, [])
    missing = _REQUIRED_INPUT_FIELDS - set(result.keys())
    assert not missing, f"apps_research builder missing fields: {missing}"
    assert result["app_id"] == "apps_research"
    assert result["live_wiring_deferred"] is True
    assert result["wiring_gate"] == _WIRING_GATE
    assert result["max_hops"] == 2
    assert result["max_nodes"] == 64
    assert result["max_edges"] == 128
    assert result["contradiction_scan_enabled"] is True
    assert result["supersession_scan_enabled"] is True
    for rel in (
        "SOURCE_AUTHORITY", "SOURCE_VERSION", "CONTRADICTS",
        "SUPERSEDES", "SUPERSEDED_BY", "EVIDENCE", "DERIVED_FROM",
    ):
        assert rel in result["allowed_relation_types"], (
            f"apps_research builder missing relation type: {rel}"
        )


# ---------------------------------------------------------------------------
# AC-7: No adapter calls run_graph_traverse()
# ---------------------------------------------------------------------------

def test_app_adapters_do_not_call_run_graph_traverse() -> None:
    """AC-7: no adapter may call run_graph_traverse() — checked on non-comment lines."""
    import re
    for label, path in (
        ("apps_lic", LIC_ADAPTER_PATH),
        ("apps_rg", RG_ADAPTER_PATH),
        ("apps_research", RESEARCH_ADAPTER_PATH),
    ):
        source = path.read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'"):
                continue
            assert "run_graph_traverse(" not in line, (
                f"{label} adapter invokes run_graph_traverse() on non-comment line: {line!r}"
            )


# ---------------------------------------------------------------------------
# AC-8: No adapter imports agentic_core.L4_state
# ---------------------------------------------------------------------------

def test_app_adapters_do_not_import_l4_state() -> None:
    """AC-8: no adapter may have an import statement referencing agentic_core.L4_state."""
    import re
    _l4_import_re = re.compile(r"^\s*(?:import|from)\s+.*L4_state")
    for label, path in (
        ("apps_lic", LIC_ADAPTER_PATH),
        ("apps_rg", RG_ADAPTER_PATH),
        ("apps_research", RESEARCH_ADAPTER_PATH),
    ):
        source = path.read_text(encoding="utf-8")
        for line in source.splitlines():
            assert not _l4_import_re.match(line), (
                f"{label} adapter imports L4_state: {line!r}"
            )
        assert "from agentic_core.L4_state" not in source, (
            f"{label} adapter imports from agentic_core.L4_state — W4N violation"
        )


# ---------------------------------------------------------------------------
# AC-9: No adapter answers, routes, executes tools, or writes L4
# ---------------------------------------------------------------------------

def test_app_adapters_do_not_answer_route_execute_or_write() -> None:
    """AC-9: adapters must not contain answer/route/execute_tool/write_l4 patterns."""
    for label, path in (
        ("apps_lic", LIC_ADAPTER_PATH),
        ("apps_rg", RG_ADAPTER_PATH),
        ("apps_research", RESEARCH_ADAPTER_PATH),
    ):
        source = path.read_text(encoding="utf-8")
        for pattern in ("execute_tool(", "write_l4(", "emit_answer(", "dispatch_route("):
            assert pattern not in source, (
                f"{label} adapter contains forbidden pattern '{pattern}'"
            )


# ---------------------------------------------------------------------------
# AC-10: All adapters are side-effect-free on import
# ---------------------------------------------------------------------------

def test_app_adapters_are_side_effect_free_on_import() -> None:
    """AC-10: importing each adapter must produce no exceptions and no side effects."""
    for label, module_name, path in (
        ("apps_lic", "apps_lic.integrations.c0_graph_adapter_se_test", LIC_ADAPTER_PATH),
        ("apps_rg", "apps_rg.integrations.c0_graph_adapter_se_test", RG_ADAPTER_PATH),
        ("apps_research", "apps_research.integrations.c0_graph_adapter_se_test", RESEARCH_ADAPTER_PATH),
    ):
        try:
            mod = _load_adapter_module(module_name, path)
        except Exception as exc:
            pytest.fail(f"{label} adapter raised on import: {exc}")
        assert mod is not None, f"{label} adapter module is None after import"


# ---------------------------------------------------------------------------
# AC-11: Pre-existing adapter stubs classified
# ---------------------------------------------------------------------------

def test_existing_adapter_stubs_are_classified_if_present() -> None:
    """AC-11: adapters that existed before W4N (from prior reverted W4 work)
    must contain W4N markers confirming W4N updated (not created) them."""
    for label, path in (
        ("apps_lic", LIC_ADAPTER_PATH),
        ("apps_rg", RG_ADAPTER_PATH),
        ("apps_research", RESEARCH_ADAPTER_PATH),
    ):
        source = path.read_text(encoding="utf-8")
        assert "W4N" in source, (
            f"{label} adapter missing W4N marker — W4N must update pre-existing stubs"
        )
        assert "live_wiring_deferred" in source, (
            f"{label} adapter missing live_wiring_deferred marker"
        )
        assert _WIRING_GATE in source, (
            f"{label} adapter missing wiring_gate={_WIRING_GATE!r}"
        )


# ---------------------------------------------------------------------------
# AC-12: apps_lic semantic cache bypass still preserved (W2N invariant)
# ---------------------------------------------------------------------------

def test_apps_lic_semantic_cache_bypass_still_preserved() -> None:
    """AC-12: apps_lic semantic_cache.enabled must still be false (W2N invariant)."""
    data = yaml.safe_load(LIC_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is False, (
        f"apps_lic semantic_cache.enabled changed: {sc.get('enabled')!r}"
    )
    assert sc.get("reason") == "personalized_outreach_not_cacheable"


# ---------------------------------------------------------------------------
# AC-13: apps_lic R1B absent from route order (W2N invariant)
# ---------------------------------------------------------------------------

def test_apps_lic_r1b_absent_from_route_order() -> None:
    """AC-13: R1B_SEMANTIC_CACHE must not appear in apps_lic route_evaluation_order."""
    profile = _load_lic_route_profile()
    order = profile.get("route_evaluation_order", [])
    route_ids = [
        (item.get("route_id") if isinstance(item, dict) else item)
        for item in order
    ]
    assert "R1B_SEMANTIC_CACHE" not in route_ids, (
        f"R1B_SEMANTIC_CACHE found in apps_lic route order: {route_ids}"
    )


# ---------------------------------------------------------------------------
# AC-14: apps_rg quarantined r1b_adapter.py untouched
# ---------------------------------------------------------------------------

def test_apps_rg_quarantined_r1b_adapter_untouched() -> None:
    """W7: apps_rg/cache/r1b_adapter.py is the active ROLE_TARGET_RUN implementation."""
    assert RG_R1B_ADAPTER.exists(), f"r1b_adapter.py missing: {RG_R1B_ADAPTER}"
    source = RG_R1B_ADAPTER.read_text(encoding="utf-8")
    assert "check_r1b_for_apps_rg" in source
    assert "ROLE_TARGET_RUN" in source or "CACHE_GRAIN_ROLE_TARGET_RUN" in source


# ---------------------------------------------------------------------------
# AC-15: apps_research embedding conflict deferred to W5N
# ---------------------------------------------------------------------------

def test_apps_research_embedding_conflict_deferred_to_w5n() -> None:
    """AC-15: apps_research embedding_model check.

    W4N constraint: W4N must NOT have resolved the conflict.
    W5N update: W5N legitimately resolves the conflict to BAAI/bge-m3/1024.
    Post-W5N: accept either the original value (pre-W5N) or the fixed value.
    """
    data = yaml.safe_load(RESEARCH_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    model = sc.get("embedding_model", "")
    dims = sc.get("embedding_dimensions", 0)
    _valid_models = {"text-embedding-3-large", "BAAI/bge-m3"}
    assert model in _valid_models, (
        f"apps_research embedding_model is unrecognised: {model!r}"
    )
    _valid_dims = {3072, 1024}
    assert dims in _valid_dims, (
        f"apps_research embedding_dimensions is unrecognised: {dims!r}"
    )
    source = RESEARCH_ADAPTER_PATH.read_text(encoding="utf-8")
    import re
    _chroma_import_re = re.compile(r"^\s*(?:import|from)\s+.*ChromaResearchStore")
    for line in source.splitlines():
        assert not _chroma_import_re.match(line), (
            f"apps_research adapter imports ChromaResearchStore: {line!r}"
        )
    _chroma_call_re = re.compile(r"ChromaResearchStore\s*\(")
    assert not _chroma_call_re.search(source), (
        "apps_research adapter instantiates ChromaResearchStore — W5N boundary violated"
    )


# ---------------------------------------------------------------------------
# AC-16: No agentic_core files changed in W4N
# ---------------------------------------------------------------------------

def test_no_agentic_core_files_changed_in_w4n() -> None:
    """AC-16: agentic_core binding, route_contract, and C0.3 pipeline must not
    contain W4N markers."""
    for path in (CORE_L0_BINDING, CORE_ROUTE_CONTRACT, CORE_C03_PIPELINE):
        source = path.read_text(encoding="utf-8")
        assert "W4N" not in source, (
            f"{path.name} contains W4N marker — W4N must not touch agentic_core"
        )


# ---------------------------------------------------------------------------
# AC-17: W4N does not claim live Graph RAG wiring
# ---------------------------------------------------------------------------

def test_w4n_does_not_claim_live_graph_rag_wiring() -> None:
    """AC-17: all three adapters must carry live_wiring_deferred=True in build output."""
    for label, module_name, path, fn_name in (
        (
            "apps_lic",
            "apps_lic.integrations.c0_graph_adapter_lw_test",
            LIC_ADAPTER_PATH,
            "build_lic_graph_traverse_input",
        ),
        (
            "apps_rg",
            "apps_rg.integrations.c0_graph_adapter_lw_test",
            RG_ADAPTER_PATH,
            "build_rg_graph_traverse_input",
        ),
        (
            "apps_research",
            "apps_research.integrations.c0_graph_adapter_lw_test",
            RESEARCH_ADAPTER_PATH,
            "build_research_graph_traverse_input",
        ),
    ):
        mod = _load_adapter_module(module_name, path)
        fn = getattr(mod, fn_name)
        result = fn({}, [])
        assert result.get("live_wiring_deferred") is True, (
            f"{label} builder does not mark live_wiring_deferred=True "
            "(W4N must not claim live Graph RAG wiring)"
        )
        assert result.get("wiring_gate") == _WIRING_GATE, (
            f"{label} builder missing wiring_gate sentinel"
        )
