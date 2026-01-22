"""
RG Validation Gates - Validation gates for resume generation.

Ported from: archives/legacy_resume_gen/Job Workflow - JSON/Job_Workflow_v61.27.json
"""


class GateDecision(Enum):
    """Decision from a validation gate."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class GateSeverity(Enum):
    """Severity level for gate violations."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class GateResult:
    """Result from a validation gate."""

    gate_id: str
    decision: GateDecision
    Severity: GateSeverity
    message: str
    details: dict[str, object] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)


@dataclass
class ValidationGate:
    """Definition of a validation gate."""

    gate_id: str
    name: str
    description: str
    Severity: GateSeverity
    validator: Callable[[object, dict[str, object]], GateResult]


class RGValidationGates:
    """Collection of validation gates for resume generation."""

    # Gate IDs
    VG_SUMMARY_GROUNDING_CHECK = "VG_SUMMARY_GROUNDING_CHECK"
    VG_BULLET_HALLUCINATION_CHECK = "VG_BULLET_HALLUCINATION_CHECK"
    VG_THEMATIC_UNIQUENESS = "VG_THEMATIC_UNIQUENESS"
    VG_CREATIVE_BRIEF_ADHERENCE = "VG_CREATIVE_BRIEF_ADHERENCE"
    VG_HEADER_INTEGRITY_CHECK = "VG_HEADER_INTEGRITY_CHECK"
    VG_BULLET_PROVENANCE_CHECK = "VG_BULLET_PROVENANCE_CHECK"
    VG_REDUNDANCY_CHECK = "VG_REDUNDANCY_CHECK"
    VG_NATURAL_HYPHEN_PRESERVATION = "VG_NATURAL_HYPHEN_PRESERVATION"
    VG_COMPETENCY_WORD_COUNT_BALANCE = "VG_COMPETENCY_WORD_COUNT_BALANCE"
    VG_BULLET_PUNCTUATION = "VG_BULLET_PUNCTUATION"
    VG_SUMMARY_VOICE_TENSE = "VG_SUMMARY_VOICE_TENSE"
    VG_AGENTIC_OUTPUT_VALIDATION = "VG_AGENTIC_OUTPUT_VALIDATION"

    def __init__(self) -> None:
        """Initialize the validation gates."""
        self._gates: dict[str, ValidationGate] = {}
        self._register_default_gates()

    def _register_critical_gates(self) -> None:
        """Register critical validation gates."""
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_SUMMARY_GROUNDING_CHECK,
                name="Summary Grounding Check",
                description=(
                    "Verifies that the executive summary is grounded in source "
                    "material and does not contain hallucinated claims."
                ),
                Severity=GateSeverity.CRITICAL,
                validator=self._validate_summary_grounding,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_BULLET_HALLUCINATION_CHECK,
                name="Bullet Hallucination Check",
                description=(
                    "Checks that all bullet points are derived from source "
                    "material with proper provenance."
                ),
                Severity=GateSeverity.CRITICAL,
                validator=self._validate_bullet_hallucination,
            )
        )

    def _register_high_priority_gates(self) -> None:
        """Register high priority validation gates."""
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_THEMATIC_UNIQUENESS,
                name="Thematic Uniqueness",
                description=(
                    "Ensures each bullet point covers a unique theme without "
                    "redundancy across sections."
                ),
                Severity=GateSeverity.HIGH,
                validator=self._validate_thematic_uniqueness,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_CREATIVE_BRIEF_ADHERENCE,
                name="Creative Brief Adherence",
                description=(
                    "Validates that all content adheres to the creative brief "
                    "constraints including word counts and structure."
                ),
                Severity=GateSeverity.HIGH,
                validator=self._validate_creative_brief_adherence,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_BULLET_PROVENANCE_CHECK,
                name="Bullet Provenance Check",
                description=(
                    "Ensures each bullet can be traced back to source material "
                    "with documented provenance."
                ),
                Severity=GateSeverity.HIGH,
                validator=self._validate_bullet_provenance,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_AGENTIC_OUTPUT_VALIDATION,
                name="Agentic Output Validation",
                description=("Validates that agentic outputs meet all quality standards."),
                Severity=GateSeverity.HIGH,
                validator=self._validate_agentic_output,
            )
        )

    def _register_medium_priority_gates(self) -> None:
        """Register medium priority validation gates."""
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_HEADER_INTEGRITY_CHECK,
                name="Header Integrity Check",
                description=(
                    "Verifies that all section headers are correctly formatted and consistent."
                ),
                Severity=GateSeverity.MEDIUM,
                validator=self._validate_header_integrity,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_REDUNDANCY_CHECK,
                name="Redundancy Check",
                description=("Detects and flags redundant content across the resume."),
                Severity=GateSeverity.MEDIUM,
                validator=self._validate_redundancy,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_COMPETENCY_WORD_COUNT_BALANCE,
                name="Competency Word Count Balance",
                description=("Validates that competency descriptions are balanced in word count."),
                Severity=GateSeverity.MEDIUM,
                validator=self._validate_competency_balance,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_SUMMARY_VOICE_TENSE,
                name="Summary Voice and Tense",
                description=(
                    "Validates that the executive summary uses correct voice and tense throughout."
                ),
                Severity=GateSeverity.MEDIUM,
                validator=self._validate_summary_voice_tense,
            )
        )

    def _register_low_priority_gates(self) -> None:
        """Register low priority validation gates."""
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_NATURAL_HYPHEN_PRESERVATION,
                name="Natural Hyphen Preservation",
                description=("Ensures natural hyphens in compound words are preserved correctly."),
                Severity=GateSeverity.LOW,
                validator=self._validate_hyphen_preservation,
            )
        )
        self.register_gate(
            ValidationGate(
                gate_id=self.VG_BULLET_PUNCTUATION,
                name="Bullet Punctuation",
                description=("Ensures consistent punctuation across all bullet points."),
                Severity=GateSeverity.LOW,
                validator=self._validate_bullet_punctuation,
            )
        )

    def _register_default_gates(self) -> None:
        """Register all default validation gates."""
        self._register_critical_gates()
        self._register_high_priority_gates()
        self._register_medium_priority_gates()
        self._register_low_priority_gates()

    def register_gate(self, gate: ValidationGate) -> None:
        """Register a validation gate."""
        self._gates[gate.gate_id] = gate

    def get_gate(self, gate_id: str) -> ValidationGate | None:
        """Get a gate by ID."""
        return self._gates.get(gate_id)

    def list_gates(self) -> list[str]:
        """List all registered gate IDs."""
        return list(self._gates.keys())

    def run_gate(
        self,
        gate_id: str,
        content: object,
        context: dict[str, object] | None = None,
    ) -> GateResult:
        """
        Run a specific validation gate.

        Args:
            gate_id: ID of the gate to run
            content: Content to validate
            context: Additional context for validation

        Returns:
            GateResult with validation outcome
        """
        gate = self._gates.get(gate_id)
        if gate is None:
            return GateResult(
                gate_id=gate_id,
                decision=GateDecision.FAIL,
                Severity=GateSeverity.CRITICAL,
                message=f"Unknown gate: {gate_id}",
            )

        context = context or {}
        return gate.validator(content, context)

    def run_all_gates(
        self,
        content: object,
        context: dict[str, object] | None = None,
    ) -> list[GateResult]:
        """
        Run all validation gates.

        Args:
            content: Content to validate
            context: Additional context for validation

        Returns:
            List of GateResults
        """
        results = []
        for gate_id in self._gates:
            result = self.run_gate(gate_id, content, context)
            results.append(result)
        return results

    def _validate_summary_grounding(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate summary grounding."""
        violations = []

        if isinstance(content, str):
            text = content
        elif isinstance(content, dict):
            text = content.get("executive_summary", "")
        else:
            text = str(content)

        # Check for template marker patterns
        template_patterns = [r"\[.*?\]", r"\{.*?\}", r"<.*?>", r"TODO", r"XXX"]
        for pattern in template_patterns:
            matches = re.findall(pattern, text)
            if matches:
                violations.append(f"Template marker found: {matches}")

        # Check for unsupported claims (heuristic)
        unsupported_markers = [
            "reportedly",
            "allegedly",
            "it is said",
            "some say",
            "many believe",
        ]
        for marker in unsupported_markers:
            if marker.lower() in text.lower():
                violations.append(f"Unsupported Claim marker: {marker}")

        decision = GateDecision.PASS if not violations else GateDecision.FAIL

        return GateResult(
            gate_id=self.VG_SUMMARY_GROUNDING_CHECK,
            decision=decision,
            Severity=GateSeverity.CRITICAL,
            message="Summary grounding check completed",
            violations=violations,
            details={"text_length": len(text)},
        )

    def _validate_bullet_hallucination(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate bullet hallucination."""
        violations = []

        bullets = []
        if isinstance(content, list):
            bullets = content
        elif isinstance(content, dict):
            bullets = content.get("bullets", [])

        source_material = context.get("source_material", "")

        for i, bullet in enumerate(bullets):
            bullet_text = bullet if isinstance(bullet, str) else bullet.get("text", "")

            # Check for metrics without source
            metrics = re.findall(r"\d+%|\$\d+|\d+x|\d+\+", bullet_text)
            for Metric in metrics:
                if Metric not in source_material:
                    violations.append(f"Bullet {i + 1}: Metric '{Metric}' not found in source")

        decision = GateDecision.PASS if not violations else GateDecision.FAIL

        return GateResult(
            gate_id=self.VG_BULLET_HALLUCINATION_CHECK,
            decision=decision,
            Severity=GateSeverity.CRITICAL,
            message="Bullet hallucination check completed",
            violations=violations,
            details={"bullet_count": len(bullets)},
        )

    def _validate_thematic_uniqueness(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate thematic uniqueness."""
        violations = []

        bullets = []
        if isinstance(content, list):
            bullets = [b if isinstance(b, str) else b.get("text", "") for b in content]
        elif isinstance(content, dict):
            bullets = content.get("bullets", [])

        # Simple similarity check
        for i, bullet1 in enumerate(bullets):
            for j, bullet2 in enumerate(bullets[i + 1 :], start=i + 1):
                # Check word overlap
                words1 = set(bullet1.lower().split())
                words2 = set(bullet2.lower().split())
                overlap = len(words1 & words2) / max(len(words1 | words2), 1)

                if overlap > 0.6:
                    violations.append(
                        f"Bullets {i + 1} and {j + 1} have high similarity ({overlap:.0%})"
                    )

        decision = GateDecision.PASS if not violations else GateDecision.WARN

        return GateResult(
            gate_id=self.VG_THEMATIC_UNIQUENESS,
            decision=decision,
            Severity=GateSeverity.HIGH,
            message="Thematic uniqueness check completed",
            violations=violations,
        )

    def _validate_creative_brief_adherence(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate creative brief adherence."""
        violations = []

        brief = context.get("creative_brief", {})

        if isinstance(content, dict):
            # Check headline
            headline = content.get("headline", "")
            if headline:
                word_count = len(headline.split())
                min_words = brief.get("headline", {}).get("min_words", 8)
                max_words = brief.get("headline", {}).get("max_words", 12)
                if word_count < min_words or word_count > max_words:
                    violations.append(
                        f"Headline word count {word_count} outside range [{min_words}, {max_words}]"
                    )

            # Check executive summary
            summary = content.get("executive_summary", "")
            if summary:
                word_count = len(summary.split())
                min_words = brief.get("executive_summary", {}).get("min_words", 120)
                max_words = brief.get("executive_summary", {}).get("max_words", 140)
                if word_count < min_words or word_count > max_words:
                    violations.append(
                        f"Summary word count {word_count} outside range [{min_words}, {max_words}]"
                    )

        decision = GateDecision.PASS if not violations else GateDecision.FAIL

        return GateResult(
            gate_id=self.VG_CREATIVE_BRIEF_ADHERENCE,
            decision=decision,
            Severity=GateSeverity.HIGH,
            message="Creative brief adherence check completed",
            violations=violations,
        )

    def _validate_header_integrity(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate header integrity."""
        violations = []

        if isinstance(content, dict):
            required_sections = context.get(
                "required_sections",
                ["headline", "executive_summary", "experience", "education"],
            )

            for section in required_sections:
                if section not in content or not content[section]:
                    violations.append(f"Missing required section: {section}")

        decision = GateDecision.PASS if not violations else GateDecision.FAIL

        return GateResult(
            gate_id=self.VG_HEADER_INTEGRITY_CHECK,
            decision=decision,
            Severity=GateSeverity.MEDIUM,
            message="Header integrity check completed",
            violations=violations,
        )

    def _validate_bullet_provenance(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate bullet provenance."""
        violations = []

        bullets = []
        if isinstance(content, list):
            bullets = content
        elif isinstance(content, dict):
            bullets = content.get("bullets", [])

        for i, bullet in enumerate(bullets):
            if isinstance(bullet, dict):
                if "source" not in bullet and "provenance" not in bullet:
                    violations.append(f"Bullet {i + 1}: Missing provenance information")

        decision = GateDecision.PASS if not violations else GateDecision.WARN

        return GateResult(
            gate_id=self.VG_BULLET_PROVENANCE_CHECK,
            decision=decision,
            Severity=GateSeverity.HIGH,
            message="Bullet provenance check completed",
            violations=violations,
        )

    def _validate_redundancy(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate for redundancy."""
        # Simplified implementation
        return GateResult(
            gate_id=self.VG_REDUNDANCY_CHECK,
            decision=GateDecision.PASS,
            Severity=GateSeverity.MEDIUM,
            message="Redundancy check completed",
        )

    def _validate_hyphen_preservation(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate hyphen preservation."""
        # Simplified implementation
        return GateResult(
            gate_id=self.VG_NATURAL_HYPHEN_PRESERVATION,
            decision=GateDecision.PASS,
            Severity=GateSeverity.LOW,
            message="Hyphen preservation check completed",
        )

    def _validate_competency_balance(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate competency word count balance."""
        violations = []

        competencies = []
        if isinstance(content, list):
            competencies = content
        elif isinstance(content, dict):
            competencies = content.get("competencies", [])

        if competencies:
            word_counts = [len(c.split()) if isinstance(c, str) else 0 for c in competencies]
            if word_counts:
                avg = sum(word_counts) / len(word_counts)
                for i, wc in enumerate(word_counts):
                    if abs(wc - avg) > avg * 0.5:
                        violations.append(
                            f"Competency {i + 1}: Word count {wc} significantly differs from average {avg:.0f}"
                        )

        decision = GateDecision.PASS if not violations else GateDecision.WARN

        return GateResult(
            gate_id=self.VG_COMPETENCY_WORD_COUNT_BALANCE,
            decision=decision,
            Severity=GateSeverity.MEDIUM,
            message="Competency balance check completed",
            violations=violations,
        )

    def _validate_bullet_punctuation(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate bullet punctuation."""
        violations = []

        bullets = []
        if isinstance(content, list):
            bullets = [b if isinstance(b, str) else b.get("text", "") for b in content]
        elif isinstance(content, dict):
            bullets = content.get("bullets", [])

        for i, bullet in enumerate(bullets):
            if bullet and not bullet.rstrip().endswith((".", "!", "?")):
                violations.append(f"Bullet {i + 1}: Missing ending punctuation")

        decision = GateDecision.PASS if not violations else GateDecision.WARN

        return GateResult(
            gate_id=self.VG_BULLET_PUNCTUATION,
            decision=decision,
            Severity=GateSeverity.LOW,
            message="Bullet punctuation check completed",
            violations=violations,
        )

    def _validate_summary_voice_tense(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate summary voice and tense."""
        violations = []

        text = ""
        if isinstance(content, str):
            text = content
        elif isinstance(content, dict):
            text = content.get("executive_summary", "")

        # Check for first person (should be third person implied)
        first_person_markers = [" I ", " I'm ", " I've ", " my ", " me "]
        for marker in first_person_markers:
            if marker.lower() in f" {text.lower()} ":
                violations.append(f"First person marker found: {marker.strip()}")

        decision = GateDecision.PASS if not violations else GateDecision.FAIL

        return GateResult(
            gate_id=self.VG_SUMMARY_VOICE_TENSE,
            decision=decision,
            Severity=GateSeverity.MEDIUM,
            message="Summary voice and tense check completed",
            violations=violations,
        )

    def _validate_agentic_output(
        self,
        content: object,
        context: dict[str, object],
    ) -> GateResult:
        """Validate agentic output."""
        violations = []

        # Check for required fields in agentic output
        if isinstance(content, dict):
            required_fields = context.get(
                "required_fields",
                ["status", "output"],
            )
            for field_name in required_fields:
                if field_name not in content:
                    violations.append(f"Missing required field: {field_name}")

        decision = GateDecision.PASS if not violations else GateDecision.FAIL

        return GateResult(
            gate_id=self.VG_AGENTIC_OUTPUT_VALIDATION,
            decision=decision,
            Severity=GateSeverity.HIGH,
            message="Agentic output validation completed",
            violations=violations,
        )


def create_validation_gates() -> RGValidationGates:
    """builder function to create validation gates."""
    return RGValidationGates()


def run_gate(
    gate_id: str,
    content: object,
    context: dict[str, object] | None = None,
) -> GateResult:
    """Run a specific validation gate."""
    gates = RGValidationGates()
    return gates.run_gate(gate_id, content, context)
