#!/usr/bin/env python3
"""
Generate apps_lic and apps_rg structure from YAML specification.
Creates hardened module files for all paths defined in unified_structure_subatomic.yaml.
"""

import yaml
from pathlib import Path
from datetime import datetime

REPO = Path("c:/Git/Agentic-Workflow")


def extract_yaml_paths(obj, prefix='', paths=None):
    """Extract file paths from YAML structure."""
    if paths is None:
        paths = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.startswith('__'):
                continue
            new_prefix = f"{prefix}/{key}" if prefix else key
            if value is None:
                paths.append(new_prefix)
            elif isinstance(value, dict) and value:
                extract_yaml_paths(value, new_prefix, paths)
    return paths


def classify_module(path: str) -> str:
    """Classify module type from path."""
    path_lower = path.lower()
    name = Path(path).stem.lower()
    
    if "policy_check_safety" in path_lower or "check_rules" in path_lower:
        return "policy"
    elif "embedding" in path_lower or "similarity" in name or "vectors" in name:
        return "embedding"
    elif "scoring_ops" in path_lower or "score" in name:
        return "scoring"
    elif "state_update_ops" in path_lower or "aggregate" in name or "merge" in name:
        return "state_update"
    elif "understand_request" in path_lower or "query" in name or "fetch" in name or "retrieve" in name:
        return "retrieval"
    elif "utility_prepare" in path_lower or "format" in name or "prepare" in name or "build" in name:
        return "formatting"
    elif "routing_retry" in path_lower or "retry" in name or "fallback" in name:
        return "retry"
    elif "use_a_tool" in path_lower or "execute" in name or "invoke" in name or "call" in name:
        return "execution"
    elif "diagnostics" in path_lower or "inspect" in name or "diagnose" in name:
        return "diagnostics"
    elif "refinement" in path_lower or "adjust" in name or "optimize" in name or "refine" in name:
        return "refinement"
    else:
        return "generic"


def get_domain_context(path: str, app_type: str) -> dict:
    """Get domain-specific context for code generation."""
    if app_type == "lic":
        return {
            "domain": "outreach",
            "entity": "message",
            "target": "recipient",
            "action": "personalization",
            "data_type": "campaign"
        }
    else:  # rg
        return {
            "domain": "resume",
            "entity": "resume",
            "target": "job",
            "action": "generation",
            "data_type": "content"
        }


def generate_policy_module(name: str, ctx: dict) -> str:
    """Generate policy enforcement module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Policy Enforcement Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"


@dataclass
class PolicyViolation:
    """A policy violation."""
    rule_id: str
    message: str
    severity: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    decision: PolicyDecision
    violations: List[PolicyViolation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class {class_name}:
    """Policy enforcer for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.rules = self.config.get("rules", [])
        self.strict = self.config.get("strict", True)
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def evaluate(self, data: Any, context: Optional[Dict] = None) -> PolicyResult:
        """Evaluate data against policy rules."""
        violations = []
        
        # Check required fields
        violations.extend(self._check_required(data))
        
        # Check constraints
        violations.extend(self._check_constraints(data))
        
        # Check safety rules
        violations.extend(self._check_safety(data))
        
        # Determine decision
        if any(v.severity == "error" for v in violations):
            decision = PolicyDecision.DENY
        elif violations:
            decision = PolicyDecision.WARN if not self.strict else PolicyDecision.DENY
        else:
            decision = PolicyDecision.ALLOW
        
        return PolicyResult(decision=decision, violations=violations)
    
    def _check_required(self, data: Any) -> List[PolicyViolation]:
        """Check required fields."""
        violations = []
        if isinstance(data, dict):
            for field in self.config.get("required_fields", []):
                if field not in data:
                    violations.append(PolicyViolation(
                        rule_id="REQUIRED_FIELD",
                        message=f"Missing required field: {{field}}",
                        severity="error"
                    ))
        return violations
    
    def _check_constraints(self, data: Any) -> List[PolicyViolation]:
        """Check value constraints."""
        violations = []
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 10000:
                    violations.append(PolicyViolation(
                        rule_id="MAX_LENGTH",
                        message=f"Field {{key}} exceeds max length",
                        severity="warning"
                    ))
        return violations
    
    def _check_safety(self, data: Any) -> List[PolicyViolation]:
        """Check safety rules."""
        violations = []
        dangerous = ["<script>", "javascript:", "__import__"]
        data_str = str(data).lower()
        for pattern in dangerous:
            if pattern in data_str:
                violations.append(PolicyViolation(
                    rule_id="DANGEROUS_CONTENT",
                    message=f"Dangerous pattern detected",
                    severity="error"
                ))
                break
        return violations


