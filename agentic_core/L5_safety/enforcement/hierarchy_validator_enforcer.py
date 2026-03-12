"""
agentic_core/enforcement/hierarchy_validator_enforcer.py

Validates layer hierarchy configuration loaded from the canonical JSON config
and computes a cryptographic hash that is included in the determinism proof.

If the hierarchy config file changes, its hash changes, which changes the
determinism digest, breaking any stale replay proofs and forcing CI review.
"""
import hashlib
import json
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class HierarchyValidator:
    """Loads, validates, and hashes the layer hierarchy configuration."""
    _REQUIRED_FIELDS = frozenset({'version', 'layers', 'forbidden_cross_imports', 'allowed_cross_imports'})

    def __init__(self, config_path: Path) -> None:
        if not config_path.exists():
            raise FileNotFoundError(f'Layer hierarchy config not found: {config_path}')
        self.config_path = config_path
        raw = config_path.read_text(encoding='utf-8')
        self.config_hash: str = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        self.hierarchy: dict[str, Any] = self._load_and_validate(raw)

    def _load_and_validate(self, raw: str) -> dict[str, Any]:
        config = json.loads(raw)
        missing = self._REQUIRED_FIELDS - set(config.keys())
        if missing:
            raise ValueError(f'Layer hierarchy config missing required fields: {missing}')
        return config

    def get_layer_level(self, module_name: str) -> int:
        """Return numeric hierarchy level for module_name (-1 = external/unknown)."""
        for pattern, level in self.hierarchy['layers'].items():
            if pattern.endswith('*'):
                if module_name.startswith(pattern[:-1]):
                    return int(level)
            elif module_name == pattern or module_name.startswith(pattern + '.'):
                return int(level)
        return -1

    def is_import_allowed(self, source: str, target: str) -> bool:
        """Return True iff import from source to target is permitted by policy."""
        source_level = self.get_layer_level(source)
        target_level = self.get_layer_level(target)
        if source_level < 0 or target_level < 0:
            return True
        for src_pattern, forbidden_list in self.hierarchy['forbidden_cross_imports'].items():
            if self._matches(source, src_pattern):
                for tgt_pattern in forbidden_list:
                    if self._matches(target, tgt_pattern):
                        return False
        for src_pattern, allowed_list in self.hierarchy['allowed_cross_imports'].items():
            if self._matches(source, src_pattern):
                for tgt_pattern in allowed_list:
                    if self._matches(target, tgt_pattern):
                        return True
        return source_level >= target_level

    @staticmethod
    def _matches(module: str, pattern: str) -> bool:
        if pattern.endswith('*'):
            return module.startswith(pattern[:-1])
        return module == pattern or module.startswith(pattern + '.')
_hierarchy_validator: HierarchyValidator | None = None
_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'core' / 'layer_hierarchy.json'

def get_hierarchy_validator(config_path: Path | None=None) -> HierarchyValidator:
    """Return the global HierarchyValidator (lazy-initialized from default path)."""
    global _hierarchy_validator
    if _hierarchy_validator is None:
        _hierarchy_validator = HierarchyValidator(config_path or _DEFAULT_CONFIG_PATH)
    return _hierarchy_validator
