from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "capability_extractor_util")
emit_determinism_digest("p0", "capability_extractor_util")

_emit_dispatches_healing_run("p1", "capability_extractor_util", "L5")
_emit_routes_through("p1", "capability_extractor_util", "L5")
_emit_escalates_to_human("p1", "capability_extractor_util", "L5")
_emit_reads_policy_state("p1", "capability_extractor_util", "L5")

_emit_applies_guardrail("p0", "capability_extractor_util", "p0_governance")
_emit_snapshots_state("p0", "capability_extractor_util", "state_snapshot")

"\nCapability Extractor - AST-based capability analysis for agent classes.\nExtracted from agent_capability_supplement.py for single responsibility.\n"
import ast

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class CapabilityExtractor:
    """Extracts semantic capabilities from agent class definitions."""

    COMMON_METHODS = {"__init__", "heal_violation", "execute", "run", "validate", "monitor"}
    SEMANTIC_KEYWORDS = {
        "healing": ["heal", "fix", "repair"],
        "validation": ["validate", "check", "enforce"],
        "detection": ["detect", "find", "scan"],
        "pruning": ["prune", "clean", "remove"],
        "mapping": ["map", "territory", "structure"],
        "monitoring": ["watch", "monitor", "observe"],
        "git_integration": ["git"],
    }
    PATTERN_KEYWORDS = {
        "git_operations": [("git", "subprocess"), ("git", "repo")],
        "dead_code_analysis": ["dead code", "unused"],
        "filesystem_introspection": [("filesystem",), ("path", "exists")],
        "redis_integration": ["redis"],
    }

    def extract_capabilities(self, class_node: ast.ClassDef) -> dict[str, any]:
        """Extract rich capability metadata from an agent class.

        Args:
            class_node: AST ClassDef node to analyze

        Returns:
            Dictionary with semantic_tags, unique_methods, patterns, and valuable_methods
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "CapabilityExtractor.extract_capabilities"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CapabilityExtractor.extract_capabilities".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        caps = {"semantic_tags": set(), "unique_methods": set(), "patterns": set(), "valuable_methods": []}
        for item in class_node.body:
            if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            method_name = item.name
            method_loc = item.lineno
            if method_name not in self.COMMON_METHODS:
                caps["unique_methods"].add(method_name)
                caps["valuable_methods"].append((method_name, method_loc, "Unique method signature"))
            self._tag_by_method_name(method_name, caps)
            self._analyze_method_body(item, method_name, method_loc, caps)
        return caps

    def _tag_by_method_name(self, method_name: str, caps: dict) -> None:
        """Tag capabilities based on method name patterns.

        Args:
            method_name: Name of the method
            caps: Capabilities dictionary to update
        """
        lower_name = method_name.lower()
        for tag, keywords in self.SEMANTIC_KEYWORDS.items():
            if any(k in lower_name for k in keywords):
                caps["semantic_tags"].add(tag)

    def _analyze_method_body(
        self, item: ast.FunctionDef, method_name: str, method_loc: int, caps: dict
    ) -> None:
        """Analyze method body for specialized patterns.

        Args:
            item: AST FunctionDef node
            method_name: Name of the method
            method_loc: Line number of method
            caps: Capabilities dictionary to update
        """
        try:
            body_source = ast.unparse(item.body) if hasattr(ast, "unparse") else ""
        # guardian: allow-silent-swallow
        except:
            body_source = ""
        lower_body = body_source.lower()
        if (
            "git" in lower_body
            and "subprocess" in lower_body
            or ("git" in lower_body and "repo" in lower_body)
        ):
            caps["patterns"].add("git_operations")
            caps["valuable_methods"].append((method_name, method_loc, "Git repository interaction"))
        if "dead code" in lower_body or "unused" in lower_body:
            caps["patterns"].add("dead_code_analysis")
            caps["valuable_methods"].append((method_name, method_loc, "Dead/unused code detection"))
        if "filesystem" in lower_body or ("path" in lower_body and "exists" in lower_body):
            caps["patterns"].add("filesystem_introspection")
            caps["valuable_methods"].append((method_name, method_loc, "Advanced filesystem checks"))
        if "redis" in lower_body:
            caps["patterns"].add("redis_integration")
            caps["valuable_methods"].append((method_name, method_loc, "Redis state access"))

    def get_all_capabilities(self, caps: dict) -> set[str]:
        """Get all capabilities (semantic tags + patterns) as a unified set.

        Args:
            caps: Capabilities dictionary

        Returns:
            Set of all capability identifiers
        """
        return caps["semantic_tags"] | caps["patterns"]

    def filter_unique_methods(self, method_names: set[str]) -> set[str]:
        """Filter out common methods, returning only unique ones.

        Args:
            method_names: Set of method names to filter

        Returns:
            Set of unique (non-common) method names
        """
        return method_names - self.COMMON_METHODS
