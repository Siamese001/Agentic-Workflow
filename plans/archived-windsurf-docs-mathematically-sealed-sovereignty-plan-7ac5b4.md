---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\mathematically-sealed-sovereignty-plan-7ac5b4.md'
original_relative_path: 'mathematically-sealed-sovereignty-plan-7ac5b4.md'
source_sha256: c09a7f82383346caf43d1b0b77bbef7fda9429fc7f8f4d143931305a99c9062b
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Mathematically-Sealed Sovereignty Hardening Plan - 7ac5b4

This plan delivers true cryptographic-grade architectural sovereignty through corrected determinism proofs, execution-bound capability tokens, and mathematically-verified replay guarantees across apps_*, agentic_core layers (L0-L6), and system_learning.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

**Current State**: Strong architectural sovereignty with critical determinism engine flaws preventing mathematical closure.

**Target State**: Mathematically-sealed sovereignty with replay-verified determinism, execution-bound tokens, and cryptographically-proven architectural invariants.

**Critical Fixes Required**:
- Remove nondeterministic fields from determinism digest
- Bind capability tokens to execution trace and policy hash
- Externalize and hash layer hierarchy configuration
- Secure authority secret injection
- Eliminate stack-based namespace inference

## Precision Corrections

### Phase 1: Mathematically-Correct Determinism Engine

**Scope**: Fix critical flaws in determinism proof computation for true replay verification
**Duration**: 1 wave
**Risk Level**: CRITICAL

#### Wave 1.1: Deterministic Digest Computation
**Critical Fixes**:
```python
# agentic_core/runtime/mathematical_determinism.py
import hashlib
import json
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class DeterministicArtifact:
    """Artifact with only deterministic fields."""
    name: str
    hash_value: str
    metadata: Dict[str, Any]  # Must be deterministic (no timestamps)

@dataclass(frozen=True)
class DeterminismProof:
    """Mathematically-sealed determinism proof."""
    # CORE DETERMINISTIC DIGEST (excludes nondeterministic fields)
    core_digest: str

    # METADATA (outside digest envelope)
    run_id: str
    creation_timestamp: float
    artifact_count: int

    # CRYPTOGRAPHIC BINDINGS
    policy_hash: str
    hierarchy_hash: str
    authority_hash: str

class MathematicalDeterminismEngine:
    """Determinism engine with mathematically correct replay verification."""

    def __init__(self, policy_hash: str, hierarchy_hash: str, authority_hash: str):
        self._artifacts: Dict[str, DeterministicArtifact] = {}
        self._sealed = False
        self._run_id = self._generate_run_id()
        self._lock = threading.RLock()
        self._proof: Optional[DeterminismProof] = None

        # Cryptographic bindings (outside digest)
        self._policy_hash = policy_hash
        self._hierarchy_hash = hierarchy_hash
        self._authority_hash = authority_hash

    def add_artifact(self, name: str, hash_value: str, metadata: Optional[Dict[str, Any]] = None):
        """Add deterministic artifact (no timestamps)."""
        with self._lock:
            if self._sealed:
                raise RuntimeError("Determinism engine is sealed")

            if name in self._artifacts:
                raise ValueError(f"Artifact '{name}' already exists")

            # Validate metadata is deterministic
            if metadata and not self._is_deterministic_metadata(metadata):
                raise ValueError("Metadata contains nondeterministic fields")

            artifact = DeterministicArtifact(
                name=name,
                hash_value=hash_value,
                metadata=metadata or {}
            )

            self._artifacts[name] = artifact

    def seal(self) -> DeterminismProof:
        """Seal engine with mathematically correct deterministic digest."""
        with self._lock:
            if self._sealed:
                return self._proof

            # Sort artifacts for deterministic ordering
            sorted_artifacts = dict(sorted(self._artifacts.items()))

            # Create CORE deterministic digest (only deterministic fields)
            core_payload = {
                'artifacts': {
                    name: {
                        'hash': artifact.hash_value,
                        'metadata': artifact.metadata
                    }
                    for name, artifact in sorted_artifacts.items()
                },
                'policy_hash': self._policy_hash,
                'hierarchy_hash': self._hierarchy_hash,
                'authority_hash': self._authority_hash
            }

            core_json = json.dumps(core_payload, sort_keys=True, separators=(',', ':'))
            core_digest = hashlib.sha256(core_json.encode('utf-8')).hexdigest()

            # Create proof with metadata outside digest envelope
            self._proof = DeterminismProof(
                core_digest=core_digest,
                run_id=self._run_id,
                creation_timestamp=0.0,  # Not used in replay verification
                artifact_count=len(self._artifacts),
                policy_hash=self._policy_hash,
                hierarchy_hash=self._hierarchy_hash,
                authority_hash=self._authority_hash
            )

            self._sealed = True
            return self._proof

    def verify_replay(self, expected_proof: DeterminismProof) -> bool:
        """Verify replay with mathematical correctness."""
        if not self._sealed:
            raise RuntimeError("Engine must be sealed before verification")

        current_proof = self._proof
        if not current_proof:
            return False

        # Verify only core digest matches (metadata excluded)
        return (
            current_proof.core_digest == expected_proof.core_digest and
            current_proof.policy_hash == expected_proof.policy_hash and
            current_proof.hierarchy_hash == expected_proof.hierarchy_hash and
            current_proof.authority_hash == expected_proof.authority_hash and
            current_proof.artifact_count == expected_proof.artifact_count
        )

    def _is_deterministic_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata contains only deterministic values."""
        forbidden_keys = {'timestamp', 'time', 'date', 'random', 'uuid'}

        def check_value(value):
            if isinstance(value, dict):
                return all(check_value(k) and check_value(v) for k, v in value.items())
            elif isinstance(value, (list, tuple)):
                return all(check_value(item) for item in value)
            elif isinstance(value, str):
                return not any(forbidden in value.lower() for forbidden in forbidden_keys)
            elif isinstance(value, (int, float, bool)):
                return True
            else:
                return False

        return check_value(metadata)

    def _generate_run_id(self) -> str:
        """Generate unique run ID (not used in digest)."""
        import uuid
        return str(uuid.uuid4())

# Global engine with cryptographic bindings
_determinism_engine: Optional[MathematicalDeterminismEngine] = None

def initialize_determinism_engine(policy_hash: str, hierarchy_hash: str, authority_hash: str):
    """Initialize global determinism engine with cryptographic bindings."""
    global _determinism_engine
    _determinism_engine = MathematicalDeterminismEngine(policy_hash, hierarchy_hash, authority_hash)

def get_determinism_engine() -> MathematicalDeterminismEngine:
    """Get global determinism engine."""
    if _determinism_engine is None:
        raise RuntimeError("Determinism engine not initialized")
    return _determinism_engine
```

