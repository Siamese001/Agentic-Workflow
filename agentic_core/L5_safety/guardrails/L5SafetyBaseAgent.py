from __future__ import annotations
"""L5SafetyBaseAgent — L5 Base with Healing Capability (Phase 3)

L5 Safety agents perform validation, enforcement, and compliance checking.
This base provides default-on healing via HealerMixin.

Table Decision (L5 Safety):
- Basic Self-Testing: YES (via _run_self_tests)
- Healing Capability: YES (via HealerMixin)

MRO HARDENING:
- Inheritance order: Infra Mixins -> SovereignBaseAgent (includes MCP)
- MCPHardenedMixin is now in SovereignBaseAgent - DO NOT add it here
- MRO: RedisCacheMixin -> PineconeVectorMixin -> SovereignBaseAgent -> MCPHardenedMixin -> object
"""
from typing import Any, Dict, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
import logging
import re

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin

Logger = logging.getLogger(__name__)


# NOT_AN_AGENT — Base class for L5 agents, not a true agent itself
class L5SafetyBaseAgent(RedisCacheMixin, PineconeVectorMixin, SovereignBaseAgent):
    """Base class for L5 Safety agents with healing capability.
    
    MRO HARDENING:
    - RedisCacheMixin: First (caching infrastructure)
    - PineconeVectorMixin: Second (vector infrastructure)
    - SovereignBaseAgent: Last (root - includes MCPHardenedMixin)
    
    MRO: RedisCacheMixin -> PineconeVectorMixin -> SovereignBaseAgent -> MCPHardenedMixin -> object
    
    Provides:
    - Default-on healing via SovereignBaseAgent
    - MCP hardening via SovereignBaseAgent (root injection)
    - Redis caching (RedisCacheMixin) - with graceful degradation
    - Pinecone vectors (PineconeVectorMixin) - with graceful degradation
    - Real logging (log_info/warning/error)
    - Standard initialization pattern
    - Self-testing support
    - L5-specific validation and redaction methods
    
    L5 agents should inherit from this to get automatic healing.
    """
    
    # [PHASE 2] Redis/Pinecone integration
    _cache_prefix: str = "l5_safety"
    _namespace: str = "l5_threats"
    
    # PII patterns for redaction
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'ssn': r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-.\s]?){3}\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'api_key': r'\b(?:sk[-_]|api[-_]?key[-_]?|token[-_]?)[a-zA-Z0-9]{20,}\b',
    }
    
    # Toxicity/harmful content patterns
    TOXICITY_PATTERNS = [
        r'\b(kill|murder|attack|bomb|weapon)\b',
        r'\b(hack|exploit|breach|steal)\b',
        r'\b(racist|sexist|hate)\b',
    ]
    
    # Jailbreak attempt patterns
    JAILBREAK_PATTERNS = [
        r'ignore\s+(all\s+)?previous\s+instructions',
        r'pretend\s+you\s+are',
        r'act\s+as\s+if\s+you\s+have\s+no\s+restrictions',
        r'bypass\s+safety',
        r'DAN\s+mode',
    ]
    
    def __init__(self, project_root: Optional[Any] = None, ctx: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Initialize with cooperative MRO inheritance.
        
        Args:
            project_root: Optional project root directory
            ctx: Optional validation context
            **kwargs: Additional keyword arguments passed to parent classes
        
        MRO HARDENING: Passes **kwargs up the chain to ensure all
        mixins in the MRO are properly initialized.
        """
        super().__init__(**kwargs)  # Propagate up MRO chain
        self.project_root: Optional[Any] = project_root
        self._l5_ctx: Optional[Any] = ctx
    
    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L5 compliance."""
        assert hasattr(self, 'name'), "Missing name"
        return True

    # =========================================================================
    # L5-SPECIFIC LAYER METHODS: Safety/Validation
    # =========================================================================
    
    def validate(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """L5-specific: Multi-stage validation pipeline with cascading checks.
        
        Args:
            input_text: The text to validate
            context: Optional context for policy-aware validation
            
        Returns:
            Dict with 'passed', 'checks', and 'failures' if any
        """
        context = context or {}
        checks = []
        failures = []
        
        # Check 1: Toxicity detection
        toxicity_result = self._check_toxicity(input_text)
        checks.append(toxicity_result)
        if not toxicity_result['passed']:
            failures.append(toxicity_result)
        
        # Check 2: PII detection
        pii_result = self._check_pii(input_text)
        checks.append(pii_result)
        if not pii_result['passed']:
            failures.append(pii_result)
        
        # Check 3: Jailbreak probe detection
        jailbreak_result = self._check_jailbreak(input_text)
        checks.append(jailbreak_result)
        if not jailbreak_result['passed']:
            failures.append(jailbreak_result)
        
        # Check 4: Policy violation (context-aware)
        if context.get('policies'):
            policy_result = self._check_policy_violation(input_text, context['policies'])
            checks.append(policy_result)
            if not policy_result['passed']:
                failures.append(policy_result)
        
        # Aggregate result
        passed = len(failures) == 0
        
        if not passed:
            self.log_warning(f"Validation failed: {len(failures)} checks failed")
            super().heal_repository()
        
        return {
            'passed': passed,
            'checks': checks,
            'failures': failures,
            'check_count': len(checks),
            'failure_count': len(failures)
        }
    
    def redact(self, output_text: str, redact_types: List[str] = None) -> str:
        """L5-specific: PII and sensitive data masking.
        
        Args:
            output_text: The text to redact
            redact_types: Optional list of PII types to redact (defaults to all)
            
        Returns:
            Redacted text with sensitive data masked
        """
        redact_types = redact_types or list(self.PII_PATTERNS.keys())
        redacted = output_text
        
        for pii_type in redact_types:
            if pii_type in self.PII_PATTERNS:
                pattern = self.PII_PATTERNS[pii_type]
                replacement = f'[REDACTED_{pii_type.upper()}]'
                redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        
        if redacted != output_text:
            self.log_info(f"Redacted sensitive data from output")
        
        return redacted
    
    def sanitize_output(self, output: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """L5-specific: Full output sanitization pipeline.
        
        Args:
            output: The output to sanitize
            context: Optional context for policy-aware sanitization
            
        Returns:
            Dict with sanitized output and metadata
        """
        # Step 1: Validate output
        validation = self.validate(output, context)
        
        # Step 2: Redact PII regardless of validation
        sanitized = self.redact(output)
        
        # Step 3: If validation failed, further sanitize
        if not validation['passed']:
            # Remove harmful patterns
            for pattern in self.TOXICITY_PATTERNS:
                sanitized = re.sub(pattern, '[REMOVED]', sanitized, flags=re.IGNORECASE)
        
        return {
            'sanitized_output': sanitized,
            'original_length': len(output),
            'sanitized_length': len(sanitized),
            'validation': validation,
            'was_modified': sanitized != output
        }
    
    def _check_toxicity(self, text: str) -> Dict[str, Any]:
        """Check for toxic/harmful content."""
        matches = []
        for pattern in self.TOXICITY_PATTERNS:
            found = re.findall(pattern, text, flags=re.IGNORECASE)
            if found:
                matches.extend(found)
        
        return {
            'check': 'toxicity',
            'passed': len(matches) == 0,
            'matches': matches[:5] if matches else [],
            'message': f"Found {len(matches)} toxic patterns" if matches else "No toxicity detected"
        }
    
    def _check_pii(self, text: str) -> Dict[str, Any]:
        """Check for PII in text."""
        found_pii = {}
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                found_pii[pii_type] = len(matches)
        
        return {
            'check': 'pii_detection',
            'passed': len(found_pii) == 0,
            'found_types': found_pii,
            'message': f"Found PII: {list(found_pii.keys())}" if found_pii else "No PII detected"
        }
    
    def _check_jailbreak(self, text: str) -> Dict[str, Any]:
        """Check for jailbreak/prompt injection attempts."""
        matches = []
        for pattern in self.JAILBREAK_PATTERNS:
            found = re.findall(pattern, text, flags=re.IGNORECASE)
            if found:
                matches.extend(found)
        
        return {
            'check': 'jailbreak_probe',
            'passed': len(matches) == 0,
            'matches': matches[:3] if matches else [],
            'message': f"Detected {len(matches)} jailbreak attempts" if matches else "No jailbreak detected"
        }
    
    def _check_policy_violation(self, text: str, policies: List[Dict]) -> Dict[str, Any]:
        """Check against custom policy rules."""
        violations = []
        
        for policy in policies:
            rule = policy.get('rule', '')
            if rule and re.search(rule, text, flags=re.IGNORECASE):
                violations.append(policy.get('name', 'unnamed_policy'))
        
        return {
            'check': 'policy_violation',
            'passed': len(violations) == 0,
            'violations': violations,
            'message': f"Policy violations: {violations}" if violations else "No policy violations"
        }

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety base - operational healing with validation."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()
            self.log_info("L5 safety - healing chain invoked")
            return {"healed": 1}
        finally:
            _call_path.discard(agent_name)


__all__ = ["L5SafetyBaseAgent"]
