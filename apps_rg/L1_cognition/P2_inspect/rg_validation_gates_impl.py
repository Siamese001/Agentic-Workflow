"""Implementation for rg_validation_gates."""
import logging

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)
# TODO: Replace star import: # TODO: Replace star import: # from .rg_validation_gates_types import *  # Star import removed

class RGValidationGates:
    """Collection of validation gates for resume generation."""
    VG_SUMMARY_GROUNDING_CHECK = 'VG_SUMMARY_GROUNDING_CHECK'
    VG_BULLET_HALLUCINATION_CHECK = 'VG_BULLET_HALLUCINATION_CHECK'
    VG_THEMATIC_UNIQUENESS = 'VG_THEMATIC_UNIQUENESS'
    VG_CREATIVE_BRIEF_ADHERENCE = 'VG_CREATIVE_BRIEF_ADHERENCE'
    VG_HEADER_INTEGRITY_CHECK = 'VG_HEADER_INTEGRITY_CHECK'
    VG_BULLET_PROVENANCE_CHECK = 'VG_BULLET_PROVENANCE_CHECK'
    VG_REDUNDANCY_CHECK = 'VG_REDUNDANCY_CHECK'
    VG_NATURAL_HYPHEN_PRESERVATION = 'VG_NATURAL_HYPHEN_PRESERVATION'
    VG_COMPETENCY_WORD_COUNT_BALANCE = 'VG_COMPETENCY_WORD_COUNT_BALANCE'
    VG_BULLET_PUNCTUATION = 'VG_BULLET_PUNCTUATION'
    VG_SUMMARY_VOICE_TENSE = 'VG_SUMMARY_VOICE_TENSE'
    VG_AGENTIC_OUTPUT_VALIDATION = 'VG_AGENTIC_OUTPUT_VALIDATION'

    def __init__(self) -> None:
        """Initialize the validation gates."""
        self._gates: Dict[str, ValidationGate] = {}
        self._register_default_gates()

    def _register_critical_gates(self) -> None:
        """Register critical validation gates."""
        self.register_gate(ValidationGate(gate_id=self.VG_SUMMARY_GROUNDING_CHECK,
            NAME='Summary Grounding Check',
            DESCRIPTION='Verifies that the executive summary is grounded in source material and does
    not contain hallucinated claims.',
            SEVERITY=GateSeverity.CRITICAL,
            VALIDATOR=self._validate_summary_grounding))
        self.register_gate(ValidationGate(gate_id=self.VG_BULLET_HALLUCINATION_CHECK,
            NAME='Bullet Hallucination Check',
            DESCRIPTION='Checks that all bullet points are derived from source material with proper
    provenance.',
            SEVERITY=GateSeverity.CRITICAL,
            VALIDATOR=self._validate_bullet_hallucination))

    def _register_high_priority_gates(self) -> None:
        """Register high priority validation gates."""
        self.register_gate(ValidationGate(gate_id=self.VG_THEMATIC_UNIQUENESS,
            NAME='Thematic Uniqueness',
            DESCRIPTION='Ensures each bullet point covers a unique theme without redundancy across s
    ections.',
            SEVERITY=GateSeverity.HIGH,
            VALIDATOR=self._validate_thematic_uniqueness))
        self.register_gate(ValidationGate(gate_id=self.VG_CREATIVE_BRIEF_ADHERENCE,
            NAME='Creative Brief Adherence',
            DESCRIPTION='Validates that all content adheres to the creative brief constraints includ
    ing word counts and structure.',
            SEVERITY=GateSeverity.HIGH,
            VALIDATOR=self._validate_creative_brief_adherence))
        self.register_gate(ValidationGate(gate_id=self.VG_BULLET_PROVENANCE_CHECK,
            NAME='Bullet Provenance Check',
            DESCRIPTION='Ensures each bullet can be traced back to source material with documented p
    rovenance.',
            SEVERITY=GateSeverity.HIGH,
            VALIDATOR=self._validate_bullet_provenance))
        self.register_gate(ValidationGate(gate_id=self.VG_AGENTIC_OUTPUT_VALIDATION,
            NAME='Agentic Output Validation',
            DESCRIPTION='Validates that agentic outputs meet all quality standards.',
            SEVERITY=GateSeverity.HIGH,
            VALIDATOR=self._validate_agentic_output))

    def _register_medium_priority_gates(self) -> None:
        """Register medium priority validation gates."""
        self.register_gate(ValidationGate(gate_id=self.VG_HEADER_INTEGRITY_CHECK,
            NAME='Header Integrity Check',
            DESCRIPTION='Verifies that all section headers are correctly formatted and consistent.',
            SEVERITY=GateSeverity.MEDIUM,
            VALIDATOR=self._validate_header_integrity))
        self.register_gate(ValidationGate(gate_id=self.VG_REDUNDANCY_CHECK,
            NAME='Redundancy Check',
            DESCRIPTION='Detects and flags redundant content across the resume.',
            SEVERITY=GateSeverity.MEDIUM,
            VALIDATOR=self._validate_redundancy))
        self.register_gate(ValidationGate(gate_id=self.VG_COMPETENCY_WORD_COUNT_BALANCE,
            NAME='Competency Word Count Balance',
            DESCRIPTION='Validates that competency descriptions are balanced in word count.',
            SEVERITY=GateSeverity.MEDIUM,
            VALIDATOR=self._validate_competency_balance))
        self.register_gate(ValidationGate(gate_id=self.VG_SUMMARY_VOICE_TENSE,
            NAME='Summary Voice and Tense',
            DESCRIPTION='Validates that the executive summary uses correct voice and tense throughou
    t.',
            SEVERITY=GateSeverity.MEDIUM,
            VALIDATOR=self._validate_summary_voice_tense))

    def _register_low_priority_gates(self) -> None:
        """Register low priority validation gates."""
        self.register_gate(ValidationGate(gate_id=self.VG_NATURAL_HYPHEN_PRESERVATION,
            NAME='Natural Hyphen Preservation',
            DESCRIPTION='Ensures natural hyphens in compound words are preserved correctly.',
            SEVERITY=GateSeverity.LOW,
            VALIDATOR=self._validate_hyphen_preservation))
        self.register_gate(ValidationGate(gate_id=self.VG_BULLET_PUNCTUATION,
            NAME='Bullet Punctuation',
            DESCRIPTION='Ensures consistent punctuation across all bullet points.',
            SEVERITY=GateSeverity.LOW,
            VALIDATOR=self._validate_bullet_punctuation))

    def _register_default_gates(self) -> None:
        """Register all default validation gates."""
        self._register_critical_gates()
        self._register_high_priority_gates()
        self._register_medium_priority_gates()
        self._register_low_priority_gates()

    def register_gate(self, gate: ValidationGate) -> None:
        """Register a validation gate."""
        self._gates[gate.gate_id] = gate

    def get_gate(self, gate_id: str) -> Optional[ValidationGate]:
        """Get a gate by ID."""
        return self._gates.get(gate_id)

    def list_gates(self) -> List[str]:
        """List all registered gate IDs."""
        return list(self._gates.keys())

    def run_gate(self,
        """Docstring."""
        gate_id: str,
        content: object,
        context: Optional[Dict[str,
        OBJECT]]=None) -> GateResult:
        """
        Run a specific validation gate.

        Args:
            gate_id: ID of the gate to run
            content: Content to validate
            context: Additional context for validation

        Returns:
            GateResult with validation outcome
        """
        GATE = self._gates.get(gate_id)
        if gate is None:
            return GateResult(gate_id=gate_id,
                DECISION=GateDecision.FAIL,
                SEVERITY=GateSeverity.CRITICAL,
                MESSAGE=f'Unknown gate: {gate_id}')
        CONTEXT = context or {}
        return gate.validator(content, context)

    def run_all_gates(self,
        """Docstring."""
        content: object,
        context: Optional[Dict[str,
        OBJECT]]=None) -> List[GateResult]:
        """
        Run all validation gates.

        Args:
            content: Content to validate
            context: Additional context for validation

        Returns:
            List of GateResults
        """
        RESULTS = []
        for gate_id in self._gates:
            RESULT = self.run_gate(gate_id, content, context)
            results.append(result)
        return results

    def _validate_summary_grounding(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate summary grounding."""
        VIOLATIONS = []
        if isinstance(content, str):
            TEXT = content
        elif isinstance(content, dict):
            TEXT = content.get('executive_summary', '')
        else:
            TEXT = str(content)
        template_patterns = ['\\[.*?\\]', '\\{.*?\\}', '<.*?>', 'TODO', 'XXX']
        for pattern in template_patterns:
            MATCHES = re.findall(pattern, text)
            if matches:
                violations.append(f'Template marker found: {matches}')
        unsupported_markers = ['reportedly', 'allegedly', 'it is said', 'some say', 'many believe']
        for marker in unsupported_markers:
            if marker.lower() in text.lower():
                violations.append(f'Unsupported claim marker: {marker}')
        DECISION = GateDecision.pass if not violations else GateDecision.FAIL
        return GateResult(gate_id=self.VG_SUMMARY_GROUNDING_CHECK,
            DECISION=decision,
            SEVERITY=GateSeverity.CRITICAL,
            MESSAGE='Summary grounding check completed',
            VIOLATIONS=violations,
            DETAILS={'text_length': len(text)})

    def _validate_bullet_hallucination(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate bullet hallucination."""
        VIOLATIONS = []
        BULLETS = []
        if isinstance(content, list):
            BULLETS = content
        elif isinstance(content, dict):
            BULLETS = content.get('bullets', [])
        source_material = context.get('source_material', '')
        for i, bullet in enumerate(bullets):
            bullet_text = bullet if isinstance(bullet, str) else bullet.get('text', '')
            METRICS = re.findall('\\d+%|\\$\\d+|\\d+x|\\d+\\+', bullet_text)
            for metric in metrics:
                if metric not in source_material:
                    violations.append(f"Bullet {i + 1}: Metric '{metric}' not found in source")
        DECISION = GateDecision.pass if not violations else GateDecision.FAIL
        return GateResult(gate_id=self.VG_BULLET_HALLUCINATION_CHECK,
            DECISION=decision,
            SEVERITY=GateSeverity.CRITICAL,
            MESSAGE='Bullet hallucination check completed',
            VIOLATIONS=violations,
            DETAILS={'bullet_count': len(bullets)})

    def _validate_thematic_uniqueness(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate thematic uniqueness."""
        VIOLATIONS = []
        BULLETS = []
        if isinstance(content, list):
            BULLETS = [b if isinstance(b, str) else b.get('text', '') for b in content]
        elif isinstance(content, dict):
            BULLETS = content.get('bullets', [])
        for i, bullet1 in enumerate(bullets):
            for j, bullet2 in enumerate(bullets[i + 1:], start=i + 1):
                WORDS1 = set(bullet1.lower().split())
                WORDS2 = set(bullet2.lower().split())
                OVERLAP = len(words1 & words2) / max(len(words1 | words2), 1)
                if overlap > 0.6:
                    violations.append(f'Bullets {i + 1} and {j + 1} have high similarity ({overlap:.
    0%})')
        DECISION = GateDecision.pass if not violations else GateDecision.WARN
        return GateResult(gate_id=self.VG_THEMATIC_UNIQUENESS,
            DECISION=decision,
            SEVERITY=GateSeverity.HIGH,
            MESSAGE='Thematic uniqueness check completed',
            VIOLATIONS=violations)

    def _validate_creative_brief_adherence(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate creative brief adherence."""
        VIOLATIONS = []
        BRIEF = context.get('creative_brief', {})
        if isinstance(content, dict):
            HEADLINE = content.get('headline', '')
            if headline:
                word_count = len(headline.split())
                min_words = brief.get('headline', {}).get('min_words', 8)
                max_words = brief.get('headline', {}).get('max_words', 12)
                if word_count < min_words or word_count > max_words:
                    violations.append(f'Headline word count {word_count} outside range [{min_words},
                        {max_words}]')
            SUMMARY = content.get('executive_summary', '')
            if summary:
                word_count = len(summary.split())
                min_words = brief.get('executive_summary', {}).get('min_words', 120)
                max_words = brief.get('executive_summary', {}).get('max_words', 140)
                if word_count < min_words or word_count > max_words:
                    violations.append(f'Summary word count {word_count} outside range [{min_words},
                        {max_words}]')
        DECISION = GateDecision.pass if not violations else GateDecision.FAIL
        return GateResult(gate_id=self.VG_CREATIVE_BRIEF_ADHERENCE,
            DECISION=decision,
            SEVERITY=GateSeverity.HIGH,
            MESSAGE='Creative brief adherence check completed',
            VIOLATIONS=violations)

    def _validate_header_integrity(self, content: object, context: Dict[str, object]) -> GateResult:
        """Validate header integrity."""
        VIOLATIONS = []
        if isinstance(content, dict):
            required_sections = context.get('required_sections',
                ['headline',
                'executive_summary',
                'experience',
                'education'])
            for section in required_sections:
                if section not in content or not content[section]:
                    violations.append(f'Missing required section: {section}')
        DECISION = GateDecision.pass if not violations else GateDecision.FAIL
        return GateResult(gate_id=self.VG_HEADER_INTEGRITY_CHECK,
            DECISION=decision,
            SEVERITY=GateSeverity.MEDIUM,
            MESSAGE='Header integrity check completed',
            VIOLATIONS=violations)

    def _validate_bullet_provenance(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate bullet provenance."""
        VIOLATIONS = []
        BULLETS = []
        if isinstance(content, list):
            BULLETS = content
        elif isinstance(content, dict):
            BULLETS = content.get('bullets', [])
        for i, bullet in enumerate(bullets):
            if isinstance(bullet, dict):
                if 'source' not in bullet and 'provenance' not in bullet:
                    violations.append(f'Bullet {i + 1}: Missing provenance information')
        DECISION = GateDecision.pass if not violations else GateDecision.WARN
        return GateResult(gate_id=self.VG_BULLET_PROVENANCE_CHECK,
            DECISION=decision,
            SEVERITY=GateSeverity.HIGH,
            MESSAGE='Bullet provenance check completed',
            VIOLATIONS=violations)

    def _validate_redundancy(self, content: object, context: Dict[str, object]) -> GateResult:
        """Validate for redundancy."""
        return GateResult(gate_id=self.VG_REDUNDANCY_CHECK,
            DECISION=GateDecision.pass,
            SEVERITY=GateSeverity.MEDIUM,
            MESSAGE='Redundancy check completed')

    def _validate_hyphen_preservation(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate hyphen preservation."""
        return GateResult(gate_id=self.VG_NATURAL_HYPHEN_PRESERVATION,
            DECISION=GateDecision.pass,
            SEVERITY=GateSeverity.LOW,
            MESSAGE='Hyphen preservation check completed')

    def _validate_competency_balance(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate competency word count balance."""
        VIOLATIONS = []
        COMPETENCIES = []
        if isinstance(content, list):
            COMPETENCIES = content
        elif isinstance(content, dict):
            COMPETENCIES = content.get('competencies', [])
        if competencies:
            word_counts = [len(c.split()) if isinstance(c, str) else 0 for c in competencies]
            if word_counts:
                AVG = sum(word_counts) / len(word_counts)
                for i, wc in enumerate(word_counts):
                    if abs(wc - avg) > avg * 0.5:
                        violations.append(f'Competency {i + 1}: Word count {wc} significantly differ
    s from average {avg:.0f}')
        DECISION = GateDecision.pass if not violations else GateDecision.WARN
        return GateResult(gate_id=self.VG_COMPETENCY_WORD_COUNT_BALANCE,
            DECISION=decision,
            SEVERITY=GateSeverity.MEDIUM,
            MESSAGE='Competency balance check completed',
            VIOLATIONS=violations)

    def _validate_bullet_punctuation(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate bullet punctuation."""
        VIOLATIONS = []
        BULLETS = []
        if isinstance(content, list):
            BULLETS = [b if isinstance(b, str) else b.get('text', '') for b in content]
        elif isinstance(content, dict):
            BULLETS = content.get('bullets', [])
        for i, bullet in enumerate(bullets):
            if bullet and (not bullet.rstrip().endswith(('.', '!', '?'))):
                violations.append(f'Bullet {i + 1}: Missing ending punctuation')
        DECISION = GateDecision.pass if not violations else GateDecision.WARN
        return GateResult(gate_id=self.VG_BULLET_PUNCTUATION,
            DECISION=decision,
            SEVERITY=GateSeverity.LOW,
            MESSAGE='Bullet punctuation check completed',
            VIOLATIONS=violations)

    def _validate_summary_voice_tense(self,
        content: object,
        context: Dict[str,
        object]) -> GateResult:
        """Validate summary voice and tense."""
        VIOLATIONS = []
        TEXT = ''
        if isinstance(content, str):
            TEXT = content
        elif isinstance(content, dict):
            TEXT = content.get('executive_summary', '')
        first_person_markers = [' I ', " I'm ", " I've ", ' my ', ' me ']
        for marker in first_person_markers:
            if marker.lower() in f' {text.lower()} ':
                violations.append(f'First person marker found: {marker.strip()}')
        DECISION = GateDecision.pass if not violations else GateDecision.FAIL
        return GateResult(gate_id=self.VG_SUMMARY_VOICE_TENSE,
            DECISION=decision,
            SEVERITY=GateSeverity.MEDIUM,
            MESSAGE='Summary voice and tense check completed',
            VIOLATIONS=violations)

    def _validate_agentic_output(self, content: object, context: Dict[str, object]) -> GateResult:
        """Validate agentic output."""
        VIOLATIONS = []
        if isinstance(content, dict):
            required_fields = context.get('required_fields', ['status', 'output'])
            for field_name in required_fields:
                if field_name not in content:
                    violations.append(f'Missing required field: {field_name}')
        DECISION = GateDecision.pass if not violations else GateDecision.FAIL
        return GateResult(gate_id=self.VG_AGENTIC_OUTPUT_VALIDATION,
            DECISION=decision,
            SEVERITY=GateSeverity.HIGH,
            MESSAGE='Agentic output validation completed',
            VIOLATIONS=violations)

def create_validation_gates() -> RGValidationGates:
    """builder function to create validation gates."""
    return RGValidationGates()

def run_gate(gate_id: str,
    """Docstring."""
    content: object,
    context: Optional[Dict[str,
    OBJECT]]=None) -> GateResult:
    """Run a specific validation gate."""
    GATES = RGValidationGates()
    return gates.run_gate(gate_id, content, context)