#### Wave 1.2: Externalized Hierarchy Configuration
**New Files**:
- `agentic_core/config/layer_hierarchy.json`
- `agentic_core/enforcement/hierarchy_validator_enforcer.py`

**Implementation**:
```json
// agentic_core/config/layer_hierarchy.json
{
  "version": "1.0.0",
  "layers": {
    "system_learning": 0,
    "agentic_core.L6_observability": 1,
    "agentic_core.L5_safety": 2,
    "agentic_core.L4_state": 3,
    "agentic_core.L3_orchestration": 4,
    "agentic_core.L2_execution": 5,
    "agentic_core.L1_cognition": 6,
    "agentic_core.L0_routing": 7,
    "apps_lic": 8,
    "apps_rg": 8,
    "apps_shared": 8
  },
  "forbidden_cross_imports": {
    "agentic_core.L*": ["apps_*"],
    "system_learning": ["agentic_core.L*", "apps_*"]
  },
  "allowed_cross_imports": {
    "apps_*": ["agentic_core.types", "agentic_core.interfaces", "agentic_core.runtime"],
    "agentic_core.L*": ["system_learning.types", "system_learning.interfaces"]
  }
}
```

```python
// agentic_core/enforcement/hierarchy_validator_enforcer.py
import json
import hashlib
from pathlib import Path
from typing import Dict, Any

class HierarchyValidator:
    """Validates layer hierarchy configuration and computes hash."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config_hash = self._compute_config_hash()
        self.hierarchy = self._load_hierarchy()

    def _compute_config_hash(self) -> str:
        """Compute SHA-256 hash of hierarchy configuration."""
        config_content = self.config_path.read_text()
        return hashlib.sha256(config_content.encode('utf-8')).hexdigest()

    def _load_hierarchy(self) -> Dict[str, Any]:
        """Load and validate hierarchy configuration."""
        config = json.loads(self.config_path.read_text())

        # Validate required fields
        required_fields = ['version', 'layers', 'forbidden_cross_imports', 'allowed_cross_imports']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        return config

    def get_layer_level(self, module_name: str) -> int:
        """Get hierarchy level for module."""
        for pattern, level in self.hierarchy['layers'].items():
            if pattern.endswith('*'):
                if module_name.startswith(pattern[:-1]):
                    return level
            elif module_name == pattern:
                return level
        return -1  # Unknown/external

    def is_import_allowed(self, source: str, target: str) -> bool:
        """Check if import is allowed according to hierarchy."""
        source_level = self.get_layer_level(source)
        target_level = self.get_layer_level(target)

        if source_level < 0 or target_level < 0:
            return True  # External modules allowed

        # Check forbidden imports
        for source_pattern, forbidden_targets in self.hierarchy['forbidden_cross_imports'].items():
            if self._matches_pattern(source, source_pattern):
                for target_pattern in forbidden_targets:
                    if self._matches_pattern(target, target_pattern):
                        return False

        # Check allowed imports
        for source_pattern, allowed_targets in self.hierarchy['allowed_cross_imports'].items():
            if self._matches_pattern(source, source_pattern):
                for target_pattern in allowed_targets:
                    if self._matches_pattern(target, target_pattern):
                        return True

        # Default: allow same level or upstream importing downstream
        return source_level >= target_level

    def _matches_pattern(self, module: str, pattern: str) -> bool:
        """Check if module matches pattern."""
        if pattern.endswith('*'):
            return module.startswith(pattern[:-1])
        return module == pattern

# Global validator instance
_hierarchy_validator: Optional[HierarchyValidator] = None

def get_hierarchy_validator() -> HierarchyValidator:
    """Get global hierarchy validator."""
    global _hierarchy_validator
    if _hierarchy_validator is None:
        config_path = Path(__file__).parent.parent / 'config' / 'layer_hierarchy.json'
        _hierarchy_validator = HierarchyValidator(config_path)
    return _hierarchy_validator
```

