"""ADG schema: entity types, relation types, edge kinds, and naming conventions.

All ADG entities use the ADG:: namespace prefix to avoid collisions with other
Memory MCP uses.

Naming convention:
    ADG::Module::<forward/slash/path>
    ADG::Symbol::<qualified.symbol.name>
    ADG::Layer::L0 ... ADG::Layer::L6
    ADG::Commit::<40-hex-sha>
    ADG::Snapshot::<40-hex-sha>::<digest>
    ADG::Gateway::<ClassName>
    ADG::Policy::<POLICY_ID>
    ADG::Decision::<DecisionName>
    ADG::Retrieval::<ComponentName>
    ADG::Run::<run_id>
"""

from __future__ import annotations

from typing import Literal

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ADG_NS = "ADG"

EntityType = Literal[
    "module",
    "symbol",
    "layer",
    "agent",
    "tool",
    "gateway",
    "provider",
    "datastore",
    "side_effect_endpoint",
    "retrieval_component",
    "decision_point",
    "policy",
    "commit",
    "snapshot",
    "scan_run",
]

RelationType = Literal[
    "imports",
    "calls",
    "belongs_to_layer",
    "implements",
    "routes_through",
    "writes_through",
    "reads_from",
    "writes_to",
    "invokes_provider",
    "instantiates",
    "produces",
    "consumes",
    "influences",
    "bypasses",
    "violates",
    "allows",
]

EdgeKind = Literal[
    "import",
    "call",
    "write",
    "network",
    "embedding",
    "retrieval",
    "decision",
]


def canonical_name(entity_type: str, *parts: str) -> str:
    """Build a canonical ADG entity name.

    Examples:
        canonical_name("Module", "agentic_core/L0_routing/engines/path_router.py")
        canonical_name("Layer", "L0")
        canonical_name("Commit", "abcdef1234567890abcdef1234567890abcdef12")
        canonical_name("Snapshot", sha, digest)
    """
    safe_parts = [p.replace("\\", "/") for p in parts]
    return "::".join([ADG_NS, entity_type] + safe_parts)


LAYER_PREFIXES: dict[str, str] = {
    "agentic_core/L0_routing": "L0",
    "agentic_core/L1_cognition": "L1",
    "agentic_core/L2_execution": "L2",
    "agentic_core/L3_orchestration": "L3",
    "agentic_core/L4_state": "L4",
    "agentic_core/L5_safety": "L5",
    "agentic_core/L6_observability": "L6",
    # H2: previously L_UNKNOWN subdirs now mapped to named labels
    "agentic_core/base_agents": "L_SHARED",
    "agentic_core/interfaces": "L_SHARED",
    "agentic_core/config": "L_SHARED",
    "agentic_core/mixins": "L_SHARED",
    "agentic_core/utils": "L_SHARED",
    "agentic_core/seams": "L_SHARED",
    "agentic_core/cache": "L_SHARED",
    "agentic_core/agents": "L_SHARED",
    "agentic_core/evaluation": "L_SHARED",
    "agentic_core/runtime": "L_RUNTIME",
    "agentic_core/prompt_governance": "L_PG",
    "agentic_core/knowledge": "L_PG",
    "agentic_core/adg": "L_TOOLS",
    # App and infra layers
    "apps_rg": "L_APP",
    "apps_lic": "L_APP",
    "apps_shared": "L_APP",
    "system_learning": "L_SL",
    "tools": "L_TOOLS",
    "ops_scripts": "L_OPS",
    "tests": "L_TEST",
}

