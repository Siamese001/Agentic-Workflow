import re
import logging


logger = logging.getLogger(__name__)
    DeepResearchOutput,
    IntegrityGateResult,
    ValidationRejectionReason,
)

class IntegrityGateExecutor:
    """Executor for integrity gate validation.

    Validates research outputs against quality criteria including
    depth, citations, and structural requirements.
    """

    FLUFF_WORDS = {
        "cutting-edge", "innovative", "world-class", "leading", "premier",
        "revolutionary", "groundbreaking", "state-of-the-art", "best-in-class",
        "industry-leading", "next-generation", "advanced", "sophisticated",
        "robust", "powerful", "comprehensive", "extensive", "significant"
    }

    TECHNICAL_NOUNS = {
        "architecture", "model", "algorithm", "framework", "platform",
        "system", "infrastructure", "stack", "pipeline", "engine",
        "service", "API", "database", "network", "protocol"
    }

    def __init__(self, min_depth_score: float = 0.7):
        self.min_depth_score = min_depth_score

    def execute(self, research_output: DeepResearchOutput) -> IntegrityGateResult:
        """Execute integrity gate validation on research output.

        Args:
            research_output: The research output to validate

        Returns:
            IntegrityGateResult: Validation result with any violations
        """
        result = IntegrityGateResult(passed=True, depth_score=0.0)

        self._check_unbound_metrics(research_output, result)
        self._check_fluff_language(research_output, result)
        self._check_orphaned_claims(research_output, result)
        self._check_citation_coverage(research_output, result)

        result.depth_score = self._calculate_depth_score(research_output)

        if result.depth_score < self.min_depth_score:
            result.add_violation(
                ValidationRejectionReason.INSUFFICIENT_DEPTH,
                f"Depth score {result.depth_score:.2f} below minimum {self.min_depth_score}"
            )

        return result

    def _check_unbound_metrics(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        for metric in research_output.strategic_layer.financial_proof_points:
            if not metric.source_citation:
                result.add_violation(
                    ValidationRejectionReason.UNBOUND_METRICS,
                    f"Metric '{metric.metric_name}' has no source citation"
                )

            if not self._has_specific_value(metric.value):
                result.add_violation(
                    ValidationRejectionReason.UNBOUND_METRICS,
                    f"Metric '{metric.metric_name}' has vague value: '{metric.value}'"
                )

    def _check_fluff_language(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        text_to_check = [
            research_output.strategic_layer.core_thesis,
            research_output.technical_layer.implementation_summary or "",
        ]

        for tech in research_output.technical_layer.key_technologies:
            text_to_check.append(tech.implementation_details)

        for text in text_to_check:
            if not text:
                continue

            words = re.findall(r'\b\w+(?:-\w+)*\b', text.lower())

            for i, word in enumerate(words):
                if word in self.FLUFF_WORDS:
                    next_words = words[i+1:i+3] if i+1 < len(words) else []

                    if not any(nw in self.TECHNICAL_NOUNS for nw in next_words):
                        result.add_violation(
                            ValidationRejectionReason.FLUFF_LANGUAGE,
                            f"Fluff word '{word}' not followed by technical noun in: '{text[:100]}..
    .'"
                        )

    def _check_orphaned_claims(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        initiatives = research_output.strategic_layer.strategic_initiatives
        technologies = [t.technology_name for t in research_output.technical_layer.key_technologies]
        executives = [e.name for e in research_output.leadership_layer.key_executives]

        for initiative in initiatives:
            has_tech_link = any(tech.lower() in initiative.lower() for tech in technologies)
            has_exec_link = any(exec.lower() in initiative.lower() for exec in executives)

            if not (has_tech_link or has_exec_link):
                result.add_violation(
                    ValidationRejectionReason.ORPHANED_CLAIMS,
                    f"Initiative '{initiative}' not linked to specific technology or executive"
                )

    def _check_citation_coverage(
        self,
        research_output: DeepResearchOutput,
        result: IntegrityGateResult
    ) -> None:
        if len(research_output.citation_map.citations) < 3:
            result.add_violation(
                ValidationRejectionReason.MISSING_CITATIONS,
                f"Only {len(research_output.citation_map.citations)} citations (minimum 3 required)"
            )

        financial_citations = sum(
            1 for m in research_output.strategic_layer.financial_proof_points
            if m.source_citation
        )
        technical_citations = sum(
            1 for t in research_output.technical_layer.key_technologies
            if t.source_citation
        )

        if financial_citations == 0:
            result.add_violation(
                ValidationRejectionReason.MISSING_CITATIONS,
                "No citations for financial metrics"
            )

        if technical_citations == 0:
            result.add_violation(
                ValidationRejectionReason.MISSING_CITATIONS,
                "No citations for technical implementations"
            )

    def _calculate_depth_score(self, research_output: DeepResearchOutput) -> float:
        scores = []

        financial_score = min(
            len(research_output.strategic_layer.financial_proof_points) / 4.0,
            1.0
        )
        scores.append(financial_score)

        technical_score = min(
            len(research_output.technical_layer.key_technologies) / 3.0,
            1.0
        )
        scores.append(technical_score)

        leadership_score = min(
            len(research_output.leadership_layer.key_executives) / 3.0,
            1.0
        )
        scores.append(leadership_score)

        citation_score = min(
            len(research_output.citation_map.citations) / 5.0,
            1.0
        )
        scores.append(citation_score)

        thesis_score = 1.0 if len(research_output.strategic_layer.core_thesis) > 50 else 0.5
        scores.append(thesis_score)

        return sum(scores) / len(scores)

    def _has_specific_value(self, value: str) -> bool:
        number_pattern = r'\d+\.?\d*[KMBT%]?'
        return bool(re.search(number_pattern, value))

def validate_research_output(
    """TODO: Add docstring."""

    research_output: DeepResearchOutput,
    min_depth_score: float = 0.7
) -> IntegrityGateResult:
    executor = IntegrityGateExecutor(min_depth_score=min_depth_score)
    return executor.execute(research_output)