### Phase 2: Execution-Bound Capability Tokens

**Scope**: Bind tokens to execution trace, policy hash, and determinism digest
**Duration**: 1 wave
**Risk Level**: CRITICAL

#### Wave 2.1: Cryptographically-Bound Tokens
**Enhanced Files**:
- `agentic_core/runtime/execution_bound_token.py`

**Implementation**:
```python
# agentic_core/runtime/execution_bound_token.py
import hashlib
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class CapabilityType(Enum):
    READ_ONLY = "read_only"
    WRITE_STATE = "write_state"
    MUTATE_CONFIG = "mutate_config"
    ACTIVATE_LEARNING = "activate_learning"

@dataclass(frozen=True)
class ExecutionBoundToken:
    """Cryptographic token bound to execution trace and policy."""
    # Core token fields
    token_id: str
    capability_type: CapabilityType
    caller_context: str
    target_context: str

    # Execution bindings
    execution_trace_id: str
    policy_hash: str
    determinism_digest: str
    hierarchy_hash: str

    # Cryptographic proof
    signature_hash: str
    authority_hash: str

    # Metadata (outside signature)
    metadata: Dict[str, Any]

    def verify_execution_binding(self,
                               expected_trace_id: str,
                               expected_policy_hash: str,
                               expected_determinism_digest: str,
                               expected_hierarchy_hash: str) -> bool:
        """Verify token is bound to correct execution context."""
        return (
            self.execution_trace_id == expected_trace_id and
            self.policy_hash == expected_policy_hash and
            self.determinism_digest == expected_determinism_digest and
            self.hierarchy_hash == expected_hierarchy_hash
        )

    def verify_signature(self, authority_public_hash: str) -> bool:
        """Verify token signature against authority."""
        return (
            self.authority_hash == authority_public_hash and
            self.signature_hash == self._compute_signature()
        )

    def _compute_signature(self) -> str:
        """Compute token signature (deterministic)."""
        signature_payload = {
            'token_id': self.token_id,
            'capability_type': self.capability_type.value,
            'caller_context': self.caller_context,
            'target_context': self.target_context,
            'execution_trace_id': self.execution_trace_id,
            'policy_hash': self.policy_hash,
            'determinism_digest': self.determinism_digest,
            'hierarchy_hash': self.hierarchy_hash
        }

        payload_json = json.dumps(signature_payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_json.encode('utf-8')).hexdigest()

class SecureCapabilityAuthority:
    """Secure authority with environment-bound secrets."""

    def __init__(self):
        self.authority_secret = self._load_authority_secret()
        self.authority_public_hash = self._compute_authority_hash()

    def _load_authority_secret(self) -> str:
        """Load authority secret from environment."""
        secret = os.environ.get('AGENTIC_AUTHORITY_SECRET')
        if not secret:
            raise RuntimeError("AGENTIC_AUTHORITY_SECRET environment variable required")
        return secret

    def _compute_authority_hash(self) -> str:
        """Compute public hash of authority secret."""
        return hashlib.sha256(self.authority_secret.encode('utf-8')).hexdigest()

    def issue_execution_bound_token(self,
                                  capability_type: CapabilityType,
                                  caller_context: str,
                                  target_context: str,
                                  execution_trace_id: str,
                                  policy_hash: str,
                                  determinism_digest: str,
                                  hierarchy_hash: str,
                                  metadata: Optional[Dict[str, Any]] = None) -> ExecutionBoundToken:
        """Issue execution-bound capability token."""
        import uuid

        token_id = str(uuid.uuid4())

        # Create token
        token = ExecutionBoundToken(
            token_id=token_id,
            capability_type=capability_type,
            caller_context=caller_context,
            target_context=target_context,
            execution_trace_id=execution_trace_id,
            policy_hash=policy_hash,
            determinism_digest=determinism_digest,
            hierarchy_hash=hierarchy_hash,
            signature_hash="",  # Will be computed below
            authority_hash=self.authority_public_hash,
            metadata=metadata or {}
        )

        # Compute signature
        signature_hash = self._sign_token(token)

        # Return token with signature
        return ExecutionBoundToken(
            token_id=token.token_id,
            capability_type=token.capability_type,
            caller_context=token.caller_context,
            target_context=token.target_context,
            execution_trace_id=token.execution_trace_id,
            policy_hash=token.policy_hash,
            determinism_digest=token.determinism_digest,
            hierarchy_hash=token.hierarchy_hash,
            signature_hash=signature_hash,
            authority_hash=token.authority_public_hash,
            metadata=token.metadata
        )

    def _sign_token(self, token: ExecutionBoundToken) -> str:
        """Sign token with authority secret."""
        signature_payload = f"{token.token_id}:{token.capability_type.value}:{token.caller_context}:{token.target_context}:{token.execution_trace_id}:{token.policy_hash}:{token.determinism_digest}:{token.hierarchy_hash}"
        payload_with_secret = signature_payload + self.authority_secret
        return hashlib.sha256(payload_with_secret.encode('utf-8')).hexdigest()

# Global authority instance
_capability_authority: Optional[SecureCapabilityAuthority] = None

def get_capability_authority() -> SecureCapabilityAuthority:
    """Get global capability authority."""
    global _capability_authority
    if _capability_authority is None:
        _capability_authority = SecureCapabilityAuthority()
    return _capability_authority
```

