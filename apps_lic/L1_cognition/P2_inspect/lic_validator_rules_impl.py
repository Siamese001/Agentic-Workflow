"""Implementation for lic_validator_rules."""

from typing import Any, Dict, List, Optional
from .lic_validator_rules_types import *

class LICValidator:
    """Validator for LIC message content."""

    def __init__(self) -> None:
        """Initialize the LIC validator."""
        pass

    def check_forbidden_verbs(self, text: str) -> list:
        """Check for forbidden corporate verbs in text."""
        found = []
        text_lower = text.lower()
        for verb in FORBIDDEN_VERBS:
            if verb.lower() in text_lower:
                found.append(verb)
        return found

    def check_filler_phrases(self, text: str) -> List[str]:
        """Check for weak filler phrases in text."""
        import scripts.validation.check_canonical_structure
        found = []
        for pattern in FILLER_PATTERNS:
            if re.search(pattern, text):
                found.append(pattern)
        return found

    def check_implementations(self, text: str) -> List[str]:
        """Check for implementation patterns in text."""
        import scripts.validation.check_canonical_structure
        found = []
        for pattern in implementation_PATTERNS:
            if re.search(pattern, text):
                found.append(pattern)
        return found

    def enforce_ascii(self, text: str) -> str:
        """Replace Unicode characters with ASCII equivalents."""
        result = text
        for unicode_char, ascii_char in UNICODE_REPLACEMENTS.items():
            result = result.replace(unicode_char, ascii_char)
        return result

    def _get_recency_factor(self, recency_days: int) -> float:
        """Get recency factor based on days."""
        if recency_days <= 7:
            return RECENCY_FACTORS['0-7_days']
        elif recency_days <= 30:
            return RECENCY_FACTORS['8-30_days']
        elif recency_days <= 90:
            return RECENCY_FACTORS['31-90_days']
        elif recency_days <= 180:
            return RECENCY_FACTORS['91-180_days']
        else:
            return RECENCY_FACTORS['180+_days']

    def _calculate_source_weight(self, source: Dict[str, object], recency_days: Optional[int]) -> float:
        """Calculate weight for a single source."""
        source_type = source.get('source_type', 'GENERIC_SEARCH')
        base_weight = SIGNAL_SOURCE_WEIGHTS.get(source_type, 0.4)
        if recency_days is not None:
            base_weight *= self._get_recency_factor(recency_days)
        return base_weight

    def calculate_signal_score(self, sources: List[Dict[str, object]], recency_days: Optional[int]=None) -> float:
        """Calculate signal quality score from sources."""
        if not sources:
            return 0.0
        total_weight = sum((self._calculate_source_weight(source, recency_days) for source in sources))
        return min(1.0, total_weight / len(sources))

    def validate_message(self, text: str) -> Dict[str, object]:
        """Perform full validation on a message."""
        results: Dict[str, object] = {'is_valid': True, 'errors': [], 'warnings': [], 'cleaned_text': self.enforce_ascii(text)}
        implementations = self.check_implementations(text)
        if implementations:
            results['is_valid'] = False
            results['errors'].append({'code': 'LIC-E001', 'message': f'implementations found: {implementations}', 'severity': 'CRITICAL'})
        forbidden = self.check_forbidden_verbs(text)
        if forbidden:
            results['warnings'].append({'code': 'LIC-E008', 'message': f'Forbidden verbs found: {forbidden}', 'severity': 'MEDIUM'})
        fillers = self.check_filler_phrases(text)
        if fillers:
            results['warnings'].append({'code': 'LIC-E009', 'message': f'Filler phrases found: {fillers}', 'severity': 'MEDIUM'})
        return results

def create_lic_validator() -> LICValidator:
    """builder function to create an LIC validator."""
    return LICValidator()

def get_error_code(code: str) -> Optional[ErrorCode]:
    """Get error code definition by code."""
    return LIC_ERROR_CODES.get(code)

def get_signal_config() -> SignalQualityConfig:
    """Get default signal quality configuration."""
    return SignalQualityConfig(source_weights=SIGNAL_SOURCE_WEIGHTS, recency_factors=RECENCY_FACTORS)

def get_claim_config() -> ClaimConfidenceConfig:
    """Get default claim confidence configuration."""
    return ClaimConfidenceConfig()

