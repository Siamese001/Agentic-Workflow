"""AUTO_FIX rule: Add layer assignment comments.

Auto-assigns L_UNKNOWN layers by adding a layer marker comment
based on file path inference.
"""

from __future__ import annotations

from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixCategory, FixResult


@repair_rule("fix_layer_assignment", priority=30)
class FixLayerAssignmentRule(BaseRepairRule):
    """Fixes unknown layer assignments by adding layer markers.

    Adds a layer marker comment like:
        # ADG Layer: L2

    Based on path inference rules:
        - agentic_core/L0_* -> L0
        - agentic_core/L1_* -> L1
        - etc.
        - apps_* -> L_APP
        - tests/ -> L_TEST

    Safety: Medium - path-based inference is generally reliable
    """

    rule_name = "Fix Layer Assignment"
    rule_description = "Adds layer marker comments to L_UNKNOWN modules"
    rule_priority = 30

    # Issue types this rule can handle
    HANDLED_ISSUES = {
        "unknown_layer",
        "unknown_layer_inferrable",
    }

    # Layer inference patterns
    LAYER_PATTERNS = [
        ("agentic_core/L0_", "L0"),
        ("agentic_core/L1_", "L1"),
        ("agentic_core/L2_", "L2"),
        ("agentic_core/L3_", "L3"),
        ("agentic_core/L4_", "L4"),
        ("agentic_core/L5_", "L5"),
        ("agentic_core/L6_", "L6"),
        ("agentic_core/L_CONTRACTS", "L_CONTRACTS"),
    ]

    APP_PATTERNS = [
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rfp",
        "apps_rg",
        "apps_shared",
        "apps_underwriting_ai",
    ]

    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies."""
        return deficiency.category == FixCategory.AUTO_FIX and deficiency.issue_type in self.HANDLED_ISSUES

    def can_fix(self, deficiency: Deficiency) -> tuple[bool, str]:
        """Determine if fix can be applied."""
        file_path = deficiency.file_path

        if file_path == "ADG_METADATA":
            return False, "Cannot fix ADG metadata"

        if not file_path.endswith(".py"):
            return False, "Not a Python file"

        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"

        # Get inferred layer from metadata or compute it
        inferred_layer = deficiency.metadata.get("inferred_layer")
        if not inferred_layer:
            inferred_layer = self._infer_layer(file_path)

        if not inferred_layer:
            return False, "Cannot infer layer from path"

        # Check if already has layer marker
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Cannot read file: {e}"

        if "# ADG Layer:" in content:
            return False, "Layer marker already present"

        return True, f"Can add layer marker for {inferred_layer}"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by adding a layer marker."""
        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            original_content = path.read_text(encoding="utf-8")

            # Get inferred layer
            inferred_layer = deficiency.metadata.get("inferred_layer")
            if not inferred_layer:
                inferred_layer = self._infer_layer(file_path)

            if not inferred_layer:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="Could not infer layer",
                )

            # Create layer marker comment
            marker_line = f"# ADG Layer: {inferred_layer}\n"

            # Insert after shebang or encoding declaration, or at top
            lines = original_content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("#!/"):
                    insert_index = i + 1
                elif stripped.startswith("# -*- coding"):
                    insert_index = i + 1
                elif stripped.startswith('"""') or stripped.startswith("'''"):
                    # Insert before docstring
                    insert_index = i
                    break

            # Insert the marker
            new_lines = lines[:insert_index]
            if insert_index > 0 and not lines[insert_index - 1].strip() == "":
                new_lines.append("")  # Add blank line before marker
            new_lines.append(marker_line.rstrip())
            if insert_index < len(lines) and lines[insert_index].strip():
                new_lines.append("")  # Add blank line after marker
            new_lines.extend(lines[insert_index:])

            new_content = "\n".join(new_lines)
            path.write_text(new_content, encoding="utf-8")

            return FixResult(
                deficiency_id=deficiency.id,
                success=True,
                original_content=original_content,
                new_content=new_content,
            )

        except (OSError, SyntaxError, ValueError) as e:
            return FixResult(
                deficiency_id=deficiency.id,
                success=False,
                error_message=str(e),
            )

    def verify_fix(self, deficiency: Deficiency, result: FixResult) -> bool:
        """Verify that layer marker was added."""
        if not result.success:
            return False

        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")

            # Check for layer marker
            if "# ADG Layer:" not in content:
                return False

            # Verify the specific layer is mentioned
            inferred_layer = deficiency.metadata.get("inferred_layer")
            if inferred_layer:
                expected_marker = f"# ADG Layer: {inferred_layer}"
                if expected_marker not in content:
                    return False

            return True

        except OSError:
            return False

    def _infer_layer(self, path: str) -> str | None:
        """Infer layer from file path."""
        path_lower = path.lower().replace("\\", "/")

        # Check layer patterns
        for pattern, layer in self.LAYER_PATTERNS:
            if pattern.lower() in path_lower:
                return layer

        # Check apps
        for app_pattern in self.APP_PATTERNS:
            if app_pattern.lower() in path_lower:
                return "L_APP"

        # Check tests
        if path_lower.startswith("tests/"):
            return "L_TEST"

        return None