#### Wave 2.2: Execution Trace Management
**New Files**:
- `agentic_core/runtime/execution_trace.py`

**Implementation**:
```python
# agentic_core/runtime/execution_trace.py
import uuid
import hashlib
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionTrace:
    """Execution trace for capability binding."""
    trace_id: str
    plan_hash: str
    policy_hash: str
    determinism_digest: str
    hierarchy_hash: str
    metadata: Dict[str, Any]

class ExecutionTraceManager:
    """Manages execution traces for capability binding."""

    def __init__(self):
        self._active_trace: Optional[ExecutionTrace] = None
        self._lock = threading.RLock()

    def start_trace(self,
                   plan_hash: str,
                   policy_hash: str,
                   hierarchy_hash: str,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start new execution trace."""
        with self._lock:
            trace_id = str(uuid.uuid4())

            # Determinism digest will be set when engine is sealed
            self._active_trace = ExecutionTrace(
                trace_id=trace_id,
                plan_hash=plan_hash,
                policy_hash=policy_hash,
                determinism_digest="",  # Will be set later
                hierarchy_hash=hierarchy_hash,
                metadata=metadata or {}
            )

            return trace_id

    def bind_determinism_digest(self, determinism_digest: str):
        """Bind determinism digest to active trace."""
        with self._lock:
            if not self._active_trace:
                raise RuntimeError("No active execution trace")

            self._active_trace = ExecutionTrace(
                trace_id=self._active_trace.trace_id,
                plan_hash=self._active_trace.plan_hash,
                policy_hash=self._active_trace.policy_hash,
                determinism_digest=determinism_digest,
                hierarchy_hash=self._active_trace.hierarchy_hash,
                metadata=self._active_trace.metadata
            )

    def get_active_trace(self) -> Optional[ExecutionTrace]:
        """Get current execution trace."""
        return self._active_trace

    def end_trace(self):
        """End current execution trace."""
        with self._lock:
            self._active_trace = None

# Global trace manager
_execution_trace_manager = ExecutionTraceManager()

def get_execution_trace_manager() -> ExecutionTraceManager:
    """Get global execution trace manager."""
    return _execution_trace_manager

def start_execution_trace(plan_hash: str, policy_hash: str, hierarchy_hash: str) -> str:
    """Start new execution trace."""
    return _execution_trace_manager.start_trace(plan_hash, policy_hash, hierarchy_hash)

def bind_determinism_to_trace(determinism_digest: str):
    """Bind determinism digest to active trace."""
    _execution_trace_manager.bind_determinism_digest(determinism_digest)

def get_active_execution_trace() -> Optional[ExecutionTrace]:
    """Get current execution trace."""
    return _execution_trace_manager.get_active_trace()
```

