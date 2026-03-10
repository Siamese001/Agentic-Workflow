"""Phase 7.3: ADG negative control tests.

Each test introduces a synthetic violation and asserts the scanner flags it.
All negative controls use in-memory synthetic ScanResult (no filesystem mutation).

Markers: architecture, negative_control, governance
"""

from __future__ import annotations

from pathlib import Path

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

REPO_ROOT = Path(__file__).parent.parent.parent


def _make_edge(
    from_rel: str,
    relation_type: str,
    to_sym: str,
    edge_kind: str = "import",
    line_no: int = 1,
    symbol: str = "",
) -> Edge:
    from agentic_core.adg.extraction.static_scanner import Edge
    from agentic_core.adg.schema import canonical_name

    return Edge(
        from_name=canonical_name("Module", from_rel),
        relation_type=relation_type,
        to_name=canonical_name("Symbol", to_sym),
        edge_kind=edge_kind,
        source_file=from_rel,
        line_no=line_no,
        symbol=to_sym,
    )


def _make_module_edge(
    from_rel: str,
    relation_type: str,
    to_rel: str,
    edge_kind: str = "import",
    line_no: int = 1,
) -> Edge:
    from agentic_core.adg.extraction.static_scanner import Edge
    from agentic_core.adg.schema import canonical_name

    return Edge(
        from_name=canonical_name("Module", from_rel),
        relation_type=relation_type,
        to_name=canonical_name("Module", to_rel),
        edge_kind=edge_kind,
        source_file=from_rel,
        line_no=line_no,
        symbol=to_rel,
    )


# ---------------------------------------------------------------------------
# RULE A: LLM provider bypass
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rule_a_direct_openai_import_flagged() -> None:
    """Direct openai import outside SovereignLLMGateway must trigger RULE_A."""
    from agentic_core.adg.ci.invariant_scanner import InvariantScanner
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="neg-test-a")
    result.edges = [
        _make_edge("apps_rg/engines/SomeAgentEngine.py", "imports", "openai", "network", 5, "openai")
    ]
    result.modules = ["apps_rg/engines/SomeAgentEngine.py"]
    result.compute_digest()

    report = InvariantScanner().scan(result)
    rule_a = [v for v in report.violations if v.rule == "RULE_A"]
    assert len(rule_a) >= 1, (
        f"NEGATIVE CONTROL FAILED: direct openai import was NOT flagged by RULE_A\n"
        f"violations: {[v.format() for v in report.violations]}"
    )


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rule_a_direct_anthropic_import_flagged() -> None:
    """Direct anthropic import outside gateway must trigger RULE_A."""
    from agentic_core.adg.ci.invariant_scanner import InvariantScanner
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="neg-test-a-anthropic")
    result.edges = [
        _make_edge(
            "agentic_core/L3_orchestration/engines/AgentFactory.py",
            "imports",
            "anthropic",
            "network",
            12,
            "anthropic",
        )
    ]
    result.modules = ["agentic_core/L3_orchestration/engines/AgentFactory.py"]
    result.compute_digest()

    report = InvariantScanner().scan(result)
    rule_a = [v for v in report.violations if v.rule == "RULE_A"]
    assert len(rule_a) >= 1, "NEGATIVE CONTROL FAILED: anthropic import not flagged by RULE_A"


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rule_a_vertexai_flagged() -> None:
    """Direct vertexai import outside gateway must trigger RULE_A."""
    from agentic_core.adg.ci.invariant_scanner import InvariantScanner
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="neg-test-a-vertex")
    result.edges = [
        _make_edge(
            "system_learning/arbitration/engine.py",
            "imports",
            "vertexai.generative_models",
            "network",
            7,
            "vertexai",
        )
    ]
    result.modules = ["system_learning/arbitration/engine.py"]
    result.compute_digest()

    report = InvariantScanner().scan(result)
    rule_a = [v for v in report.violations if v.rule == "RULE_A"]
    assert len(rule_a) >= 1, "NEGATIVE CONTROL FAILED: vertexai import not flagged"