def evaluate_policy(data: Any, config: Optional[Dict] = None) -> PolicyResult:
    """Evaluate data against policy."""
    return {class_name}(config).evaluate(data)
'''


def generate_embedding_module(name: str, ctx: dict) -> str:
    """Generate embedding/similarity module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Embedding Operations Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
import hashlib
import math
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of embedding operation."""
    vector: List[float]
    dimension: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimilarityMatch:
    """A similarity match."""
    item: Any
    score: float
    rank: int


class {class_name}:
    """Embedding operations for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.dimension = self.config.get("dimension", 128)
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def embed(self, text: str) -> EmbeddingResult:
        """Generate embedding vector."""
        vector = self._compute_vector(text)
        return EmbeddingResult(vector=vector, dimension=self.dimension)
    
    def similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity."""
        if len(vec_a) != len(vec_b):
            raise ValueError("Vectors must have same dimension")
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
    
    def find_similar(self, query: str, candidates: List[str], top_k: int = 5) -> List[SimilarityMatch]:
        """Find similar items."""
        query_vec = self._compute_vector(query)
        matches = []
        for cand in candidates:
            cand_vec = self._compute_vector(cand)
            score = self.similarity(query_vec, cand_vec)
            matches.append((cand, score))
        matches.sort(key=lambda x: x[1], reverse=True)
        return [SimilarityMatch(item=c, score=s, rank=i+1) for i, (c, s) in enumerate(matches[:top_k])]
    
    def _compute_vector(self, text: str) -> List[float]:
        """Compute hash-based vector."""
        h = hashlib.sha256(text.encode()).digest()
        vec = [(b - 128) / 128.0 for b in h[:self.dimension]]
        norm = math.sqrt(sum(v * v for v in vec))
        return [v / norm for v in vec] if norm else vec


def compute_embedding(text: str, config: Optional[Dict] = None) -> EmbeddingResult:
    """Compute embedding for text."""
    return {class_name}(config).embed(text)
'''


def generate_scoring_module(name: str, ctx: dict) -> str:
    """Generate scoring module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Scoring Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ScoreResult:
    """Scoring result."""
    score: float
    confidence: float
    factors: Dict[str, float] = field(default_factory=dict)


class {class_name}:
    """Scorer for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.weights = self.config.get("weights", {{}})
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def score(self, data: Dict[str, Any]) -> ScoreResult:
        """Compute score for data."""
        factors = self._extract_factors(data)
        raw_score = self._compute_weighted(factors)
        confidence = self._compute_confidence(factors)
        return ScoreResult(score=max(0, min(1, raw_score)), confidence=confidence, factors=factors)
    
    def _extract_factors(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract scoring factors."""
        factors = {{}}
        for k, v in data.items():
            if isinstance(v, (int, float)):
                factors[k] = float(v)
            elif isinstance(v, str):
                factors[f"{{k}}_len"] = min(1.0, len(v) / 100)
        return factors
    
    def _compute_weighted(self, factors: Dict[str, float]) -> float:
        """Compute weighted score."""
        if not factors:
            return 0.5
        total_w = sum(self.weights.get(k, 1.0) for k in factors)
        weighted = sum(v * self.weights.get(k, 1.0) for k, v in factors.items())
        return weighted / total_w if total_w else 0.5
    
    def _compute_confidence(self, factors: Dict[str, float]) -> float:
        """Compute confidence."""
        return min(1.0, len(factors) / 5)


def compute_score(data: Dict[str, Any], config: Optional[Dict] = None) -> ScoreResult:
    """Compute score."""
    return {class_name}(config).score(data)
'''


def generate_state_update_module(name: str, ctx: dict) -> str:
    """Generate state update module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - State Update Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StateUpdate:
    """A state update."""
    key: str
    old_value: Any
    new_value: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class StateResult:
    """Result of state operation."""
    success: bool
    updates: List[StateUpdate] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)