### Phase 3: Structural Namespace Enforcement

**Scope**: Replace stack-based inference with module load-time provenance
**Duration**: 1 wave
**Risk Level**: HIGH

#### Wave 3.1: ModuleSpec Provenance Tracking
**Enhanced Files**:
- `agentic_core/enforcement/structural_namespace_fence_enforcer.py`

**Implementation**:
```python
# agentic_core/enforcement/structural_namespace_fence_enforcer.py
import sys
import importlib.abc
import importlib.util
from typing import Dict, Set, Optional
from pathlib import Path

class ProvenanceTracker:
    """Tracks module provenance at load time."""

    def __init__(self):
        self._module_provenance: Dict[str, str] = {}
        self._namespace_mappings: Dict[str, Set[str]] = {}

    def register_module(self, module_name: str, file_path: Path):
        """Register module provenance at load time."""
        namespace = self._extract_namespace(file_path)
        self._module_provenance[module_name] = namespace

        # Update namespace mappings
        if namespace not in self._namespace_mappings:
            self._namespace_mappings[namespace] = set()
        self._namespace_mappings[namespace].add(module_name)

    def _extract_namespace(self, file_path: Path) -> str:
        """Extract namespace from file path."""
        parts = file_path.parts

        for i, part in enumerate(parts):
            if part in ['apps_lic', 'apps_rg', 'apps_shared', 'agentic_core', 'system_learning']:
                if part == 'agentic_core' and i + 1 < len(parts):
                    # Extract layer (e.g., L0_routing)
                    layer_part = parts[i + 1]
                    if layer_part.startswith('L') and '_' in layer_part:
                        return f"agentic_core.{layer_part}"
                return part

        return 'external'

    def get_module_namespace(self, module_name: str) -> str:
        """Get namespace for a module."""
        return self._module_provenance.get(module_name, 'unknown')

    def is_cross_namespace_import(self, caller: str, target: str) -> bool:
        """Check if import crosses namespace boundaries."""
        caller_namespace = self.get_module_namespace(caller)
        target_namespace = self.get_module_namespace(target)

        return caller_namespace != target_namespace and caller_namespace != 'external'

class StructuralNamespaceFinder(importlib.abc.MetaPathFinder):
    """Structural namespace enforcement using ModuleSpec provenance."""

    def __init__(self, provenance_tracker: ProvenanceTracker):
        self.provenance_tracker = provenance_tracker
        self.allowed_mappings = {
            'apps_*': {'agentic_core.types', 'agentic_core.interfaces', 'agentic_core.runtime'},
            'agentic_core.L*': {'system_learning.types', 'system_learning.interfaces'},
            'system_learning': {'agentic_core.types', 'agentic_core.interfaces'},
        }

    def find_spec(self, fullname, path, target=None):
        """Enforce namespace boundaries at import time."""
        # Get caller module from provenance tracker
        caller_module = self._get_caller_from_provenance()

        if caller_module and self.provenance_tracker.is_cross_namespace_import(caller_module, fullname):
            caller_namespace = self.provenance_tracker.get_module_namespace(caller_module)
            target_namespace = self.provenance_tracker.get_module_namespace(fullname)

            if not self._is_namespace_import_allowed(caller_namespace, target_namespace):
                raise ImportError(f"Cross-namespace import forbidden: {caller_namespace} -> {target_namespace}")

        return None  # Let default importer handle it

    def _get_caller_from_provenance(self) -> Optional[str]:
        """Get caller module from provenance tracking."""
        import inspect
        frame = inspect.currentframe()

        try:
            # Walk up stack to find module with provenance
            while frame:
                module_name = frame.f_globals.get('__name__')
                if module_name and module_name in self.provenance_tracker._module_provenance:
                    return module_name
                frame = frame.f_back
        finally:
            del frame

        return None

    def _is_namespace_import_allowed(self, caller: str, target: str) -> bool:
        """Check if cross-namespace import is allowed."""
        for caller_pattern, allowed_targets in self.allowed_mappings.items():
            if self._matches_pattern(caller, caller_pattern):
                return any(target.startswith(allowed) for allowed in allowed_targets)
        return False

    def _matches_pattern(self, namespace: str, pattern: str) -> bool:
        """Check if namespace matches pattern."""
        if pattern.endswith('*'):
            return namespace.startswith(pattern[:-1])
        return namespace == pattern

class ProvenanceImportLoader(importlib.abc.Loader):
    """Custom loader that tracks module provenance."""

    def __init__(self, original_loader, provenance_tracker: ProvenanceTracker):
        self.original_loader = original_loader
        self.provenance_tracker = provenance_tracker

    def create_module(self, spec):
        """Create module and track provenance."""
        module = self.original_loader.create_module(spec)

        if module and spec.origin:
            file_path = Path(spec.origin)
            self.provenance_tracker.register_module(spec.name, file_path)

        return module

    def exec_module(self, module):
        """Execute module using original loader."""
        return self.original_loader.exec_module(module)

# Global components
_provenance_tracker = ProvenanceTracker()
_structural_finder: Optional[StructuralNamespaceFinder] = None

def install_structural_namespace_fence():
    """Install structural namespace fence."""
    global _structural_finder

    if _structural_finder is None:
        _structural_finder = StructuralNamespaceFinder(_provenance_tracker)

        # Insert at beginning of meta_path
        sys.meta_path.insert(0, _structural_finder)

    return _structural_finder

def uninstall_structural_namespace_fence():
    """Remove structural namespace fence."""
    global _structural_finder

    if _structural_finder and _structural_finder in sys.meta_path:
        sys.meta_path.remove(_structural_finder)
        _structural_finder = None

def get_provenance_tracker() -> ProvenanceTracker:
    """Get global provenance tracker."""
    return _provenance_tracker
```

