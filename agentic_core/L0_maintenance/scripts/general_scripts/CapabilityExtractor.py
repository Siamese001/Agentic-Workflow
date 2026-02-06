from __future__ import annotations

"""
Capability Extractor - AST-based capability analysis for agent classes.
Extracted from agent_capability_supplement.py for single responsibility.
"""


import ast


class CapabilityExtractor:
    """Extracts semantic capabilities from agent class definitions."""

    # Common method names across agents (baseline)
    COMMON_METHODS = {"__init__", "heal_violation", "execute", "run", "validate", "monitor"}

    # Semantic keyword mappings
    SEMANTIC_KEYWORDS = {
        "healing": ["heal", "fix", "repair"],
        "validation": ["validate", "check", "enforce"],
        "detection": ["detect", "find", "scan"],
        "pruning": ["prune", "clean", "remove"],
        "mapping": ["map", "territory", "structure"],
        "monitoring": ["watch", "monitor", "observe"],
        "git_integration": ["git"],
    }

    # Pattern detection keywords
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
        caps = {
            "semantic_tags": set(),
            "unique_methods": set(),
            "patterns": set(),
            "valuable_methods": [],  # (method_name, loc, brief_desc)
        }

        for item in class_node.body:
            if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                continue

            method_name = item.name
            method_loc = item.lineno

            # Unique method detection
            if method_name not in self.COMMON_METHODS:
                caps["unique_methods"].add(method_name)
                caps["valuable_methods"].append((method_name, method_loc, "Unique method signature"))

            # Semantic tagging by name
            self._tag_by_method_name(method_name, caps)

            # Body pattern analysis
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
        # Unparse method body for keyword search
        try:
            body_source = ast.unparse(item.body) if hasattr(ast, "unparse") else ""
        except:
            body_source = ""

        lower_body = body_source.lower()

        # Git operations
        if ("git" in lower_body and "subprocess" in lower_body) or (
            "git" in lower_body and "repo" in lower_body
        ):
            caps["patterns"].add("git_operations")
            caps["valuable_methods"].append((method_name, method_loc, "Git repository interaction"))

        # Dead code analysis
        if "dead code" in lower_body or "unused" in lower_body:
            caps["patterns"].add("dead_code_analysis")
            caps["valuable_methods"].append((method_name, method_loc, "Dead/unused code detection"))

        # Filesystem introspection
        if "filesystem" in lower_body or ("path" in lower_body and "exists" in lower_body):
            caps["patterns"].add("filesystem_introspection")
            caps["valuable_methods"].append((method_name, method_loc, "Advanced filesystem checks"))

        # Redis integration
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