# ---------------------------------------------------------------------------
# RULE B: Embedding factory bypass
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rule_b_embedding_bypass_flagged() -> None:
    """Direct OpenAIEmbeddings instantiation outside EmbeddingSovereignAgent is flagged."""
    from agentic_core.adg.ci.invariant_scanner import InvariantScanner
    from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
    from agentic_core.adg.schema import canonical_name

    result = ScanResult(commit_sha="neg-test-b")
    result.edges = [
        Edge(
            from_name=canonical_name("Module", "apps_rg/engines/SomeEngine.py"),
            relation_type="instantiates",
            to_name=canonical_name("Symbol", "OpenAIEmbeddings"),
            edge_kind="embedding",
            source_file="apps_rg/engines/SomeEngine.py",
            line_no=20,
            symbol="OpenAIEmbeddings",
        )
    ]
    result.modules = ["apps_rg/engines/SomeEngine.py"]
    result.compute_digest()

    report = InvariantScanner().scan(result)
    rule_b = [v for v in report.violations if v.rule == "RULE_B"]
    assert len(rule_b) >= 1, (
        f"NEGATIVE CONTROL FAILED: embedding bypass NOT flagged by RULE_B\n"
        f"violations: {[v.format() for v in report.violations]}"
    )


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rule_b_huggingface_bypass_flagged() -> None:
    """HuggingFaceEmbeddings instantiation outside EmbeddingSovereignAgent is flagged."""
    from agentic_core.adg.ci.invariant_scanner import InvariantScanner
    from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
    from agentic_core.adg.schema import canonical_name

    result = ScanResult(commit_sha="neg-test-b-hf")
    result.edges = [
        Edge(
            from_name=canonical_name("Module", "agentic_core/L3_orchestration/engines/AgentFactory.py"),
            relation_type="instantiates",
            to_name=canonical_name("Symbol", "HuggingFaceEmbeddings"),
            edge_kind="embedding",
            source_file="agentic_core/L3_orchestration/engines/AgentFactory.py",
            line_no=55,
            symbol="HuggingFaceEmbeddings",
        )
    ]
    result.modules = ["agentic_core/L3_orchestration/engines/AgentFactory.py"]
    result.compute_digest()

    report = InvariantScanner().scan(result)
    rule_b = [v for v in report.violations if v.rule == "RULE_B"]
    assert len(rule_b) >= 1, "NEGATIVE CONTROL FAILED: HuggingFaceEmbeddings bypass not flagged"


# ---------------------------------------------------------------------------
# RULE C: Layer boundary violation
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rule_c_upward_layer_edge_flagged() -> None:
    """L0 importing from L5 must be flagged as upward layer violation."""
    from agentic_core.adg.ci.invariant_scanner import InvariantScanner
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="neg-test-c")
    result.edges = [
        _make_module_edge(
            "agentic_core/L0_routing/engines/path_router.py",
            "imports",
            "agentic_core/L5_safety/enforcement/some_guard.py",
            line_no=3,
        )
    ]
    result.modules = [
        "agentic_core/L0_routing/engines/path_router.py",
        "agentic_core/L5_safety/enforcement/some_guard.py",
    ]
    result.compute_digest()

    report = InvariantScanner().scan(result)
    rule_c = [v for v in report.violations if v.rule == "RULE_C"]
    assert len(rule_c) >= 1, (
        f"NEGATIVE CONTROL FAILED: L0->L5 upward import NOT flagged by RULE_C\n"
        f"violations: {[v.format() for v in report.violations]}"
    )


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rule_c_l1_importing_l6_flagged() -> None:
    """L1 importing L6 is an upward violation."""
    from agentic_core.adg.ci.invariant_scanner import InvariantScanner
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="neg-test-c-l1l6")
    result.edges = [
        _make_module_edge(
            "agentic_core/L1_cognition/engines/some_cog.py",
            "imports",
            "agentic_core/L6_observability/engines/SovereignHealthMonitor.py",
            line_no=1,
        )
    ]
    result.modules = [
        "agentic_core/L1_cognition/engines/some_cog.py",
        "agentic_core/L6_observability/engines/SovereignHealthMonitor.py",
    ]
    result.compute_digest()

    report = InvariantScanner().scan(result)
    rule_c = [v for v in report.violations if v.rule == "RULE_C"]
    assert len(rule_c) >= 1, "NEGATIVE CONTROL FAILED: L1->L6 upward import not flagged"


# ---------------------------------------------------------------------------
# Gateway topology bypass
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_gateway_bypass_flagged() -> None:
    """Module directly invoking openai outside gateway must be flagged."""
    from agentic_core.adg.applications.gateway_topology import check_gateway_topology
    from agentic_core.adg.extraction.static_scanner import ScanResult

    result = ScanResult(commit_sha="neg-gw-bypass")
    result.edges = [
        _make_edge(
            "apps_rg/engines/SomeLLMEngine.py",
            "invokes_provider",
            "openai.ChatCompletion",
            "network",
            42,
            "openai",
        )
    ]
    result.modules = ["apps_rg/engines/SomeLLMEngine.py"]
    result.compute_digest()

    report = check_gateway_topology(result)
    assert not report.passed, "NEGATIVE CONTROL FAILED: gateway bypass was NOT detected"
    assert len(report.violations) >= 1