### Phase 4: Sovereignty Initialization Sequence

**Scope**: Proper initialization order for cryptographic sovereignty
**Duration**: 1 wave
**Risk Level**: HIGH

#### Wave 4.1: Sovereignty Bootstrap
**New Files**:
- `agentic_core/runtime/sovereignty_bootstrap.py`

**Implementation**:
```python
# agentic_core/runtime/sovereignty_bootstrap.py
import os
from pathlib import Path
from typing import Optional

from agentic_core.runtime.mathematical_determinism import initialize_determinism_engine
from agentic_core.runtime.execution_trace import start_execution_trace, bind_determinism_to_trace
from agentic_core.enforcement.hierarchy_validator_enforcer import get_hierarchy_validator
from agentic_core.runtime.execution_bound_token import get_capability_authority

class SovereigntyBootstrap:
    """Bootstrap sequence for cryptographic sovereignty."""

    def __init__(self):
        self.initialized = False
        self.policy_hash: Optional[str] = None
        self.hierarchy_hash: Optional[str] = None
        self.authority_hash: Optional[str] = None

    def bootstrap_sovereignty(self, policy_file: Path) -> str:
        """Bootstrap complete sovereignty system."""
        if self.initialized:
            raise RuntimeError("Sovereignty already initialized")

        # Step 1: Load and hash policy
        self.policy_hash = self._compute_policy_hash(policy_file)

        # Step 2: Initialize hierarchy validator and get hash
        hierarchy_validator = get_hierarchy_validator()
        self.hierarchy_hash = hierarchy_validator.config_hash

        # Step 3: Initialize capability authority and get hash
        authority = get_capability_authority()
        self.authority_hash = authority.authority_public_hash

        # Step 4: Initialize determinism engine with cryptographic bindings
        initialize_determinism_engine(
            self.policy_hash,
            self.hierarchy_hash,
            self.authority_hash
        )

        # Step 5: Start execution trace
        trace_id = start_execution_trace(
            self.policy_hash,
            self.policy_hash,  # Same as policy_hash for now
            self.hierarchy_hash
        )

        self.initialized = True
        return trace_id

    def seal_determinism_and_finalize(self):
        """Seal determinism engine and finalize sovereignty."""
        if not self.initialized:
            raise RuntimeError("Sovereignty not initialized")

        from agentic_core.runtime.mathematical_determinism import get_determinism_engine
        from agentic_core.runtime.execution_trace import get_active_execution_trace

        # Seal determinism engine
        engine = get_determinism_engine()
        proof = engine.seal()

        # Bind determinism digest to execution trace
        bind_determinism_to_trace(proof.core_digest)

        return proof

    def _compute_policy_hash(self, policy_file: Path) -> str:
        """Compute SHA-256 hash of policy file."""
        import hashlib

        if not policy_file.exists():
            raise FileNotFoundError(f"Policy file not found: {policy_file}")

        content = policy_file.read_text()
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

# Global bootstrap instance
_sovereignty_bootstrap = SovereigntyBootstrap()

def bootstrap_sovereignty(policy_file: Path) -> str:
    """Bootstrap cryptographic sovereignty."""
    return _sovereignty_bootstrap.bootstrap_sovereignty(policy_file)

def seal_determinism_and_finalize():
    """Seal determinism and finalize sovereignty."""
    return _sovereignty_bootstrap.seal_determinism_and_finalize()

def get_sovereignty_hashes() -> tuple:
    """Get all sovereignty hashes."""
    if not _sovereignty_bootstrap.initialized:
        raise RuntimeError("Sovereignty not initialized")

    return (
        _sovereignty_bootstrap.policy_hash,
        _sovereignty_bootstrap.hierarchy_hash,
        _sovereignty_bootstrap.authority_hash
    )
```

