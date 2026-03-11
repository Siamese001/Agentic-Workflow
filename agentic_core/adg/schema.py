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
    ADG::Cycle::<hash_of_members>
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
    # P6: Prompt governance
    "prompt_slot",
    "prompt_template",
    "prompt_assembly",
    # P7: Observability
    "execution_trace",
    # P3: Runtime graph
    "agent_action",
    "tool_invocation",
    "layer_transition",
    "mutation_record",
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
    "covers",
    "exports",
    "re_exports",
    "in_cycle",
    "dead_imports",
    # P6: Prompt governance
    "generates_prompt",
    "consumes_prompt",
    "assembles_into",
    "injects_into",
    "overrides_prompt",
    # P7: Observability
    "executed_with_prompt",
    "triggered_telemetry",
    "proposed_improvement",
    "updated_prompt",
    # P3: Runtime graph / authority / mutation
    "executes_action",
    "invokes_tool",
    "crosses_layer",
    "bypasses_uwg",
    "routes_through_uwg",
    "layer_authority_violation",
    "policy_hash_mismatch",
    "lineage_of",
]

EdgeKind = Literal[
    "import",
    "call",
    "write",
    "network",
    "embedding",
    "retrieval",
    "decision",
    "dead_import",
    "star_import",
    "cycle",
    "export",
    "re_export",
    "decorator",
    "type_checking_import",
    "optional_import",
    "version_guard_import",
    "type_annotation",
    # P6: Prompt governance
    "prompt_generation",
    "prompt_consumption",
    "prompt_assembly",
    "prompt_injection",
    "prompt_authority_violation",
    # P7: Observability
    "trace_prompt_link",
    "prompt_drift",
    # P3: Runtime graph / authority / mutation
    "agent_execution",
    "tool_call",
    "layer_boundary_cross",
    "uwg_bypass",
    "uwg_compliant_write",
    "authority_violation",
    "policy_validation",
    "state_lineage",
]


# P6: Prompt slot authority ordering (S0 highest authority → U0 lowest)
PROMPT_SLOT_TYPES: tuple[str, ...] = ("S0", "D0", "I0", "C0", "U0")
PROMPT_SLOT_AUTHORITY: dict[str, int] = {slot: i for i, slot in enumerate(PROMPT_SLOT_TYPES)}

# P6: Authority hierarchy — high-authority slots that low-authority slots must not override
PROMPT_AUTHORITY_RULES: tuple[tuple[str, str], ...] = (
    ("U0", "S0"),  # user must not mutate system
    ("U0", "D0"),  # user must not mutate injection fences
    ("U0", "I0"),  # user must not mutate instructional
    ("C0", "S0"),  # context must not mutate system
    ("C0", "D0"),  # context must not introduce injection fences
    ("I0", "S0"),  # instructional must not mutate system
)

# P6: Prompt slot field names in GovernedPayload → slot type mapping
PROMPT_FIELD_TO_SLOT: dict[str, str] = {
    "s0_system": "S0",
    "d0_injections": "D0",
    "i0_instructional": "I0",
    "c0_context": "C0",
    "u0_user_prompt": "U0",
}

# P3: UWG canonical symbol — all writes_through must target this
UWG_CANONICAL_SYMBOL: str = "ADG::Symbol::UniversalWriteGateway"
UWG_MODULE_PATH: str = "agentic_core/L2_execution/UniversalWriteGateway.py"
UWG_INTERFACE_PATH: str = "agentic_core/interfaces/write_gateway.py"

# P3: Layer authority rules — which relations are FORBIDDEN per layer
# Format: layer_prefix → frozenset of forbidden relation_types
LAYER_AUTHORITY_FORBIDDEN: dict[str, frozenset[str]] = {
    "L1": frozenset({"writes_to", "writes_through"}),  # L1 must not mutate state
    "L3": frozenset({"invokes_tool", "invokes_provider"}),  # L3 must not directly invoke tools
    "L4": frozenset({"calls", "invokes_provider"}),  # L4 must not contain business logic
    "L6": frozenset({"writes_to", "writes_through", "routes_through"}),  # L6 must not alter execution
}

# P3: L1 write symbols that are allowlisted (self-copies, not persistent mutations)
L1_WRITE_ALLOWLIST: frozenset[str] = frozenset(
    {
        "copy",
        "output.copy",
        "self.strategy_weights.copy",
        "copy.deepcopy",
        "self.guardrails._cache_sizes.copy",
        "visited.copy",
    }
)

# P3: UWG write symbols (compliant write targets)
UWG_WRITE_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "uwg.write",
        "uwg.write_bytes",
        "write_gateway.write_text",
        "write_gateway.write_bytes",
    }
)


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

SYMBOL_KINDS: frozenset[str] = frozenset(
    {
        "function",
        "async_function",
        "class",
        "constant",
        "type_alias",
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
    "SYMBOL_KINDS",
    # P6
    "PROMPT_SLOT_TYPES",
    "PROMPT_SLOT_AUTHORITY",
    "PROMPT_AUTHORITY_RULES",
    "PROMPT_FIELD_TO_SLOT",
    # P3
    "UWG_CANONICAL_SYMBOL",
    "UWG_MODULE_PATH",
    "UWG_INTERFACE_PATH",
    "LAYER_AUTHORITY_FORBIDDEN",
    "L1_WRITE_ALLOWLIST",
    "UWG_WRITE_SYMBOLS",
]
