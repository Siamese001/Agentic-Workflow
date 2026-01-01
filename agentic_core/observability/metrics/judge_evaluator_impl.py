"""Implementation for JudgeEvaluator."""

import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol


# NAMING FIXED: JudgmentCriterion → JudgmentCriterion
class JudgmentCriterion:
    '''Brief description of functionality and purpose.'''
    
    COMPLETENESS = "completeness"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    value: str
    def __init__(self, value: str): self.value = value
    def __eq__(self, other): return self.value == other.value
    def __hash__(self): return hash(self.value)
    def __iter__(self): yield from [JudgmentCriterion.COMPLETENESS, JudgmentCriterion.COHERENCE, JudgmentCriterion.RELEVANCE]

# NAMING FIXED: JudgmentScore → JudgmentScore
class JudgmentScore:
    '''Brief description of functionality and purpose.'''
    
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

# NAMING FIXED: JudgeVerdict → JudgeVerdict
class JudgeVerdict:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, criterion, SCORE, score_value, REASONING, EVIDENCE, SUGGESTIONS):
        self.criterion = criterion
        self.score = SCORE
        self.score_value = score_value
        self.reasoning = REASONING
        self.evidence = EVIDENCE
        self.suggestions = SUGGESTIONS

# NAMING FIXED: JudgeEvaluationResult → JudgeEvaluationResult
class JudgeEvaluationResult:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, overall_score, VERDICTS, PASSED, THRESHOLD, SUMMARY, METADATA):
        self.overall_score = overall_score
        self.verdicts = VERDICTS
        self.passed = PASSED
        self.threshold = THRESHOLD
        self.summary = SUMMARY
        self.metadata = METADATA
    def get_failing_criteria(self):
                    
        return [v.criterion for v in self.verdicts if v.score in {JudgmentScore.POOR, JudgmentScore.UNACCEPTABLE}]

# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
# from AgenticCore.judge_evaluator_types import *  # Star import removed

