import re


@dataclass
class ContentCleanlinessValidatorAgent(SubatomicTestingMixin, MCPHardenedMixin, HealerMixin):
    """
    Forbidden verbs and weak language detection
    FEATURE 3.1 and 3.2 from SUPREME_SPELL
    """

    FORBIDDEN_VERBS = [
        "spearheaded",
        "leveraged",
        "utilized",
        "facilitated",
        "orchestrated",
        "championed",
        "pioneered",
        "revolutionized",
        "transformed",
        "optimized",
        "enhanced",
        "streamlined",
        "synergized",
        "enabled",
        "empowered",
        "drove",
        "drive",
    ]
    MAX_VIOLATIONS = 1

    FILLER_PATTERNS = [
        r"(?i)\bi hope\b",
        r"(?i)\bhope (this|you) (finds|are|don't)",
        r"(?i)\bi (wanted|would like) to (reach|connect|discuss|share)",
        r"(?i)\bi was wondering if",
        r"(?i)\bperhaps (we|you) could",
        r"(?i)\bif you('re| are) interested",
        r"(?i)\bjust (wanted|reaching|following)",
    ]

    def detect_forbidden_verbs(self, text: str) -> list[str]:
        """Find forbidden verbs in message text"""
        text_lower = text.lower()
        found = []

        for verb in self.FORBIDDEN_VERBS:
            if verb in text_lower:
                found.append(verb)

        return found

    def detect_fillers(self, text: str) -> list[tuple[str, str]]:
        """Find filler phrases in message"""
        found = []

        for pattern in self.FILLER_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    match_text = (
                        match
                        if isinstance(match, str)
                        else " ".join(match)
                        if isinstance(match, tuple)
                        else str(match)
                    )
                    found.append((pattern, match_text))

        return found

    def validate_verbs(self, message: str) -> tuple[bool, str]:
        """Validate no excessive forbidden verbs"""
        forbidden = self.detect_forbidden_verbs(message)

        if len(forbidden) > self.MAX_VIOLATIONS:
            return False, f"Found {len(forbidden)} forbidden verbs: {', '.join(forbidden[:3])}"

        return True, ""

    def validate_fillers(self, message: str) -> tuple[bool, str]:
        """Validate message is direct and confident"""
        fillers = self.detect_fillers(message)

        if fillers:
            filler_texts = [f[1] for f in fillers]
            return False, f"Found filler phrases: {', '.join(filler_texts[:3])}"
        return True, ""

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, Any]:
        """Autonomous healing with proper invocation chain."""
        super().heal_repository(dry_run=dry_run, execute=execute, **kwargs)
        return {"violations": 0, "fixed": 0, "errors": 0}


# File: validation.py
# Description: Validation agents, rules, and utilities for the LIC workflow.

__version__ = "11.10"

# import scripts.validation.check_canonical_structure  # TODO: Replace with sovereign equivalent
# from scripts.utilities.FormatScriptsContext import TfidfVectorizer  # TODO: Replace with sovereign equivalent

# ============================================================================
# NEW v11.6: GLOBAL ERROR CODE REGISTRY (GAP 6.1)
# ============================================================================


class ErrorCodeRegistry:
    """Centralized error codes with remediation guidance"""

    CODES = {
        "LIC-E001": {
            "Severity": "CRITICAL",
            "description": "Placeholder detected in generated message",
            "remediation": "Regenerate with explicit anti-placeholder constraint",
        },
        "LIC-E002": {
            "Severity": "CRITICAL",
            "description": "Per-Claim confidence below threshold (0.70)",
            "remediation": "Add more RAG sources or remove low-confidence Claim",
        },
        "LIC-E003": {
            "Severity": "CRITICAL",
            "description": "Hallucinated Claim without supporting evidence",
            "remediation": "Remove Claim or add supporting RAG evidence",
        },
        "LIC-E004": {
            "Severity": "HIGH",
            "description": "Message too similar to previous message (>0.85)",
            "remediation": "Increase temperature or add diversity constraint",
        },
        "LIC-E005": {
            "Severity": "HIGH",
            "description": "Job title not in first 50 words",
            "remediation": "Regenerate with job title positioning constraint",
        },
        "LIC-E006": {
            "Severity": "HIGH",
            "description": "Company name misspelled",
            "remediation": "Use exact company name from profile",
        },
        "LIC-E007": {
            "Severity": "HIGH",
            "description": "Non-ASCII characters detected",
            "remediation": "Replace Unicode with ASCII equivalents",
        },
        "LIC-E008": {
            "Severity": "MEDIUM",
            "description": "Forbidden corporate verbs detected",
            "remediation": "Regenerate avoiding: spearheaded, leveraged, etc.",
        },
        "LIC-E009": {
            "Severity": "MEDIUM",
            "description": "Weak filler phrases detected",
            "remediation": "Remove: 'I hope', 'I wanted to', 'just reaching out'",
        },
        "LIC-E010": {
            "Severity": "HIGH",
            "description": "Metric lacks supporting keyword context from RAG",
            "remediation": "Add RAG evidence keywords around Metric or remove Metric",
        },
        "LIC-E011": {
            "Severity": "HIGH",
            "description": "Signal quality score below threshold (0.70)",
            "remediation": "Trigger RAG reflexion for more research",
        },
        "LIC-E012": {
            "Severity": "CRITICAL",
            "description": "Circuit breaker OPEN - API unavailable",
            "remediation": "Wait for circuit breaker timeout or check API",
        },
        "LIC-E013": {
            "Severity": "CRITICAL",
            "description": "Constraint pre-flight check failed",
            "remediation": "Adjust constraints or change Route",
        },
    }

    @classmethod
    def get_error(cls, code: str) -> dict[str, str]:
        return cls.CODES.get(
            code,
            {
                "Severity": "UNKNOWN",
                "description": "Unknown error",
                "remediation": "Contact support",
            },
        )


