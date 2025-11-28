# File: utils.py
# Utilities module for Resume Workflow
# Contains logging, text utilities, data loading, and helper functions

import hashlib
import json
import logging
import os
import re
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Set

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None # Add a placeholder for type hints

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None # Placeholder
    cosine_similarity = None # Placeholder

# Import required classes from other modules
# Note: models and config are imported locally within functions or at the top
# of other modules to avoid circular dependencies at initialization.
from models_RES import ThematicAnalysis, ValidationResult
from config_RES import ReasoningConfig, RAGConfig, PROMPT_ADDENDUM_CONFIG, DEFAULT_GENERATION_TEMPERATURE

# ============================================================================
# FILE SYSTEM UTILITIES
# ============================================================================

def create_directory_if_missing(directory_path: str) -> None:
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Sanitizes a filename by removing or replacing invalid characters."""
    # Remove or replace characters that are invalid in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized if sanitized else "unnamed"


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

class WorkflowLogFilter(logging.Filter):
    """Log filter to add workflow_id to log records."""
    def __init__(self, workflow_id: str):
        super().__init__()
        self.workflow_id = workflow_id
    
    def filter(self, record):
        record.workflow_id = self.workflow_id
        return True


def setup_workflow_logging(workflow_id: Optional[str] = None, test_mode: bool = False) -> Tuple[logging.Logger, str]:
    """
    Set up logging for the workflow with both console and file handlers.
    
    Args:
        workflow_id: Optional workflow identifier
        test_mode: If True, disable file logging
        
    Returns:
        Tuple of (logger, log_filename)
    """
    if workflow_id is None:
        workflow_id = str(uuid.uuid4())[:8]
    
    log_filename = f"resume_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - [%(workflow_id)s] - %(message)s'
    log_formatter = logging.Formatter(log_format)
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_formatter)
    console_handler.addFilter(WorkflowLogFilter(workflow_id))
    root_logger.addHandler(console_handler)
    
    if not test_mode:
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_formatter)
        file_handler.addFilter(WorkflowLogFilter(workflow_id))
        root_logger.addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"H0_INFO - Workflow logging initialized. ID: {workflow_id}, Log file: {log_filename if not test_mode else 'DISABLED (test mode)'}")
    
    return logger, log_filename


def _load_json_data(filename: str, description: str) -> Dict:
    """
    Load JSON data from a file with error handling.
    
    Args:
        filename: Name of the JSON file to load
        description: Human-readable description of the file
        
    Returns:
        Dict containing the loaded JSON data
        
    Raises:
        FileNotFoundError: If file is not found
        json.JSONDecodeError: If JSON is invalid
    """
    # Try to find file relative to the script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        if not os.path.exists(filepath):
            # Fallback to current directory
            filepath = filename 
            if not os.path.exists(filepath):
                 raise FileNotFoundError
    except NameError:
        # Fallback if __file__ is not defined (e.g., in interactive)
        filepath = filename

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"Successfully loaded {description} from '{filepath}'.")
            return data
    except FileNotFoundError:
        logging.error(f"CRITICAL: {description} file not found at '{filepath}'. Halting.")
        raise FileNotFoundError(f"{description} file not found: {filepath}")
    except json.JSONDecodeError as e:
        logging.error(f"CRITICAL: Failed to decode JSON from {description} file '{filepath}': {e}. Halting.")
        raise json.JSONDecodeError(f"Failed to decode {description} file: {e.msg}", e.doc, e.pos)
    except Exception as e:
        logging.error(f"CRITICAL: An unexpected error occurred while loading {description} file '{filepath}': {e}. Halting.")
        raise e


# ============================================================================
# TEXT UTILITIES
# ============================================================================

class TextUtils:
    """Utilities for text processing, counting, and manipulation."""

    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count sentences in text, handling common abbreviations.
        
        Args:
            text: Input text
            
        Returns:
            Number of sentences
        """
        if not text or not text.strip():
            return 0

        abbrev_pattern = r'(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|e\.g|i\.e|Inc|Ltd|Corp)\.'
        text_protected = re.sub(
            abbrev_pattern,
            lambda m: m.group().replace('.', '<DOT>'),
            text,
            flags=re.IGNORECASE
        )

        sentences = re.split(r'[.!?]+', text_protected)

        sentences = [s.replace('<DOT>', '.').strip() for s in sentences if s.strip()]

        return len(sentences)

    @staticmethod
    def count_words_ms_word_style(text: str) -> int:
        """
        Count words using MS Word style counting.
        
        Args:
            text: Input text
            
        Returns:
            Number of words
        """
        if not text or not text.strip():
            return 0

        text = re.sub(r'\s+', ' ', text.strip())

        text = text.replace(' -- ', ' ').replace('—', ' ')

        words = text.split()

        return len(words)

    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text (alias for count_words_ms_word_style).
        
        Args:
            text: Input text
            
        Returns:
            Number of words
        """
        return TextUtils.count_words_ms_word_style(text)

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts using TF-IDF.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not SKLEARN_AVAILABLE:
            logging.error("sklearn not available. Cannot calculate text similarity.")
            return 0.0
        
        if not text1 or not text2:
            return 0.0

        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
            vectors = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
            return float(similarity)
        except Exception as e:
            logging.error(f"Similarity calculation failed: {e}")
            raise

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text by removing encoding issues and normalizing characters.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""

        replacements = {
            'â€œ': '"',   # Left double quote
            'â€': '"',    # Right double quote
            'â€˜': "'",   # Left single quote
            'â€™': "'",   # Right single quote / apostrophe
            'â€"': '-',   # En dash
            'â€"': '--',  # Em dash
            'â€¦': '...',
            'Â': '',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)

        text = text.replace('‘', "'").replace('’', "'")
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('–', '-').replace('—', '--')

        return text

    @staticmethod
    def strip_markdown_fences(text: str) -> str:
        """
        Remove markdown code fences from text.
        
        Args:
            text: Input text
            
        Returns:
            Text without markdown fences
        """
        if not text:
            return text

        fence_pattern = r"^\s*```(?:[a-z]*)?\s*\n?|\s*\n?```\s*$"
        cleaned = re.sub(fence_pattern, "", text, flags=re.MULTILINE).strip()
        return cleaned

    @staticmethod
    def format_validation_message(validation_result: ValidationResult, context_cache: dict = None) -> str:
        """
        Format a validation message with context.
        
        Args:
            validation_result: ValidationResult object
            context_cache: Optional context cache dict
            
        Returns:
            Formatted message string
        """
        try:
            details = getattr(validation_result, 'details', {}) or {}

            if context_cache:
                details = {**context_cache.get(validation_result.rule_id, {}), **details}

            msg_template = validation_result.message

            if callable(msg_template):
                return str(msg_template(defaultdict(lambda: '[N/A]', **details)))

            return str(msg_template).format_map(defaultdict(lambda: '[N/A]', **details))

        except Exception as e:
            logging.warning(f"Error formatting message for rule {validation_result.rule_id}: {e}")
            return f"[Error formatting message for {validation_result.rule_id}]"


# Global instance
text_utils = TextUtils()

# ============================================================================
# DATA UTILITIES (DuplicateDetector)
# ============================================================================

class DuplicateDetector:
    """Detects duplicate content in resume bullets."""

    def __init__(self):
        if not SKLEARN_AVAILABLE:
            logging.error("sklearn not available. DuplicateDetector functionality will be limited/disabled.")
            self.vectorizer = None
        else:
            self.vectorizer = TfidfVectorizer(stop_words='english', norm='l2')

    def find_duplicates(
        self,
        bullets: List[Dict],
        threshold: float = 0.9
    ) -> List[Tuple[int, int, float]]:
        """
        Find bullets with cosine similarity >= threshold.
        Returns: List of (index1, index2, similarity_score)
        """
        if self.vectorizer is None:
            logging.warning("Skipping duplicate detection: sklearn/TfidfVectorizer not available.")
            return []
        
        duplicates = []

        for i in range(len(bullets)):
            for j in range(i + 1, len(bullets)):
                similarity = self._calculate_cosine_similarity(
                    bullets[i].get("bullet_text", ""),
                    bullets[j].get("bullet_text", "")
                )

                if similarity >= threshold:
                    duplicates.append((i, j, similarity))

        return duplicates

    def _calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """Helper to call the global text_utils similarity function."""
        return text_utils.calculate_similarity(text1, text2)

# ============================================================================
# REASONING UTILITIES
# ============================================================================

def reasoning_config_to_api_params(reasoning_config: ReasoningConfig) -> dict:
    """
    Convert ReasoningConfig to API parameters for Gemini.
    
    Args:
        reasoning_config: ReasoningConfig instance
        
    Returns:
        Dict of API parameters including generation_config and prompt addendum
    """
    logger = logging.getLogger(__name__)

    params = _get_normalized_reasoning_params(reasoning_config)

    temperature = DEFAULT_GENERATION_TEMPERATURE

    allocated_max_tokens = _allocate_tokens_from_depth(params['tot_d'], params['cot'], params['sc'])
    try:
         # Attempt to get max_tokens from a default RAGConfig instance
         absolute_max_tokens = RAGConfig().max_tokens
    except Exception:
         logging.warning("RAGConfig not found or failed to init, using default absolute max_tokens=30000.")
         absolute_max_tokens = 30000

    final_max_tokens = min(allocated_max_tokens, absolute_max_tokens)

    prompt_addendum = _build_reasoning_prompt_addendum(params)

    try:
        logger.debug(
            f"Reasoning Params for API: cot={params['cot']}, tot_b={params['tot_b']}, tot_d={params['tot_d']}, "
            f"sc={params['sc']}, reflexion={params['reflexion']}, max_loops={params['max_loops']}, "
            f"temp={temperature}, allocated_max_tokens={allocated_max_tokens}, final_max_tokens={final_max_tokens}"
        )
    except Exception:
        pass

    if not GEMINI_AVAILABLE:
        logging.error("Gemini API not available. Cannot create GenerationConfig.")
        # Return a structure that won't crash the calling function, though API calls will fail
        return {
            "generation_config": None,
            "system_prompt_addendum": prompt_addendum,
            **params
        }

    return {
        "generation_config": genai.GenerationConfig(temperature=temperature, max_output_tokens=final_max_tokens),
        "system_prompt_addendum": prompt_addendum,
        **params
    }


def _get_normalized_reasoning_params(config: ReasoningConfig) -> Dict:
    """
    Normalize and clamp reasoning parameters.
    
    Args:
        config: ReasoningConfig instance
        
    Returns:
        Dict of normalized parameters
    """
    config = config or ReasoningConfig.DEFAULT
    tot_b = config.tot_branches if config.tot_branches is not None else 3
    tot_d = config.min_tot_depth if config.min_tot_depth is not None else 3
    sc = config.self_consistency if config.self_consistency is not None else 12
    reflexion = config.reflexion if config.reflexion is not None else True
    max_loops = config.max_reflexion_loops if config.max_reflexion_loops is not None else 2

    sc_clamped = max(1, min(sc, 8))

    return {
        "cot": max(2, min(config.cot_min_paths if config.cot_min_paths is not None else 3, 8)),
        "tot_b": max(2, min(tot_b, 6)),
        "tot_d": max(2, min(tot_d, 5)),
        "sc": sc_clamped,
        "reflexion": reflexion,
        "max_loops": max(1, min(max_loops, 5))
    }


def _allocate_tokens_from_depth(tot_d: int, cot: int, sc: int) -> int:
    """
    Allocate max tokens based on reasoning depth and complexity.
    
    Args:
        tot_d: Tree-of-thought depth
        cot: Chain-of-thought paths
        sc: Self-consistency runs
        
    Returns:
        Allocated max tokens
    """
    base_limit = 16384
    high_sc_limit = 24000
    mid_complex_limit = 26000
    high_complex_limit = 28000
    max_complex_limit = 30000

    if tot_d >= 4:
        max_tokens = max_complex_limit
    elif tot_d >= 3 and cot >= 5:
        max_tokens = high_complex_limit
    elif tot_d >= 3 or cot >= 5:
        max_tokens = mid_complex_limit
    elif sc >= 15:
        max_tokens = high_sc_limit
    else:
        max_tokens = base_limit
    
    try:
        rag_config_max = RAGConfig().max_tokens
    except Exception:
        rag_config_max = 30000 # Default fallback
        
    return max(base_limit, min(max_tokens, rag_config_max))


def _build_reasoning_prompt_addendum(params: Dict) -> str:
    """
    Build the reasoning prompt addendum from parameters.
    
    Args:
        params: Dict of reasoning parameters
        
    Returns:
        Prompt addendum string
    """
    addendum = PROMPT_ADDENDUM_CONFIG.HEADER

    def find_directive(directives: List[Tuple[int, str]], value: int) -> str:
        """Find the appropriate directive based on threshold."""
        for threshold, text in directives:
            if value >= threshold:
                return text
        return ""

    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.COT_DIRECTIVES, params.get('cot', 0)).format(cot=params.get('cot'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_B_DIRECTIVES, params.get('tot_b', 0)).format(tot_b=params.get('tot_b'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_D_DIRECTIVES, params.get('tot_d', 0)).format(tot_d=params.get('tot_d'))

    if params.get('reflexion'):
        addendum += find_directive(PROMPT_ADDENDUM_CONFIG.REFLEXION_DIRECTIVES, params.get('max_loops', 0)).format(max_loops=params.get('max_loops'))

    addendum += PROMPT_ADDENDUM_CONFIG.FOOTER
    return addendum


def enhance_system_prompt_with_reasoning(
    base_system_prompt: str,
    reasoning_config: ReasoningConfig,
    section_id: str = "UNKNOWN"
) -> str:
    """
    Enhance a system prompt with reasoning configuration directives.

    Args:
        base_system_prompt: Original system prompt (e.g., "You are an expert...")
        reasoning_config: ReasoningConfig instance
        section_id: For logging (e.g., "K.1", "K.4")

    Returns:
        Enhanced system prompt with reasoning directives appended
    """
    api_params = reasoning_config_to_api_params(reasoning_config)
    enhanced = base_system_prompt + api_params["system_prompt_addendum"]
    return enhanced


# ============================================================================
# SIGNAL SCORING (MOVED FROM WORKFLOW.PY)
# ============================================================================

def calculate_signal_score(text_content, thematic_analysis: ThematicAnalysis) -> float:
    """
    Calculate signal score based on JD keyword presence in content.
    (Moved from workflow.py to fix circular dependency)
    
    Args:
        text_content: Text content to analyze (str, list, or dict)
        thematic_analysis: ThematicAnalysis with keywords
        
    Returns:
        Signal score (0.0 to 1.0)
    """
    if not text_content:
        return 0.0

    if isinstance(text_content, (list, dict)):
        text = str(text_content).lower()
    else:
        text = str(text_content).lower()

    if not text:
        return 0.0

    try:
        differentiators = set()
        if hasattr(thematic_analysis, 'competitive_intelligence') and thematic_analysis.competitive_intelligence:
            # Check if it's the dataclass or a dict
            if hasattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords'):
                differentiators = set(getattr(thematic_analysis.competitive_intelligence, 'differentiator_keywords', []) or [])
            elif isinstance(thematic_analysis.competitive_intelligence, dict):
                differentiators = set(thematic_analysis.competitive_intelligence.get('differentiator_keywords', []) or [])

        primary_theme_data = thematic_analysis.primary_theme or {}
        primary_words = set(primary_theme_data.get('keywords', []))

        all_jd_words = differentiators.union(primary_words)

    except (AttributeError, KeyError, TypeError) as e:
        logging.warning(f"Error accessing keywords in thematic_analysis for signal score calculation: {e}")
        return 0.0

    if not all_jd_words:
        return 0.0

    words_in_text = set(re.findall(r'\b\w+\b', text))
    matches = words_in_text.intersection(all_jd_words)
    score = len(matches) / 10.0

    primary_matches = words_in_text.intersection(primary_words)
    score += len(primary_matches) * 0.1

    return min(1.0, score)


# ============================================================================
# TELEMETRY
# ============================================================================

class TelemetryLogger:
    """Logger for RAG telemetry data."""
    
    def __init__(self, log_dir: str = "/tmp/rag_telemetry"):
        """
        Initialize the telemetry logger.
        Args:
            log_dir: The directory to write log files to.
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def log(self, telemetry: 'RAGTelemetry'):
        """
        Logs a RAGTelemetry object to a file.
        
        Args:
            telemetry: The RAGTelemetry object to log.
        """
        log_file = os.path.join(
            self.log_dir,
            f"rag_telemetry_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )

        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(telemetry.to_dict()) + '\n')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to write telemetry: {e}")