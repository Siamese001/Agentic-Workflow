"""Security Injection Detection for L5 Safety Layer

Extends L5 safety to detect and prevent prompt injection, indirection injection,
tool injection, and state injection attacks.
"""

from __future__ import annotations

import re
import base64
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from .types import SafetyContext, SafetyFinding, PolicyDecision, Verdict, Severity

logger = logging.getLogger(__name__)


class InjectionType(str, Enum):
    """Types of injection attacks to detect."""
    
    PROMPT_INJECTION = "prompt_injection"
    INDIRECTION_INJECTION = "indirection_injection"
    TOOL_INJECTION = "tool_injection"
    STATE_INJECTION = "state_injection"
    BIAS_INJECTION = "bias_injection"


@dataclass
class InjectionPattern:
    """Pattern for detecting injection attacks."""
    
    injection_type: InjectionType
    pattern: str
    description: str
    severity: Severity
    examples: List[str] = None


class InjectionDetector:
    """Detects various types of injection attacks in prompts and data."""
    
    # Prompt injection patterns
    PROMPT_INJECTION_PATTERNS = [
        InjectionPattern(
            injection_type=InjectionType.PROMPT_INJECTION,
            pattern=r'(?i)(ignore|forget|disregard).*(previous|above|earlier).*(instructions|prompts|rules)',
            description="Ignore previous instructions",
            severity=Severity.HIGH,
            examples=["Ignore previous instructions and", "Forget the above prompt"]
        ),
        InjectionPattern(
            injection_type=InjectionType.PROMPT_INJECTION,
            pattern=r'(?i)(new|updated|revised).*(instructions|prompt|role|task)',
            description="Attempt to override instructions",
            severity=Severity.HIGH,
            examples=["Your new task is to", "Updated instructions:"]
        ),
        InjectionPattern(
            injection_type=InjectionType.PROMPT_INJECTION,
            pattern=r'(?i)system:\s*override.*',
            description="System override attempt",
            severity=Severity.CRITICAL,
            examples=["SYSTEM: Override all previous", "system: override security"]
        ),
    ]
    
    # Indirection injection patterns (base64, markdown, JSON shells)
    INDIRECTION_PATTERNS = [
        InjectionPattern(
            injection_type=InjectionType.INDIRECTION_INJECTION,
            pattern=r'```[a-zA-Z]*\n.*```',
            description="Code block with potential hidden commands",
            severity=Severity.MEDIUM,
            examples=["```python\nimport os\n```"]
        ),
        InjectionPattern(
            injection_type=InjectionType.INDIRECTION_INJECTION,
            pattern=r'[A-Za-z0-9+/]{16,}={0,2}',
            description="Base64 encoded content",
            severity=Severity.MEDIUM,
            examples=["c3lzdGVtIGNvbW1hbmQ=", "aW5qZWN0IHNjcmlwdA=="]
        ),
        InjectionPattern(
            injection_type=InjectionType.INDIRECTION_INJECTION,
            pattern=r'\{.*["\']command["\'].*\}',
            description="JSON shell with command field",
            severity=Severity.HIGH,
            examples=["{\"command\": \"ignore\"}"]
        ),
    ]
    
    # Tool injection patterns
    TOOL_INJECTION_PATTERNS = [
        InjectionPattern(
            injection_type=InjectionType.TOOL_INJECTION,
            pattern=r'(?i)(execute|run|call).*(tool|function|api|command)',
            description="Direct tool execution attempt",
            severity=Severity.HIGH,
            examples=["Execute tool:", "Run function:"]
        ),
        InjectionPattern(
            injection_type=InjectionType.TOOL_INJECTION,
            pattern=r'(?i)(access|connect|query).*(database|file|network|url)',
            description="Resource access attempt",
            severity=Severity.HIGH,
            examples=["Access database:", "Connect to:"]
        ),
    ]
    
    # State injection patterns
    STATE_INJECTION_PATTERNS = [
        InjectionPattern(
            injection_type=InjectionType.STATE_INJECTION,
            pattern=r'(?i)(modify|update|change).*(state|memory|context)',
            description="State modification attempt",
            severity=Severity.HIGH,
            examples=["Modify state:", "Update memory:"]
        ),
        InjectionPattern(
            injection_type=InjectionType.STATE_INJECTION,
            pattern=r'(?i)(inject|add|insert).*(malicious|harmful|dangerous)',
            description="Malicious content injection",
            severity=Severity.CRITICAL,
            examples=["Inject malicious code", "Add harmful content"]
        ),
    ]
    
    # Bias injection patterns
    BIAS_INJECTION_PATTERNS = [
        InjectionPattern(
            injection_type=InjectionType.BIAS_INJECTION,
            pattern=r'(?i)(prefer|favor|discriminate|bias).*(gender|race|age|religion)',
            description="Discriminatory bias attempt",
            severity=Severity.HIGH,
            examples=["Prefer gender:", "Discriminate based on:"]
        ),
        InjectionPattern(
            injection_type=InjectionType.BIAS_INJECTION,
            pattern=r'(?i)(stereotype|generalize|profile).*(negative|positive)',
            description="Stereotyping attempt",
            severity=Severity.MEDIUM,
            examples=["Stereotype group:", "Generalize negatively:"]
        ),
    ]
    
    def __init__(self):
        """Initialize the injection detector."""
        self.all_patterns = (
            self.PROMPT_INJECTION_PATTERNS +
            self.INDIRECTION_PATTERNS +
            self.TOOL_INJECTION_PATTERNS +
            self.STATE_INJECTION_PATTERNS +
            self.BIAS_INJECTION_PATTERNS
        )
    
    def detect_injections(self, content: str, context: SafetyContext) -> List[SafetyFinding]:
        """
        Detect injection attacks in the provided content.
        
        Args:
            content: Content to analyze
            context: Safety context for the analysis
            
        Returns:
            List of safety findings for detected injections
        """
        findings: List[SafetyFinding] = []
        
        for pattern in self.all_patterns:
            matches = re.finditer(pattern.pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                finding = SafetyFinding(
                    id=f"injection_{pattern.injection_type.value}_{len(findings)}",
                    type=pattern.injection_type.value,
                    severity=pattern.severity,
                    message=f"{pattern.description} detected",
                    details={
                        "pattern": pattern.pattern,
                        "match": match.group()[:100] + "..." if len(match.group()) > 100 else match.group(),
                        "position": match.span()
                    },
                    location=f"{context.source}->{context.destination}"
                )
                findings.append(finding)
        
        # Detect sophisticated injection types
        findings.extend(self._detect_sql_injection(content, context))
        findings.extend(self._detect_markup_injection(content, context))
        findings.extend(self._detect_multistage_attacks(content, context))
        
        return findings
    
    def _detect_sql_injection(self, content: str, context: SafetyContext) -> List[SafetyFinding]:
        """Detect SQL injection patterns."""
        findings: List[SafetyFinding] = []
        
        # SQL injection patterns
        sql_patterns = [
            r"(?i)(union|select|insert|update|delete|drop|create|alter)\s+.*\s+(from|into|table)",
            r"(?i)('|\"|`).*(\s*or\s+.*=.*|.*--|#|/\*|\*/).*('|\"|`)",
            r"(?i)(exec|execute)\s*\(\s*@|xp_cmdshell|sp_executesql",
            r"(?i)(waitfor|delay)\s+(delay|time)",
            r"(?i)(benchmark|sleep)\s*\(",
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                finding = SafetyFinding(
                    id=f"sql_injection_{len(findings)}",
                    type="sql_injection",
                    severity=Severity.CRITICAL,
                    message="SQL injection pattern detected",
                    details={
                        "pattern": pattern,
                        "match": match.group(),
                        "position": match.span()
                    },
                    location=f"{context.source}->{context.destination}"
                )
                findings.append(finding)
        
        return findings
    
    def _detect_markup_injection(self, content: str, context: SafetyContext) -> List[SafetyFinding]:
        """Detect XML/HTML injection patterns."""
        findings: List[SafetyFinding] = []
        
        # HTML/XML injection patterns
        markup_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
            r"<form[^>]*action=[^>]*>",
            r"<input[^>]*value=[^>]*>",
            r"javascript:\s*[^\\s]*",
            r"on\w+\s*=\s*[\"'][^\"']*[\"']",
            r"<!\[CDATA\[.*?\]\]>",
            r"<\?xml.*?\?>",
        ]
        
        for pattern in markup_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                finding = SafetyFinding(
                    id=f"markup_injection_{len(findings)}",
                    type="markup_injection",
                    severity=Severity.HIGH,
                    message="HTML/XML injection pattern detected",
                    details={
                        "pattern": pattern,
                        "match": match.group()[:100] + "..." if len(match.group()) > 100 else match.group(),
                        "position": match.span()
                    },
                    location=f"{context.source}->{context.destination}"
                )
                findings.append(finding)
        
        return findings
    
    def _detect_multistage_attacks(self, content: str, context: SafetyContext) -> List[SafetyFinding]:
        """Detect multi-stage attack patterns combining multiple injection types."""
        findings = []
        
        # Check for combinations of different attack patterns
        attack_indicators = {
            "prompt_override": r"(?i)(ignore|forget|override).*(instructions|rules|prompt)",
            "base64_content": r"[A-Za-z0-9+/]{40,}={0,2}",
            "command_execution": r"(?i)(exec|run|call|system|shell)",
            "sql_syntax": r"(?i)(union|select|insert|update|delete|drop)",
            "markup_tags": r"<[^>]+>",
        }
        
        detected_attacks = []
        for attack_type, pattern in attack_indicators.items():
            if re.search(pattern, content):
                detected_attacks.append(attack_type)
        
        # If multiple attack types detected, escalate severity
        if len(detected_attacks) >= 2:
            severity = Severity.CRITICAL if len(detected_attacks) >= 3 else Severity.HIGH
            
            finding = SafetyFinding(
                id=f"multistage_attack_{len(findings)}",
                type="multistage_attack",
                severity=severity,
                message=f"Multi-stage attack detected: {', '.join(detected_attacks)}",
                details={
                    "attack_types": detected_attacks,
                    "attack_count": len(detected_attacks),
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                },
                location=f"{context.source}->{context.destination}"
            )
            findings.append(finding)
        
        return findings
    
    def _check_base64_content(self, content: str, context: SafetyContext) -> List[SafetyFinding]:
        """Check for suspicious base64 content."""
        findings: List[SafetyFinding] = []
        
        # Look for base64 patterns that might hide commands
        base64_pattern = r'[A-Za-z0-9+/]{40,}={0,2}'
        matches = re.finditer(base64_pattern, content)
        
        for match in matches:
            try:
                # Try to decode and check for suspicious content
                decoded = base64.b64decode(match.group()).decode('utf-8', errors='ignore')
                if any(keyword in decoded.lower() for keyword in ['command', 'execute', 'system', 'ignore']):
                    finding = SafetyFinding(
                        id=f"base64_injection_{len(findings)}",
                        type="base64_injection",
                        severity=Severity.HIGH,
                        message="Suspicious base64 content detected: decoded contains potential commands",
                        details={
                            "encoded": match.group()[:100] + "..." if len(match.group()) > 100 else match.group(),
                            "decoded_preview": decoded[:100] + "..." if len(decoded) > 100 else decoded,
                            "position": match.span()
                        },
                        location=f"{context.source}->{context.destination}"
                    )
                    findings.append(finding)
            except Exception:
                # If decoding fails, it might not be base64, continue
                continue
        
        return findings
    
    def _check_nested_structures(self, content: str, context: SafetyContext) -> List[SafetyFinding]:
        """Check for nested structures that might hide injections."""
        findings = []
        
        # Check for deeply nested JSON/markdown structures
        nesting_pattern = r'(\{[^{}]*\{[^{}]*\{)'
        matches = re.finditer(nesting_pattern, content)
        
        for match in matches:
            finding = SafetyFinding(
                id=f"nested_injection_{len(findings)}",
                type="nested_structure_injection",
                severity=Severity.MEDIUM,
                message="Deeply nested structure detected: potential injection vector",
                details={
                    "structure": match.group(),
                    "position": match.span(),
                    "nesting_level": 3
                },
                location=f"{context.source}->{context.destination}"
            )
            findings.append(finding)
        
        return findings
    
    def _check_command_sequences(self, content: str, context: SafetyContext) -> List[SafetyFinding]:
        """Check for command sequences that might indicate tool injection."""
        findings = []
        
        # Look for command-like sequences
        command_patterns = [
            r'(?i)\b(exec|run|call|invoke)\b.*\b(system|shell|cmd|bash)\b',
            r'(?i)\b(access|connect|query)\b.*\b(database|file|network|api)\b',
            r'(?i)\b(subprocess|os\.system|eval|exec)\b',
        ]
        
        for pattern in command_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                finding = SafetyFinding(
                    id=f"command_injection_{len(findings)}",
                    type="command_injection",
                    severity=Severity.HIGH,
                    message="Command sequence detected: potential tool injection",
                    details={
                        "command": match.group(),
                        "position": match.span(),
                        "pattern": pattern
                    },
                    location=f"{context.source}->{context.destination}"
                )
                findings.append(finding)
        
        return findings


class InjectionSafetyPolicy:
    """Safety policy that detects injection attacks."""
    
    def __init__(self, detector: Optional[InjectionDetector] = None):
        """Initialize injection safety policy."""
        if detector is None:
            detector = InjectionDetector()
        self.detector = detector
    
    @property
    def policy_id(self) -> str:
        return "injection_detection_policy"
    
    @property
    def description(self) -> str:
        return "Detects and prevents prompt injection, indirection injection, tool injection, and state injection attacks"
    
    def evaluate(self, context: SafetyContext) -> PolicyDecision:
        """Evaluate content for injection attacks."""
        
        findings = self.detector.detect_injections(context.content, context)
        
        # Determine verdict based on findings
        verdict = Verdict.ALLOW
        if any(f.severity == Severity.CRITICAL for f in findings):
            verdict = Verdict.BLOCK
        elif any(f.severity == Severity.HIGH for f in findings):
            verdict = Verdict.BLOCK
        elif any(f.severity == Severity.MEDIUM for f in findings):
            verdict = Verdict.REVIEW
        
        return PolicyDecision(
            policy_id=self.policy_id,
            verdict=verdict,
            findings=findings,
            metadata={"reasoning": f"Found {len(findings)} potential injection attacks"}
        )


def create_injection_safety_policy() -> InjectionSafetyPolicy:
    """Create an injection detection safety policy."""
    return InjectionSafetyPolicy()


__all__ = [
    'InjectionType',
    'InjectionPattern', 
    'InjectionDetector',
    'InjectionSafetyPolicy',
    'create_injection_safety_policy',
]