# ============================================================================
# NEW v11.6: CONSTRAINT FEASIBILITY CHECKER (FEATURE 2.1)
# ============================================================================


class ConstraintFeasibilityChecker:
    """
    Pre-flight check for constraint satisfaction
    FEATURE 2.1 from SUPREME_SPELL
    """

    def check_feasibility(
        self, Route: models.Route, Archetype: models.Archetype, required_elements: list[str]
    ) -> tuple[bool, str]:
        """
        Pre-flight check: can we satisfy these constraints?
        (Simplified version - full implementation would use LLM)
        """
        # This function needs access to ConfigRegistry, but to avoid circular
        # imports, we'll use hardcoded fallbacks if the import fails.
        try:
            constraints = CONFIG_REGISTRY.get_route_constraints(Route, Archetype)
        except ImportError:
            constraints = {"word_target": 200, "word_range": (150, 250), "Route": Route}

        # Simple heuristic: check if number of required elements fits in word budget
        word_budget = constraints.get("word_target", constraints["word_range"][1])
        words_per_element = word_budget // (len(required_elements) + 2)  # +2 for greeting/signature

        # CONNECTION_REQ requires stricter checking (more constrained format)
        min_words_per_element = 8 if Route.value == "CONNECTION_REQ" else 5

        if words_per_element < min_words_per_element:
            return (
                False,
                f"Too many required elements ({len(required_elements)}) for {Route.value} word budget ({word_budget})",
            )

        return True, "Constraints are feasible"


# ============================================================================
# NEW v11.6: CONTENT CLEANLINESS VALIDATORS (FEATURE 3.1, 3.2, 3.3)
# ============================================================================


class ContentCleanlinessValidatorAgent:
    """
    Forbidden verbs and weak language detection
    FEATURE 3.1 and 3.2 from SUPREME_SPELL
    """

    FORBIDDEN_VERBS = [
        "spearheaded",
        "leveraged",
        "utilized",
        "facilitated",
        "orchestrated",
        "championed",
        "pioneered",
        "revolutionized",
        "transformed",
        "optimized",
        "enhanced",
        "streamlined",
        "synergized",
        "enabled",
        "empowered",
        "drove",
        "drive",
    ]
    MAX_VIOLATIONS = 1

    FILLER_PATTERNS = [
        r"(?i)\bi hope\b",
        r"(?i)\bhope (this|you) (finds|are|don't)",
        r"(?i)\bi (wanted|would like) to (reach|connect|discuss|share)",
        r"(?i)\bi was wondering if",
        r"(?i)\bperhaps (we|you) could",
        r"(?i)\bif you('re| are) interested",
        r"(?i)\bjust (wanted|reaching|following)",
    ]

    def detect_forbidden_verbs(self, text: str) -> list[str]:
        """Find forbidden verbs in message text"""
        text_lower = text.lower()
        found = []

        for verb in self.FORBIDDEN_VERBS:
            if verb in text_lower:
                found.append(verb)

        return found

    def detect_fillers(self, text: str) -> list[tuple[str, str]]:
        """Find filler phrases in message"""
        found = []

        for pattern in self.FILLER_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    match_text = (
                        match
                        if isinstance(match, str)
                        else " ".join(match)
                        if isinstance(match, tuple)
                        else str(match)
                    )
                    found.append((pattern, match_text))

        return found

    def validate_verbs(self, message: str) -> tuple[bool, str]:
        """Validate no excessive forbidden verbs"""
        forbidden = self.detect_forbidden_verbs(message)

        if len(forbidden) > self.MAX_VIOLATIONS:
            return False, f"Found {len(forbidden)} forbidden verbs: {', '.join(forbidden[:3])}"

        return True, ""

    def validate_fillers(self, message: str) -> tuple[bool, str]:
        """Validate message is direct and confident"""
        fillers = self.detect_fillers(message)

        if fillers:
            filler_texts = [f[1] for f in fillers]
            return False, f"Found {len(fillers)} filler phrases: {', '.join(filler_texts[:3])}"

        return True, ""

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()


# ============================================================================
# NEW v11.6: MESSAGE DIVERSITY VALIDATOR (FEATURE 1.3)
# ============================================================================


# ============================================================================
# NEW v11.6: ASCII CHARACTER ENFORCER (GAP 1.10)
# ============================================================================


# ============================================================================
# S6: VALIDATION AGENT
# ============================================================================