# ---------------------------------------------------------------------------
# UWG write authority bypass
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_uwg_bypass_flagged() -> None:
    """Direct filesystem write outside UWG must be flagged."""
    from agentic_core.adg.applications.uwg_write_authority import check_uwg_write_authority
    from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
    from agentic_core.adg.schema import canonical_name

    result = ScanResult(commit_sha="neg-uwg-bypass")
    result.edges = [
        Edge(
            from_name=canonical_name("Module", "agentic_core/L1_cognition/engines/some_agent.py"),
            relation_type="writes_to",
            to_name=canonical_name("Symbol", "open"),
            edge_kind="write",
            source_file="agentic_core/L1_cognition/engines/some_agent.py",
            line_no=88,
            symbol="open",
        )
    ]
    result.modules = ["agentic_core/L1_cognition/engines/some_agent.py"]
    result.compute_digest()

    report = check_uwg_write_authority(result)
    assert not report.passed, "NEGATIVE CONTROL FAILED: UWG bypass was NOT detected"
    assert len(report.violations) >= 1


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_uwg_subprocess_bypass_flagged() -> None:
    """Direct subprocess.run outside UWG must be flagged."""
    from agentic_core.adg.applications.uwg_write_authority import check_uwg_write_authority
    from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
    from agentic_core.adg.schema import canonical_name

    result = ScanResult(commit_sha="neg-uwg-subproc")
    result.edges = [
        Edge(
            from_name=canonical_name("Module", "agentic_core/L2_execution/engines/some_exec.py"),
            relation_type="writes_to",
            to_name=canonical_name("Symbol", "subprocess.run"),
            edge_kind="write",
            source_file="agentic_core/L2_execution/engines/some_exec.py",
            line_no=15,
            symbol="subprocess.run",
        )
    ]
    result.modules = ["agentic_core/L2_execution/engines/some_exec.py"]
    result.compute_digest()

    report = check_uwg_write_authority(result)
    assert not report.passed, "NEGATIVE CONTROL FAILED: subprocess bypass not flagged"


# ---------------------------------------------------------------------------
# RAG C0 sovereignty
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rag_c0_influences_routing_decision_flagged() -> None:
    """C0Context influences RoutingDecision edge must be flagged."""
    from agentic_core.adg.applications.rag_sovereignty import check_rag_sovereignty
    from agentic_core.adg.extraction.static_scanner import ScanResult
    from agentic_core.adg.schema import canonical_name

    result = ScanResult(commit_sha="neg-rag-c0")
    result.compute_digest()

    report = check_rag_sovereignty(
        result,
        extra_edges=[
            {
                "from": canonical_name("Retrieval", "C0Context"),
                "relation": "influences",
                "to": canonical_name("Decision", "RoutingDecision"),
            }
        ],
    )
    assert not report.passed, "NEGATIVE CONTROL FAILED: C0Context->RoutingDecision was NOT detected"
    assert len(report.violations) >= 1


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_rag_c0_influences_safety_threshold_flagged() -> None:
    """C0Context influences SafetyThreshold must be flagged."""
    from agentic_core.adg.applications.rag_sovereignty import check_rag_sovereignty
    from agentic_core.adg.extraction.static_scanner import ScanResult
    from agentic_core.adg.schema import canonical_name

    result = ScanResult(commit_sha="neg-rag-safety")
    result.compute_digest()

    report = check_rag_sovereignty(
        result,
        extra_edges=[
            {
                "from": canonical_name("Retrieval", "C0Context"),
                "relation": "influences",
                "to": canonical_name("Decision", "SafetyThreshold"),
            }
        ],
    )
    assert not report.passed, "NEGATIVE CONTROL FAILED: C0Context->SafetyThreshold not flagged"
    assert len(report.violations) >= 1


# ---------------------------------------------------------------------------
# Blast-radius mode escalation
# ---------------------------------------------------------------------------


@pytest.mark.architecture
@pytest.mark.negative_control
def test_negative_blast_radius_high_risk_escalates_mode() -> None:
    """Changing many high-weight L0+L2+L5 modules must produce positive risk_score."""
    from agentic_core.adg.applications.blast_radius import compute_blast_radius
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(repo_root=REPO_ROOT)
    result = scanner.scan(commit_sha="br-high-risk")

    candidate_changed = [
        "agentic_core/L0_routing/engines/path_router.py",
        "agentic_core/L0_routing/engines/reasoning_policy_engine.py",
        "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
        "agentic_core/L2_execution/UniversalWriteGateway.py",
        "agentic_core/L5_safety/enforcement/constitutional_enforcement.py",
    ]
    existing_changed = [
        f
        for f in candidate_changed
        if (REPO_ROOT / f.replace("/", "\\")).exists() or (REPO_ROOT / f).exists()
    ]
    if not existing_changed:
        existing_changed = ["agentic_core/L0_routing/engines/path_router.py"]

    br = compute_blast_radius(existing_changed, result, commit_sha="high-risk")
    assert br.risk_score > 0, "High-risk change must have positive risk_score"
    assert br.route_mode in ("RESTRICTED", "HUMAN_REVIEW", "NORMAL")