ALLOWED_LAYER_EDGES: frozenset[tuple[str, str]] = frozenset(
    {
        # Core downward edges
        ("L6", "L5"),
        ("L6", "L4"),
        ("L6", "L3"),
        ("L6", "L2"),
        ("L6", "L1"),
        ("L6", "L0"),
        ("L5", "L4"),
        ("L5", "L3"),
        ("L5", "L2"),
        ("L5", "L1"),
        ("L5", "L0"),
        ("L4", "L3"),
        ("L4", "L2"),
        ("L4", "L1"),
        ("L4", "L0"),
        ("L3", "L2"),
        ("L3", "L1"),
        ("L3", "L0"),
        ("L2", "L1"),
        ("L2", "L0"),
        ("L1", "L0"),
        # App layer
        ("L_APP", "L6"),
        ("L_APP", "L5"),
        ("L_APP", "L4"),
        ("L_APP", "L3"),
        ("L_APP", "L2"),
        ("L_APP", "L1"),
        ("L_APP", "L0"),
        # System learning
        ("L_SL", "L2"),
        ("L_SL", "L1"),
        ("L_SL", "L0"),
        # Tools
        ("L_TOOLS", "L5"),
        ("L_TOOLS", "L4"),
        ("L_TOOLS", "L3"),
        ("L_TOOLS", "L2"),
        ("L_TOOLS", "L1"),
        ("L_TOOLS", "L0"),
        # Ops
        ("L_OPS", "L5"),
        ("L_OPS", "L4"),
        ("L_OPS", "L3"),
        ("L_OPS", "L2"),
        ("L_OPS", "L1"),
        ("L_OPS", "L0"),
        # H2: L_SHARED importable from all named layers (it's a shared utility layer)
        ("L0", "L_SHARED"),
        ("L1", "L_SHARED"),
        ("L2", "L_SHARED"),
        ("L3", "L_SHARED"),
        ("L4", "L_SHARED"),
        ("L5", "L_SHARED"),
        ("L6", "L_SHARED"),
        ("L_APP", "L_SHARED"),
        ("L_SL", "L_SHARED"),
        ("L_TOOLS", "L_SHARED"),
        ("L_OPS", "L_SHARED"),
        ("L_RUNTIME", "L_SHARED"),
        ("L_PG", "L_SHARED"),
        ("L_TEST", "L_SHARED"),
        # H2: L_RUNTIME importable from L3+
        ("L3", "L_RUNTIME"),
        ("L4", "L_RUNTIME"),
        ("L5", "L_RUNTIME"),
        ("L6", "L_RUNTIME"),
        ("L_APP", "L_RUNTIME"),
        # H2: L_PG importable from L1+
        ("L1", "L_PG"),
        ("L2", "L_PG"),
        ("L3", "L_PG"),
        ("L4", "L_PG"),
        ("L5", "L_PG"),
        ("L6", "L_PG"),
        ("L_APP", "L_PG"),
        # L_TEST can import anything (test files are unrestricted consumers)
        ("L_TEST", "L0"),
        ("L_TEST", "L1"),
        ("L_TEST", "L2"),
        ("L_TEST", "L3"),
        ("L_TEST", "L4"),
        ("L_TEST", "L5"),
        ("L_TEST", "L6"),
        ("L_TEST", "L_APP"),
        ("L_TEST", "L_SL"),
        ("L_TEST", "L_TOOLS"),
        ("L_TEST", "L_OPS"),
        ("L_TEST", "L_RUNTIME"),
        ("L_TEST", "L_PG"),
        # L_TOOLS can import L_SHARED
        ("L_TOOLS", "L_SHARED"),
        # L_OPS can import L_SHARED + L_TOOLS
        ("L_OPS", "L_SHARED"),
        ("L_OPS", "L_TOOLS"),
        # L_SHARED internal cross-imports allowed
        ("L_SHARED", "L_SHARED"),
        # L_RUNTIME can import L0-L2
        ("L_RUNTIME", "L0"),
        ("L_RUNTIME", "L1"),
        ("L_RUNTIME", "L2"),
        # L_PG can import L0-L1
        ("L_PG", "L0"),
        ("L_PG", "L1"),
    }
)


def verify_layer_graph_consistency(module_layer_map: dict[str, str]) -> list[str]:
    """S4: Verify every module has exactly one layer label (no L_UNKNOWN remaining).

    Returns list of error strings; empty list means consistent.
    """
    errors: list[str] = []
    for module, layer in sorted(module_layer_map.items()):
        if layer == "L_UNKNOWN":
            errors.append(f"L_UNKNOWN module (unmapped): {module}")
    return errors


def module_path_to_layer(rel_path: str) -> str:
    """Map a repo-relative module path (forward slashes) to a layer label."""
    norm = rel_path.replace("\\", "/")
    for prefix, layer in sorted(LAYER_PREFIXES.items(), key=lambda kv: -len(kv[0])):
        if norm.startswith(prefix):
            return layer
    return "L_UNKNOWN"


GATEWAY_ALLOWLIST: dict[str, str] = {
    "SovereignLLMGateway": "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "UniversalWriteGateway": "agentic_core/L2_execution/UniversalWriteGateway.py",
    "EmbeddingSovereignAgent": "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
}

PROVIDER_SDK_SYMBOLS: frozenset[str] = frozenset(
    {
        "openai",
        "anthropic",
        "google.generativeai",
        "google.cloud.aiplatform",
        "vertexai",
        "requests",
        "httpx",
        "aiohttp",
        "boto3",
        "botocore",
    }
)

EMBEDDING_SYMBOLS: frozenset[str] = frozenset(
    {
        "OpenAIEmbeddings",
        "VertexAIEmbeddings",
        "GoogleGenerativeAIEmbeddings",
        "HuggingFaceEmbeddings",
        "FakeEmbeddings",
        "SentenceTransformerEmbeddings",
        "EmbeddingSovereignAgent",
        "bmg_embed_text",
        "create_vertex_client",
    }
)

WRITE_SIDE_EFFECT_SYMBOLS: frozenset[str] = frozenset(
    {
        "open",
        "write",
        "os.remove",
        "os.rename",
        "os.makedirs",
        "os.mkdir",
        "shutil.copy",
        "shutil.move",
        "shutil.rmtree",
        "pathlib.Path.write_text",
        "pathlib.Path.write_bytes",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
    }
)

NETWORK_SYMBOLS: frozenset[str] = frozenset(
    {
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "requests.head",
        "requests.options",
        "httpx.get",
        "httpx.post",
        "httpx.Client",
        "httpx.AsyncClient",
        "aiohttp.ClientSession",
        "urllib.request.urlopen",
        "urllib.request.urlretrieve",
    }
)


__all__ = [
    "ADG_NS",
    "EntityType",
    "RelationType",
    "EdgeKind",
    "canonical_name",
    "module_path_to_layer",
    "verify_layer_graph_consistency",
    "LAYER_PREFIXES",
    "ALLOWED_LAYER_EDGES",
    "GATEWAY_ALLOWLIST",
    "PROVIDER_SDK_SYMBOLS",
    "EMBEDDING_SYMBOLS",
    "WRITE_SIDE_EFFECT_SYMBOLS",
    "NETWORK_SYMBOLS",
]