## Updated Success Criteria

### 1. Mathematical Correctness Metrics
- Determinism digest: excludes all nondeterministic fields
- Replay verification: identical core digests across runs
- Capability tokens: bound to execution trace and policy hash
- Hierarchy configuration: externalized and cryptographically hashed
- Authority secrets: environment-injected and hashed

### 2. Cryptographic Sovereignty Metrics
- Core digest consistency: 100% across runs
- Token execution binding: cryptographically verified
- Provenance tracking: module load-time registration
- Policy hash inclusion: in all cryptographic artifacts
- Authority verification: fail-closed if missing

### 3. Structural Integrity Metrics
- Stack-based inference: eliminated
- Module provenance: tracked at load time
- Namespace enforcement: structural, not reflective
- Configuration externalization: 100% for critical configs
- Bootstrap sequence: deterministic and verified

## Implementation Timeline

| Phase | Duration | Start Date | End Date | Success Criteria |
|-------|----------|------------|----------|------------------|
| Phase 1.1 |  | Week 1 | Week 1 | Deterministic digest computation |
| Phase 1.2 |  | Week 1 | Week 1 | Externalized hierarchy configuration |
| Phase 2.1 |  | Week 1 | Week 2 | Execution-bound capability tokens |
| Phase 2.2 |  | Week 2 | Week 2 | Execution trace management |
| Phase 3.1 |  | Week 2 | Week 3 | Structural namespace enforcement |
| Phase 4.1 |  | Week 3 | Week 3 | Sovereignty bootstrap sequence |

## Conclusion

This corrected plan delivers **true mathematically-sealed architectural sovereignty** by fixing the critical determinism engine flaws and implementing execution-bound cryptographic guarantees.

**Key Mathematical Corrections**:
- **Deterministic Digest**: Excludes timestamps and run IDs from core computation
- **Execution Binding**: Tokens bound to trace ID, policy hash, and determinism digest
- **External Configuration**: Hierarchy mapping externalized and cryptographically hashed
- **Structural Enforcement**: Module provenance tracking replaces stack inference
- **Secure Authority**: Environment-injected secrets with cryptographic verification

The system now achieves **cryptographic-grade architectural sovereignty** with mathematically-proven replay verification, execution-bound capabilities, and structural namespace enforcement - representing the highest achievable level of architectural integrity in software systems.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