class {class_name}:
    """State manager for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.state: Dict[str, Any] = {{}}
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def update(self, updates: Dict[str, Any]) -> StateResult:
        """Apply state updates."""
        applied = []
        for key, new_val in updates.items():
            old_val = self.state.get(key)
            self.state[key] = new_val
            applied.append(StateUpdate(key=key, old_value=old_val, new_value=new_val))
        return StateResult(success=True, updates=applied, state=self.state.copy())
    
    def merge(self, other: Dict[str, Any]) -> StateResult:
        """Merge state with another."""
        merged = {{**self.state, **other}}
        updates = [StateUpdate(k, self.state.get(k), v) for k, v in other.items()]
        self.state = merged
        return StateResult(success=True, updates=updates, state=self.state.copy())
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        return self.state.get(key, default)


def update_state(updates: Dict[str, Any], config: Optional[Dict] = None) -> StateResult:
    """Update state."""
    return {class_name}(config).update(updates)
'''


def generate_retrieval_module(name: str, ctx: dict) -> str:
    """Generate retrieval module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Retrieval Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Retrieval result."""
    items: List[Any]
    total: int
    query: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class {class_name}:
    """Retrieval engine for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.cache: Dict[str, Any] = {{}}
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def retrieve(self, query: str, filters: Optional[Dict] = None, limit: int = 10) -> RetrievalResult:
        """Retrieve items."""
        cache_key = f"{{query}}:{{filters}}:{{limit}}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        items = self._execute_query(query, filters, limit)
        result = RetrievalResult(items=items, total=len(items), query=query)
        self.cache[cache_key] = result
        return result
    
    def _execute_query(self, query: str, filters: Optional[Dict], limit: int) -> List[Any]:
        """Execute query."""
        return []


def retrieve(query: str, config: Optional[Dict] = None, **kwargs) -> RetrievalResult:
    """Retrieve items."""
    return {class_name}(config).retrieve(query, **kwargs)
'''


def generate_formatting_module(name: str, ctx: dict) -> str:
    """Generate formatting module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Formatting Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FormatResult:
    """Formatting result."""
    data: Any
    format_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class {class_name}:
    """Formatter for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.format_type = self.config.get("format", "default")
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def format(self, data: Any, target: Optional[str] = None) -> FormatResult:
        """Format data."""
        fmt = target or self.format_type
        transformed = self._transform(data)
        return FormatResult(data=transformed, format_type=fmt)
    
    def _transform(self, data: Any) -> Any:
        """Transform data."""
        if isinstance(data, str):
            return data.strip()
        return data


def format_data(data: Any, config: Optional[Dict] = None) -> FormatResult:
    """Format data."""
    return {class_name}(config).format(data)
'''


def generate_retry_module(name: str, ctx: dict) -> str:
    """Generate retry/fallback module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Retry/Fallback Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
import time
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetryResult:
    """Retry result."""
    success: bool
    attempts: int
    result: Any = None
    error: Optional[str] = None


class {class_name}:
    """Retry handler for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.max_retries = self.config.get("max_retries", 3)
        self.backoff = self.config.get("backoff", 1.0)
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def execute(self, func: Callable, *args, **kwargs) -> RetryResult:
        """Execute with retry."""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                return RetryResult(success=True, attempts=attempt + 1, result=result)
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {{attempt + 1}} failed: {{e}}")
                time.sleep(self.backoff * (attempt + 1))
        return RetryResult(success=False, attempts=self.max_retries, error=last_error)
    
    def fallback(self, primary: Callable, fallback: Callable, *args, **kwargs) -> Any:
        """Execute with fallback."""
        result = self.execute(primary, *args, **kwargs)
        if result.success:
            return result.result
        return fallback(*args, **kwargs)


def with_retry(func: Callable, config: Optional[Dict] = None) -> RetryResult:
    """Execute with retry."""
    return {class_name}(config).execute(func)
'''


def generate_execution_module(name: str, ctx: dict) -> str:
    """Generate execution module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Execution Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Execution result."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class {class_name}:
    """Executor for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.timeout = self.config.get("timeout", 30.0)
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def execute(self, action: str, params: Dict[str, Any]) -> ExecutionResult:
        """Execute action."""
        start = time.time()
        try:
            output = self._perform_action(action, params)
            return ExecutionResult(
                success=True,
                output=output,
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    def _perform_action(self, action: str, params: Dict[str, Any]) -> Any:
        """Perform the action."""
        logger.info(f"Executing {{action}} with {{params}}")
        return {{"action": action, "params": params, "status": "completed"}}


def execute(action: str, params: Dict[str, Any], config: Optional[Dict] = None) -> ExecutionResult:
    """Execute action."""
    return {class_name}(config).execute(action, params)
'''


def generate_diagnostics_module(name: str, ctx: dict) -> str:
    """Generate diagnostics module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Diagnostics Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticReport:
    """Diagnostic report."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    healthy: bool = True
    issues: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class {class_name}:
    """Diagnostics for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def diagnose(self, target: Any) -> DiagnosticReport:
        """Run diagnostics."""
        issues = []
        metrics = {{}}
        
        if target is None:
            issues.append("Target is null")
        elif isinstance(target, dict):
            metrics["field_count"] = len(target)
        elif isinstance(target, list):
            metrics["item_count"] = len(target)
        
        metrics["type"] = type(target).__name__
        return DiagnosticReport(healthy=len(issues) == 0, issues=issues, metrics=metrics)


def diagnose(target: Any, config: Optional[Dict] = None) -> DiagnosticReport:
    """Run diagnostics."""
    return {class_name}(config).diagnose(target)
'''


def generate_refinement_module(name: str, ctx: dict) -> str:
    """Generate refinement module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - Refinement Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RefinementResult:
    """Refinement result."""
    original: Any
    refined: Any
    changes: List[str]


