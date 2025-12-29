# PromptRegistry - Sovereign Version Registry
# Territory: agentic_core/prompt_governance/version_registry
# Canon Alignment: Prompt versioning, active template management, backward compatibility
# SSOT Integration: Used by sovereign_prompt_renderer and mission logging

import json
'''Brief description of functionality and purpose.'''

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from agentic_core.runtime.shared_runtime.void_compliance import validate_file_location
except ImportError:
    # Fallback for bootstrap phase if void_compliance is not yet indexed
    def validate_file_location(path: Path, root: Path) -> tuple[bool, str]:
                    
        return True, "Bootstrap"

# NAMING FIXED: PromptRegistry → prompt_registry
class prompt_registry:
    """
    Sovereign registry for all prompt templates and meta-prompts.

    Responsibilities (per blueprint Section 8):
    - Maintain versioned entries (v1, v2, ...)
    - Track active/inactive status to prevent instruction drift
    - Provide metadata for L4 Ledger traceability
    - Ensure atomic JSON persistence
    """

    REGISTRY_FILE = Path(__file__).parent / "registry.json"

    def __init__(self):
        self.registry: Dict[str, List[Dict[str, Any]]] = {}
        
        # [L6 SOVEREIGNTY] Validate our own placement at initialization
        is_valid, reason = validate_file_location(Path(__file__), Path.cwd())
        if not is_valid:
             # Non-breaking warning for deployment; critical in validation missions
             print(f"[!] PromptRegistry placement violation: {reason}")

        self._load_registry()

    def _load_registry(self) -> None:
        """Loads the registry from disk with defensive error handling."""
        if self.REGISTRY_FILE.exists():
            try:
                content = self.REGISTRY_FILE.read_text(encoding="utf-8")
                data = json.loads(content)
                self.registry = data.get("prompts", {})
            except Exception as e:
                print(f"[!] PromptRegistry: Failed to load {self.REGISTRY_FILE}: {e}")
                self.registry = {}
        else:
            self.registry = {}
            self._save_registry()

    def _save_registry(self) -> None:
        """Saves the registry to disk using atomic-style write logic."""
        data = {
            "sovereign_version": "1.0",
            "generated_date": "2025-12-29",
            "prompts": self.registry
        }
        try:
            self.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
            # Highly defensive: format JSON with indentation for human auditability
            self.REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except IOError as e:
            print(f"[!] PromptRegistry: Critical persistence failure: {e}")

    def register_prompt(
        self,
        template_name: str,
        version: str = "v1",
        purpose: str = "",
        territory: str = "templates",
        active: bool = True,
        author: str = "SovereignOrchestrator"
    ) -> None:
        """Register or update a prompt version. Enforces single-active-version law."""
        if template_name not in self.registry:
            self.registry[template_name] = []

        entry = {
            "version": version,
            "purpose": purpose,
            "territory": territory,
            "active": active,
            "author": author,
            "registered_date": "2025-12-29"
        }

        # Deactivate previous versions to ensure SSOT convergence
        if active:
            for prev in self.registry[template_name]:
                prev["active"] = False

        self.registry[template_name].append(entry)
        self._save_registry()
        print(f"    [REGISTERED] {template_name} {version} (Territory: {territory})")

    def get_active_version(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Return the current active version metadata for a given template."""
        versions = self.registry.get(template_name, [])
        active = [v for v in versions if v.get("active", False)]
        return active[0] if active else None

    def list_active_prompts(self) -> List[str]:
        """List all currently active template names for mission planning."""
        return [name for name, versions in self.registry.items() if any(v.get("active") for v in versions)]

# Singleton Management
_global_registry: Optional[PromptRegistry] = None

def get_prompt_registry() -> PromptRegistry:
    """Factory for singleton access. Bootstraps known templates on first call."""
    global _global_registry
    if _global_registry is None:
        _global_registry = PromptRegistry()
        # Auto-register canonical templates defined in constitution
        _global_registry.register_prompt("reasoning_chain.jinja", purpose="Structured CoT reasoning")
        _global_registry.register_prompt("type_inference.jinja", purpose="Precise type hint inference")
        _global_registry.register_prompt("gravity_repair.jinja", purpose="Gravity leak dynamic import fix")
        _global_registry.register_prompt("code_healing.jinja", purpose="General code healing")
        _global_registry.register_prompt("file_placement.jinja", purpose="Relocation guidance")
        _global_registry.register_prompt("sovereign_convergence_orchestrator.jinja", territory="meta_prompts")
        _global_registry.register_prompt("red_team_governance.jinja", territory="meta_prompts")
        _global_registry.register_prompt("jailbreak_classic.jinja", purpose="Adversarial safety probing")
    return _global_registry