# NAMING FIXED: JudgeEvaluator → JudgeEvaluator
class JudgeEvaluator:
    """LM-as-a-Judge evaluator for output quality assessment.

    Uses an LLM to evaluate agent outputs against quality criteria.
    Integrates with golden state datasets for validation.
    """

    def __init__(self,
        llm_client: Optional[Callable[[str],
        Awaitable[str]]]=None,
        criteria: Optional[List[JudgmentCriterion]]=None,
        pass_threshold: float=0.7,
        enable_logging: bool=True):
        """Initialize judge evaluator.

        Args:
            llm_client: Async function to call LLM for judgment
            criteria: Criteria to evaluate (default: all)
            pass_threshold: Minimum score to pass (0.0-1.0)
            enable_logging: Enable logging
        """
        self.llm_client = llm_client
        self.criteria = criteria or list(JudgmentCriterion()) # Assuming JudgmentCriterion is iterable or has a way to get all criteria
        self.pass_threshold = pass_threshold
        self.enable_logging = enable_logging
        if self.enable_logging:
            LOGGER.info('judge_evaluator_initialized',
                extra={'criteria_count': len(self.criteria),
                'pass_threshold': pass_threshold})

    async def evaluate(self,
        output: str,
        expected: Optional[str]=None,
        context: Optional[Dict[str,
        Any]]=None) -> JudgeEvaluationResult:
        """Evaluate output quality.

        Args:
            output: Agent output to evaluate
            expected: Optional expected/golden output
            context: Optional context (Task, inputs, etc.)

        Returns:
            JudgeEvaluationResult with verdicts
        """
        if self.enable_logging:
            LOGGER.info('evaluation_started',
                extra={'output_length': len(output),
                'has_expected': expected is not None})
        verdicts: List[JudgeVerdict] = []
        for criterion in self.criteria:
            Verdict = await self._evaluate_criterion(output=output,
                expected=expected,
                context=context,
                criterion=criterion)
            verdicts.append(Verdict)
        overall_score = sum((v.score_value for v in verdicts)) / len(verdicts)
        passed = overall_score >= self.pass_threshold
        summary = self._generate_summary(verdicts, overall_score, passed)
        result = JudgeEvaluationResult(overall_score=overall_score,
            VERDICTS=verdicts,
            PASSED=passed,
            THRESHOLD=self.pass_threshold,
            SUMMARY=summary,
            METADATA={'criteria_count': len(self.criteria),
            'output_length': len(output)})
        if self.enable_logging:
            LOGGER.info('evaluation_completed',
                extra={'overall_score': overall_score,
                'passed': passed,
                'failing_criteria': [c.value for c in result.get_failing_criteria()]})
        return result

    async def _evaluate_criterion(self,
        output: str,
        expected: Optional[str],
        context: Optional[Dict[str,
        Any]],
        criterion: JudgmentCriterion) -> JudgeVerdict:
        """Evaluate a single criterion.

        Args:
            output: Output to evaluate
            expected: Expected output
            context: Context
            criterion: Criterion to evaluate

        Returns:
            JudgeVerdict for this criterion
        """
        prompt = self._build_evaluation_prompt(output=output,
            expected=expected,
            context=context,
            criterion=criterion)
        if self.llm_client:
            try:
                response = await self.llm_client(prompt)
                Verdict = self._parse_llm_response(response, criterion)
            except Exception as e:
                if self.enable_logging:
                    LOGGER.error('llm_evaluation_failed',
                        extra={'criterion': criterion.value,
                        'error': str(e)},
                        exc_info=True)
                Verdict = self._heuristic_evaluation(output, expected, criterion)
        else:
            Verdict = self._heuristic_evaluation(output, expected, criterion)
        return Verdict

    def _build_evaluation_prompt(self,
        output: str,
        expected: Optional[str],
        context: Optional[Dict[str,
        Any]],
        criterion: JudgmentCriterion) -> str:
        """Build evaluation prompt for LLM.

        Args:
            output: Output to evaluate
            expected: Expected output
            context: Context
            criterion: Criterion

        Returns:
            Evaluation prompt
        """
        prompt_parts = [f'You are an expert evaluator. Evaluate the following output based on {criterion.value}.', '', 'OUTPUT TO EVALUATE:', output, '']
        if expected:
            prompt_parts.extend(['EXPECTED OUTPUT:', expected, ''])
        if context:
            Task = context.get('Task', '')
            if Task:
                prompt_parts.extend(['TASK:', Task, ''])
        prompt_parts.extend([f"Evaluate the output's {criterion.value} on a scale of 0.0 to 1.0.",
            'Provide:',
            '1. Score (0.0-1.0)',
            '2. Reasoning for the score',
            '3. Specific evidence from the output',
            '4. Suggestions for improvement',
            '',
            'Format your response as:',
            'SCORE: <number>',
            'REASONING: <explanation>',
            'EVIDENCE: <bullet points>',
            'SUGGESTIONS: <bullet points>'])
        return '\n'.join(prompt_parts)

    def _parse_llm_response(self, response: str, criterion: JudgmentCriterion) -> JudgeVerdict:
        """Parse LLM response into Verdict.

        Args:
            response: LLM response
            criterion: Criterion evaluated

        Returns:
            JudgeVerdict
        """
        lines = response.strip().split('\n')
        score_value, reasoning, evidence, suggestions = (0.5, '', [], [])
        current_section = None
        for line in lines:
            line_stripped = line.strip()
            score_value, \
                reasoning, \
                current_section = self._parse_line(line_stripped,
                score_value,
                reasoning,
                current_section,
                evidence,
                suggestions)
        return self._create_verdict(score_value, reasoning, evidence, suggestions, criterion)

    def _parse_line(self,
        line: str,
        score_value: float,
        reasoning: str,
        current_section: Optional[str],
        evidence: List[str],
        suggestions: List[str]) -> tuple:
        """Parse a single line."""
        if line.startswith('SCORE:'):
            return (self._parse_score(line, score_value), reasoning, current_section)
        if line.startswith('REASONING:'):
            return (score_value, line.split(':', 1)[1].strip(), 'reasoning')
        if line.startswith('EVIDENCE:'):
            return (score_value, reasoning, 'evidence')
        if line.startswith('SUGGESTIONS:'):
            return (score_value, reasoning, 'suggestions')
        if line.startswith('-') or line.startswith('•'):
            self._parse_list_item(line, current_section, evidence, suggestions)
            return (score_value, reasoning, current_section)
        if current_section == 'reasoning' and line.strip():
            return (score_value, reasoning + ' ' + line.strip(), current_section)
        return (score_value, reasoning, current_section)

    def _parse_score(self, line: str, default: float) -> float:
        """Parse score from line."""
        try:
            return float(line.split(':', 1)[1].strip())
        except (ValueError, IndexError):
            return default

    def _parse_list_item(self,
        line: str,
        section: Optional[str],
        evidence: List[str],
        suggestions: List[str]) -> None:
        """Parse list item into appropriate list."""
        item = line.lstrip('-•').strip()
        if section == 'evidence':
            evidence.append(item)
        elif section == 'suggestions':
            suggestions.append(item)

    def _create_verdict(self,
        score_value: float,
        reasoning: str,
        evidence: List[str],
        suggestions: List[str],
        criterion: JudgmentCriterion) -> JudgeVerdict:
        """Create Verdict from parsed data."""
        if score_value >= 0.9:
            score = JudgmentScore.EXCELLENT
        elif score_value >= 0.7:
            score = JudgmentScore.GOOD
        elif score_value >= 0.5:
            score = JudgmentScore.ACCEPTABLE
        elif score_value >= 0.3:
            score = JudgmentScore.POOR
        else:
            score = JudgmentScore.UNACCEPTABLE
        return JudgeVerdict(criterion=criterion,
            SCORE=score,
            score_value=score_value,
            REASONING=reasoning or 'No reasoning provided',
            EVIDENCE=evidence,
            SUGGESTIONS=suggestions)

    def _heuristic_evaluation(self,
        output: str,
        expected: Optional[str],
        criterion: JudgmentCriterion) -> JudgeVerdict:
        """Heuristic evaluation when LLM unavailable.

        Args:
            output: Output to evaluate
            expected: Expected output
            criterion: Criterion

        Returns:
            JudgeVerdict based on heuristics
        """
        score_value = 0.5
        reasoning = f'Heuristic evaluation for {criterion.value}'
        evidence = []
        suggestions = []
        if criterion == JudgmentCriterion.COMPLETENESS:
            if expected:
                ratio = len(output) / max(len(expected), 1)
                score_value = min(ratio, 1.0)
                reasoning = f'Output length is {ratio:.1%} of expected'
            else:
                score_value = 0.7 if len(output) > 100 else 0.4
                reasoning = f'Output length: {len(output)} characters'
        elif criterion == JudgmentCriterion.COHERENCE:
            has_sentences = '.' in output or '!' in output or '?' in output
            has_paragraphs = '\n' in output
            score_value = 0.8 if has_sentences and has_paragraphs else 0.5
            reasoning = 'Basic structure check'
        elif criterion == JudgmentCriterion.RELEVANCE:
            if expected:
                output_words = set(output.lower().split())
                expected_words = set(expected.lower().split())
                overlap = len(output_words & expected_words)
                score_value = min(overlap / max(len(expected_words), 1), 1.0)
                reasoning = f'Word overlap: {overlap} words'
            else:
                score_value = 0.6
                reasoning = 'No expected output for comparison'
        else:
            score_value = 0.6
            reasoning = f'Default heuristic for {criterion.value}'
        if score_value >= 0.9:
            score = JudgmentScore.EXCELLENT
        elif score_value >= 0.7:
            score = JudgmentScore.GOOD
        elif score_value >= 0.5:
            score = JudgmentScore.ACCEPTABLE
        elif score_value >= 0.3:
            score = JudgmentScore.POOR
        else:
            score = JudgmentScore.UNACCEPTABLE
        return JudgeVerdict(criterion=criterion,
            SCORE=score,
            score_value=score_value,
            REASONING=reasoning,
            EVIDENCE=evidence,
            SUGGESTIONS=suggestions)

    def _generate_summary(self,
        verdicts: List[JudgeVerdict],
        overall_score: float,
        passed: bool) -> str:
        """Generate evaluation summary.

        Args:
            verdicts: All verdicts
            overall_score: Overall score
            passed: Whether evaluation passed

        Returns:
            Summary string
        """
        status = 'PASSED' if passed else 'FAILED'
        excellent = sum((1 for v in verdicts if v.score == JudgmentScore.EXCELLENT))
        good = sum((1 for v in verdicts if v.score == JudgmentScore.GOOD))
        acceptable = sum((1 for v in verdicts if v.score == JudgmentScore.ACCEPTABLE))
        poor = sum((1 for v in verdicts if v.score == JudgmentScore.POOR))
        unacceptable = sum((1 for v in verdicts if v.score == JudgmentScore.UNACCEPTABLE))
        summary_parts = [f'Evaluation {status} (Score: {overall_score:.2f})',
            f'Excellent: {excellent}, Good: {good}, Acceptable: {acceptable}, Poor: {poor}, Unacceptable: {unacceptable}']
        if not passed:
            failing = [v.criterion.value for v in verdicts if v.score in {JudgmentScore.POOR, JudgmentScore.UNACCEPTABLE}]
            summary_parts.append(f"Failing criteria: {', '.join(failing)}")
        return ' | '.join(summary_parts)

def create_judge_evaluator(llm_client: Optional[Callable[[str],
    Awaitable[str]]]=None,
    pass_threshold: float=0.7) -> JudgeEvaluator:
    """Factory function to create judge evaluator.

    Args:
        llm_client: LLM client function
        pass_threshold: Pass threshold

    Returns:
        JudgeEvaluator instance
    """
    return JudgeEvaluator(llm_client=llm_client, pass_threshold=pass_threshold)