class {class_name}:
    """Refiner for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.weights = self.config.get("weights", {{}})
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def refine(self, data: Any, adjustments: Optional[Dict] = None) -> RefinementResult:
        """Refine data."""
        changes = []
        refined = data
        
        if adjustments and isinstance(data, dict):
            refined = {{**data}}
            for key, adj in adjustments.items():
                if key in refined and isinstance(refined[key], (int, float)):
                    old = refined[key]
                    refined[key] = old * adj
                    changes.append(f"{{key}}: {{old}} -> {{refined[key]}}")
        
        return RefinementResult(original=data, refined=refined, changes=changes)


def refine(data: Any, adjustments: Optional[Dict] = None, config: Optional[Dict] = None) -> RefinementResult:
    """Refine data."""
    return {class_name}(config).refine(data, adjustments)
'''


def generate_generic_module(name: str, ctx: dict) -> str:
    """Generate generic module."""
    class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    return f'''"""
{name}.py - {ctx['domain'].title()} Operations Module

Domain: {ctx['domain']}
Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class OperationResult:
    """Operation result."""
    success: bool
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class {class_name}:
    """Operations handler for {ctx['domain']} domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def process(self, data: Any, context: Optional[Dict] = None) -> OperationResult:
        """Process data."""
        try:
            result = self._execute(data, context)
            return OperationResult(success=True, data=result)
        except Exception as e:
            logger.error(f"Processing failed: {{e}}")
            return OperationResult(success=False, metadata={{"error": str(e)}})
    
    def _execute(self, data: Any, context: Optional[Dict]) -> Any:
        """Execute processing."""
        return data


def process(data: Any, config: Optional[Dict] = None) -> OperationResult:
    """Process data."""
    return {class_name}(config).process(data)
'''


GENERATORS = {
    "policy": generate_policy_module,
    "embedding": generate_embedding_module,
    "scoring": generate_scoring_module,
    "state_update": generate_state_update_module,
    "retrieval": generate_retrieval_module,
    "formatting": generate_formatting_module,
    "retry": generate_retry_module,
    "execution": generate_execution_module,
    "diagnostics": generate_diagnostics_module,
    "refinement": generate_refinement_module,
    "generic": generate_generic_module,
}


def generate_init_file(package_path: str) -> str:
    """Generate __init__.py content."""
    return f'''"""
{package_path} package initialization.

Generated: {datetime.now().isoformat()}
"""

from __future__ import annotations

__all__: list[str] = []
'''


def main():
    """Generate apps structure from YAML."""
    with open(REPO / "unified_structure_subatomic.yaml", "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    
    apps_to_generate = {
        "apps_lic": ("09_apps/apps_lic", "lic"),
        "apps_rg": ("09_apps/apps_rg", "rg"),
    }
    
    total_created = 0
    total_skipped = 0
    
    for app_key, (dest_folder, app_type) in apps_to_generate.items():
        if app_key not in spec:
            print(f"SKIP: {app_key} not in YAML")
            continue
        
        paths = extract_yaml_paths(spec[app_key])
        dest_base = REPO / dest_folder
        ctx = get_domain_context("", app_type)
        
        print(f"\n{'='*60}")
        print(f"Generating {app_key} -> {dest_folder}")
        print(f"{'='*60}")
        
        # Create __init__.py files for all directories
        dirs_created = set()
        
        for path in paths:
            full_path = dest_base / path
            
            # Create parent directories and __init__.py
            for parent in list(full_path.parents):
                if parent not in dirs_created and str(parent).startswith(str(REPO)) and parent != REPO:
                    parent.mkdir(parents=True, exist_ok=True)
                    init_file = parent / "__init__.py"
                    if not init_file.exists():
                        try:
                            rel_parent = str(parent.relative_to(REPO)).replace("\\", "/")
                        except ValueError:
                            continue
                        init_file.write_text(generate_init_file(rel_parent), encoding="utf-8")
                    dirs_created.add(parent)
            
            # Generate module file
            if full_path.exists():
                total_skipped += 1
                continue
            
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            module_type = classify_module(path)
            generator = GENERATORS.get(module_type, generate_generic_module)
            name = full_path.stem
            
            content = generator(name, ctx)
            full_path.write_text(content, encoding="utf-8")
            total_created += 1
            print(f"  [{module_type.upper()}] {path}")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Files created: {total_created}")
    print(f"Files skipped (exist): {total_skipped}")


if __name__ == "__main__":
    main()
