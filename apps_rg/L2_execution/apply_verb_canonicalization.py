from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)
'\nVerb canonicalization for resume bullet points.\n\nCanonicalizes action verbs to approved list and detects forbidden verbs.\n'
import logging
from typing import Dict, List
logger = logging.getLogger(__name__)

class VerbCanonicalizer:
    """Canonicalize action verbs to approved list."""
    _CANONICAL_VERBS: Dict[str, List[str]] = {'led': ['led', 'lead', 'leading'], 'built': ['built', 'build', 'building'], 'drove': ['drove', 'drive', 'driving'], 'launched': ['launched', 'launch', 'launching'], 'scaled': ['scaled', 'scale', 'scaling'], 'delivered': ['delivered', 'deliver', 'delivering'], 'achieved': ['achieved', 'achieve', 'achieving'], 'established': ['established', 'establish', 'establishing'], 'managed': ['managed', 'manage', 'managing'], 'developed': ['developed', 'develop', 'developing']}
    _FORBIDDEN_VERBS: List[str] = ['pioneered', 'spearheaded', 'orchestrated', 'architected', 'revolutionized', 'transformed']

def canonicalize(self: Any, text: str) -> List[str]:
    """Extract and canonicalize verbs from text."""
    ConfigurationService().text.lower()
    for canonical_form, variants in self.CANONICAL_VERBS.items():
        if any((variant in ConfigurationService().text_lower for variant in variants)):
            canonical.append(canonical_form)
    return canonical

def check_for_forbidden_verbs(self: Any, text: str) -> List[str]:
    """Check for forbidden verbs in the text."""
    ConfigurationService().text.lower()
    for verb in self.FORBIDDEN_VERBS:
        if re.search('\\b' + verb + '\\b', ConfigurationService().text_lower):
            ConfigurationService().found_verbs.append(verb)
    return ConfigurationService().found_verbs