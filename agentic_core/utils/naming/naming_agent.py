"""
NamingAgent: Canon Naming Law Enforcer (Key 49 territory)

Enforces:
- snake_case only (no CamelCase, no hyphens)
- High-signal canon keywords in non-root files (from CANON_SIGNALS)
- Forbidden generic/versioned/temporary filenames (FORBIDDEN_PATTERNS)
- Sovereign marker presence in root files (validator, compliance, etc.)
- Provides placement guidance heuristics for healer agents

Replaces logic from void_compliance.py:
  - validate_file_naming()
  - get_placement_guidance()
  - HIGH_SIGNAL_KEYWORDS usage

Placed in utils/naming per semantic_l2_registry:
  "Naming law enforcement logic, casing validators, and canon signal checks"
"""
from pathlib import Path
from typing import Tuple, Dict, List
import re

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    CANON_SIGNALS,              # High-signal keywords SSOT
    FORBIDDEN_PATTERNS,         # Compiled regex list of banned names
    ROOT_PROTECTED_FILES,
)


class naming_agent:
    """
    Autonomous agent for naming law compliance.
    Operates after LocationAgent (assumes file is in valid territory).
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.high_signal_keywords = CANON_SIGNALS
        self.forbidden_patterns = FORBIDDEN_PATTERNS

    def get_placement_guidance(self, content_preview: str) -> str:
        """
        High-signal heuristic guidance for healer/orchestrator agents.
        Helps suggest correct L-layer placement based on content.
        SSOT for Key 40/49 migration hints.
        """
        lower_content = content_preview.lower()

        if any(k in lower_content for k in ['planner', 'strategy', 'reasoning', 'mission', 'intent', 'decompose']):
            return 'agentic_core/L1_cognition'
        if any(k in lower_content for k in ['thought', 'node', 'execute', 'react', 'chain']):
            return 'agentic_core/L1_cognition/thought_engine'
        if any(k in lower_content for k in ['router', 'orchestrator', 'fission', 'hop', 'workflow', 'coordinate']):
            return 'agentic_core/L3_orchestration'
        if any(k in lower_content for k in ['pinecone', 'redis', 'vector', 'embedding', 'storage', 'cache', 'ledger']):
            return 'agentic_core/L4_state'
        if any(k in lower_content for k in ['guardrail', 'safety', 'redteam', 'gravity', 'validator']):
            return 'agentic_core/L5_safety'
        if 'prompt' in lower_content or 'template' in lower_content or 'persona' in lower_content:
            return 'agentic_core/prompt_governance'
        if 'schema' in lower_content or 'model' in lower_content or 'pydantic' in lower_content:
            return 'agentic_core/schemas'

        # Default fallback
        return 'agentic_core/L1_cognition'

    def validate_file_naming(self, file_path: Path) -> Tuple[bool, str]:
        """
        Core naming law validation.
        Returns (is_compliant, reason_or_guidance)
        """
        file_name = file_path.name

        if not file_name.endswith('.py'):
            return True, "Non-Python file - naming exempt"

        stem = file_path.stem
        lower_stem = stem.lower()

        # === SNAKE_CASE ENFORCEMENT ===
        if re.search(r'[A-Z]', stem):  # Any uppercase letter
            return False, f"NAMING VIOLATION: '{file_name}' contains uppercase letters (must be snake_case)"
        if '-' in stem:
            return False, f"NAMING VIOLATION: '{file_name}' contains hyphens (use underscores)"

        # === ROOT-LEVEL SOVEREIGN MARKER CHECK ===
        try:
            rel_path = file_path.relative_to(self.project_root)
            is_root_file = len(rel_path.parts) == 1
        except ValueError:
            return False, "File outside project root"

        if is_root_file:
            if file_name in ROOT_PROTECTED_FILES:
                return True, "Protected sovereign root file (Key 0 exempt)"

            sovereign_markers = {'validator', 'compliance', 'healer', 'enforcer', 'governor', 'auditor', 'canon'}
            if not any(marker in lower_stem for marker in sovereign_markers):
                return False, f"SOVEREIGN VIOLATION: Root file '{file_name}' missing required marker {sovereign_markers}"
            return True, "Valid sovereign root file"

        # === FORBIDDEN GENERIC/VERSIONED NAMES ===
        for pattern in self.forbidden_patterns:
            if pattern.match(file_name):
                return False, f"NAMING VIOLATION: Forbidden pattern '{file_name}' matched {pattern.pattern}"

        # === HIGH-SIGNAL KEYWORD ENFORCEMENT ===
        if not any(keyword in lower_stem for keyword in self.high_signal_keywords):
            try:
                # Read content safely
                content_preview = file_path.read_text(encoding='utf-8', errors='ignore')[:1000]
                guidance = self.get_placement_guidance(content_preview)
            except Exception:
                guidance = "agentic_core/L1_cognition" # fallback

            return False, (
                f"SIGNAL VIOLATION: '{file_name}' lacks high-signal canon keyword. "
                f"Suggested placement: {guidance}"
            )

        return True, "Naming compliant with high-signal requirement"

    def run(self, files: List[Path]) -> List[Tuple[Path, str]]:
        """
        Full naming compliance scan on provided files.
        Returns list of violations as (file_path, reason).
        """
        violations: List[Tuple[Path, str]] = []

        for file_path in files:
            is_valid, reason = self.validate_file_naming(file_path)
            if not is_valid:
                violations.append((file_path, reason))

        return violations

    def suggest_fixes(self, violations: List[Tuple[Path, str]]) -> Dict[Path, str]:
        """
        Optional: Generate suggested rename targets.
        Useful for autonomous healer integration.
        """
        suggestions = {}
        for file_path, reason in violations:
            if "SIGNAL VIOLATION" in reason or "Suggested placement" in reason:
                # Extract suggested path from reason if present
                if "Suggested placement:" in reason:
                    suggested_path = reason.split("Suggested placement:")[-1].strip()
                    # new_name = file_path.name  # Could enhance with keyword injection
                    suggestions[file_path] = f"Move to {suggested_path} (consider adding signal keyword)"
        return suggestions


# Uppercase alias for backward compatibility
NamingAgent = naming_agent
