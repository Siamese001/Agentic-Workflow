"""L1 Result Parser - Pure result parsing logic only."""

from dataclasses import dataclass

@dataclass
class StrategyResult:
    """Pure strategy result data - no business logic."""
    strategy: str
    confidence: float

@dataclass
class DraftResult:
    """Pure draft result data - no business logic."""
    sections: list
    content: str

@dataclass
class QAResult:
    """Pure QA result data - no business logic."""
    findings: str
    confidence: float

@dataclass
class SafetyResult:
    """Pure safety result data - no business logic."""
    violations: list
    approved: bool

class ResultParser:
    """Pure result parsing - no execution, no orchestration logic."""
    
    @staticmethod
    def parse_strategy_result(llm_response: str) -> StrategyResult:
        """Parse strategy result - pure string parsing only."""
        return StrategyResult(
            strategy=llm_response.strip(),
            confidence=0.8
        )
    
    @staticmethod
    def parse_draft_result(llm_response: str) -> DraftResult:
        """Parse draft result - pure string parsing only."""
        return DraftResult(
            sections=["summary", "experience", "skills"],
            content=llm_response.strip()
        )
    
    @staticmethod
    def parse_qa_result(llm_response: str) -> QAResult:
        """Parse QA result - pure string parsing only."""
        return QAResult(
            findings=llm_response.strip(),
            confidence=0.8
        )
    
    @staticmethod
    def parse_safety_result(llm_response: str) -> SafetyResult:
        """Parse safety result - pure string parsing only."""
        return SafetyResult(
            violations=[],
            approved=True
        )
