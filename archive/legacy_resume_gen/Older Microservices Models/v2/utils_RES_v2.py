# File: utils_RES_v2.py
# Version: 17.01 (Patched)
# Utilities module for Resume Workflow
# Contains logging, text utilities, data loading, and helper functions
#
# V2 TOOL INTEGRATION:
# - TextSanitizer: Used in HOP-4 (generation loop step 4)
# - CodeInterpreterTool: Used for Macro ToT evaluation and deterministic operations
# - DuplicateDetector: Used in HOP-2 (enrichment)
# - WorkflowLogFilter: Used by TraceRegistry/logging system
# - TextUtils: Word counting and text manipulation for validation

import hashlib
import json
import logging
import os
import re
import subprocess
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
from models_RES import ThematicAnalysis, ValidationResult, ValidationSeverity
# --- FIX: Import DATA_DIR and CACHE_DIR ---
from config_RES_v2 import (
    ReasoningConfig, RAGConfig, PROMPT_ADDENDUM_CONFIG, 
    DEFAULT_GENERATION_TEMPERATURE, DATA_DIR, CACHE_DIR
)

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


def setup_workflow_logging(workflow_id: Optional[str] = None, log_file_path: Optional[str] = None, test_mode: bool = False) -> Tuple[logging.Logger, str]:
    """
    Set up logging for the workflow with both console and file handlers.
    
    Args:
        workflow_id: Optional workflow identifier
        log_file_path: Specific path for the log file
        test_mode: If True, disable file logging
        
    Returns:
        Tuple of (logger, log_filename)
    """
    if workflow_id is None:
        workflow_id = str(uuid.uuid4())[:8]
    
    log_filename = log_file_path
    if not log_filename:
        # Fallback if path not provided (e.g., direct util testing)
        log_dir = CACHE_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_filename = str(log_dir / f"workflow_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    
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
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_filename)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(log_formatter)
            file_handler.addFilter(WorkflowLogFilter(workflow_id))
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.error(f"Failed to create file logger at {log_filename}: {e}")
            test_mode = True # Fallback to console-only
    
    logger = logging.getLogger(__name__)
    logger.info(f"H0_INFO - Workflow logging initialized. ID: {workflow_id}, Log file: {log_filename if not test_mode else 'DISABLED'}")
    
    return logger, log_filename


# ============================================================================
# TEXT UTILITIES
# ============================================================================

class TextUtils:
    """Utilities for text processing, counting, and manipulation."""

    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Counts the number of sentences in a text.
        Uses simple heuristic: split on '.', '!', '?'
        """
        if not text:
            return 0
        sentence_endings = re.findall(r'[.!?]+', text)
        return len(sentence_endings) if sentence_endings else 1

    @staticmethod
    def count_words(text: str) -> int:
        """
        Counts words in text using simple whitespace split.
        More accurate than regex for most resume text.
        """
        if not text:
            return 0
        return len(text.split())

    @staticmethod
    def count_words_ms_word_style(text: str) -> int:
        """
        Counts words similar to MS Word:
        - Split on whitespace
        - Count hyphenated words as one word
        """
        if not text:
            return 0
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text.strip())
        return len(text.split())

    @staticmethod
    def extract_first_n_words(text: str, n: int) -> str:
        """Extracts the first N words from text."""
        words = text.split()
        return ' '.join(words[:n])

    @staticmethod
    def truncate_to_word_count(text: str, max_words: int) -> str:
        """Truncates text to a maximum word count, preserving whole words."""
        words = text.split()
        if len(words) <= max_words:
            return text
        return ' '.join(words[:max_words])

    @staticmethod
    def strip_markdown_fences(text: str) -> str:
        """Removes markdown code fences from text."""
        # Remove opening fence with optional language identifier
        text = re.sub(r'^```\w*\n?', '', text, flags=re.MULTILINE)
        # Remove closing fence
        text = re.sub(r'\n?```$', '', text, flags=re.MULTILINE)
        return text.strip()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalizes whitespace in text (collapses multiple spaces/newlines)."""
        # Replace multiple whitespace chars with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def remove_extra_newlines(text: str, max_consecutive: int = 2) -> str:
        """Removes excess consecutive newlines."""
        pattern = r'\n{' + str(max_consecutive + 1) + r',}'
        return re.sub(pattern, '\n' * max_consecutive, text)

    @staticmethod
    def is_valid_sentence_start(text: str) -> bool:
        """
        Checks if text starts with a valid sentence beginning.
        Invalid starts: "At ", "As ", "In ", "The ", "This "
        """
        forbidden_starts = ['At ', 'As ', 'In ', 'The ', 'This ', 'In my role', 'At the company']
        return not any(text.startswith(start) for start in forbidden_starts)

    @staticmethod
    def remove_forbidden_sentence_starts(text: str) -> str:
        """Removes forbidden sentence starts and recapitalizes."""
        forbidden_patterns = [
            r'^At\s+\w+,?\s+',
            r'^As\s+\w+,?\s+',
            r'^In\s+my\s+role,?\s+',
            r'^In\s+this\s+role,?\s+',
        ]
        
        for pattern in forbidden_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                if text:
                    text = text[0].upper() + text[1:]
                break
        
        return text

    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """
        Extracts significant keywords from text.
        Filters out common stop words and short words.
        """
        # Simple stop word list
        stop_words = {
            'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have',
            'has', 'had', 'are', 'was', 'were', 'been', 'being', 'will'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter by length and stop words
        keywords = [w for w in words if len(w) >= min_length and w not in stop_words]
        
        # Return unique keywords, preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        return unique_keywords

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculates cosine similarity between two texts using TF-IDF.
        Returns a score between 0.0 and 1.0.
        Requires scikit-learn.
        """
        if not SKLEARN_AVAILABLE:
            logging.warning("sklearn not available, returning 0.0 similarity")
            return 0.0
        
        if not text1 or not text2:
            return 0.0
        
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logging.warning(f"Error calculating similarity: {e}")
            return 0.0

    # --- PATCH: ADDED FUNCTIONS FOR SANITIZER ---
    @staticmethod
    def remove_conversational_fillers(text: str) -> str:
        """Removes common conversational filler phrases from the start of text."""
        fillers = [
            r"Here is the generated content:",
            r"Here is the requested resume section:",
            r"Here's the generated content:",
            r"Here's the generated section:",
            r"Certainly, here is the section:",
            r"Certainly, here you go:",
            r"Here is the content you requested:",
            r"Here is the output:",
            r"Here is the updated section:",
            r"Here is the text:",
        ]
        text_lower = text.lower()
        for filler in fillers:
            if text_lower.startswith(filler.lower()):
                text = text[len(filler):].lstrip()
                break # Only remove one filler from the start
        return text

    @staticmethod
    def remove_trailing_explanations(text: str) -> str:
        """Removes trailing 'Note:' or 'I have ensured...' meta-commentary."""
        text = re.sub(r"\s*\n\s*\n\s*Note:.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"\s*\n\s*\n\s*I have ensured.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
        return text

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Runs a single string through all sanitization rules.
        (Merged from sanitizer_RES_v2.py)
        """
        if not isinstance(text, str):
            return text
        
        sanitization_counts = defaultdict(int) # Local counter for logging if needed
        original_len = len(text)
        
        # Rule 1: Strip markdown fences (both leading and trailing)
        text_after_fences = TextUtils.strip_markdown_fences(text)
        if len(text_after_fences) < len(text):
            sanitization_counts["markdown_fences"] += 1
        
        # Rule 2: Remove conversational fillers
        text_after_fillers = TextUtils.remove_conversational_fillers(text_after_fences)
        if len(text_after_fillers) < len(text_after_fences):
            sanitization_counts["conversational_fillers"] += 1

        # Rule 3: Remove trailing explanations
        text_after_explanations = TextUtils.remove_trailing_explanations(text_after_fillers)
        if len(text_after_explanations) < len(text_after_fillers):
            sanitization_counts["trailing_explanations"] += 1
            
        return text_after_explanations.strip()
    # --- END PATCH ---

# --- Create a global instance for easy access ---
text_utils = TextUtils()


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

class DuplicateDetector:
    """Detects duplicate or near-duplicate text."""

    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer() if SKLEARN_AVAILABLE else None

    def find_duplicates_in_list(self, texts: List[str]) -> List[Tuple[str, str, float]]:
        """
        Finds duplicates within a list of strings.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of tuples (text1, text2, similarity_score) for duplicates
        """
        if not SKLEARN_AVAILABLE or len(texts) < 2:
            return []
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            cosine_sim_matrix = cosine_similarity(tfidf_matrix)
            
            duplicates = []
            checked_pairs = set()
            
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    if (i, j) in checked_pairs:
                        continue
                    
                    similarity = cosine_sim_matrix[i, j]
                    
                    if similarity >= self.threshold:
                        duplicates.append((texts[i], texts[j], similarity))
                    
                    checked_pairs.add((i, j))
            
            return duplicates
            
        except Exception as e:
            logging.warning(f"Duplicate detection failed: {e}")
            return []


# ============================================================================
# SIGNAL SCORING
# ============================================================================

# --- PATCH: ADDED MISSING FUNCTION ---
def calculate_signal_score(
    generated_content: str,
    thematic_analysis: ThematicAnalysis,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculates a 'signal score' based on theme and keyword presence.
    This was referenced by validator_RES_v2.py but was missing.
    """
    if not generated_content or not thematic_analysis:
        return 0.0

    if weights is None:
        weights = {
            "primary_theme": 0.5,
            "primary_keywords": 0.3,
            "differentiators": 0.2
        }

    content_lower = generated_content.lower()
    score = 0.0

    # 1. Primary Theme
    primary_theme = thematic_analysis.primary_theme.get('name', '').lower()
    if primary_theme and primary_theme in content_lower:
        score += weights.get("primary_theme", 0.5)

    # 2. Primary Keywords
    primary_keywords = thematic_analysis.primary_theme.get('keywords', [])
    if primary_keywords:
        found_keywords = sum(1 for kw in primary_keywords if kw.lower() in content_lower)
        keyword_score = found_keywords / len(primary_keywords)
        score += keyword_score * weights.get("primary_keywords", 0.3)

    # 3. Differentiator Keywords
    differentiators = []
    comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
    if comp_intel:
        differentiators = getattr(comp_intel, 'differentiator_keywords', [])
    
    if differentiators:
        found_diffs = sum(1 for kw in differentiators if kw.lower() in content_lower)
        diff_score = found_diffs / len(differentiators)
        score += diff_score * weights.get("differentiators", 0.2)

    return min(1.0, score)
# --- END PATCH ---


# ============================================================================
# TELEMETRY LOGGING
# ============================================================================

class TelemetryLogger:
    """
    Logs telemetry data to a structured JSONL file for analysis.
    This is a stub implementation.
    """
    def __init__(self, log_path: str = None):
        if log_path is None:
            log_path = str(CACHE_DIR / "telemetry_log.jsonl")
        self.log_path = log_path
        self.logger = logging.getLogger(__name__)

    def log(self, telemetry_data: Any):
        """Logs a telemetry event."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": type(telemetry_data).__name__,
                "data": asdict(telemetry_data) if hasattr(telemetry_data, '_asdict') else str(telemetry_data)
            }
            with open(self.log_path, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write telemetry log: {e}")


# ============================================================================
# REASONING & PROMPT UTILITIES
# ============================================================================

def reasoning_config_to_api_params(
    reasoning_config: ReasoningConfig,
    section_id: str
) -> Dict[str, Any]:
    """
    Converts a ReasoningConfig dataclass into API parameters.
    (This is a stub, as the full logic depends on the specific API)
    """
    # This is a simplified example. In a real system, this would
    # configure more complex parameters like multi-shot prompts,
    # or chain-of-thought instructions.
    
    params = {}
    
    if reasoning_config.self_consistency > 1:
        # In a real system, this might trigger multiple parallel calls
        # For Gemini, we might adjust temperature for diversity
        params["temperature_adjustment"] = 0.2
    
    if reasoning_config.tot_branches > 1:
        # Suggests a request for more diverse outputs
        params["top_k"] = 50
    
    return params


def enhance_system_prompt_with_reasoning(
    system_prompt: str,
    reasoning_config: ReasoningConfig
) -> str:
    """
    Enhances a system prompt with reasoning directives based on the config.
    """
    if not reasoning_config:
        return system_prompt
    
    addendums = [PROMPT_ADDENDUM_CONFIG.HEADER]
    
    def get_directive(value, directives):
        for threshold, template in directives:
            if value >= threshold:
                return template
        return None

    # Chain-of-Thought
    cot_template = get_directive(reasoning_config.cot_min_paths, PROMPT_ADDENDUM_CONFIG.COT_DIRECTIVES)
    if cot_template:
        addendums.append(cot_template.format(cot=reasoning_config.cot_min_paths))

    # Tree-of-Thought (Breadth)
    tot_b_template = get_directive(reasoning_config.tot_branches, PROMPT_ADDENDUM_CONFIG.TOT_B_DIRECTIVES)
    if tot_b_template:
        addendums.append(tot_b_template.format(tot_b=reasoning_config.tot_branches))

    # Tree-of-Thought (Depth)
    tot_d_template = get_directive(reasoning_config.min_tot_depth, PROMPT_ADDENDUM_CONFIG.TOT_D_DIRECTIVES)
    if tot_d_template:
        addendums.append(tot_d_template.format(tot_d=reasoning_config.min_tot_depth))

    # Reflexion
    if reasoning_config.reflexion:
        reflexion_template = get_directive(reasoning_config.max_reflexion_loops, PROMPT_ADDENDUM_CONFIG.REFLEXION_DIRECTIVES)
        if reflexion_template:
            addendums.append(reflexion_template.format(max_loops=reasoning_config.max_reflexion_loops))

    if len(addendums) > 1:
        addendums.append(PROMPT_ADDENDUM_CONFIG.FOOTER)
        return system_prompt + "\n" + "".join(addendums)
    
    return system_prompt


def build_generation_prompt_with_reinforced_constraints(
    base_prompt: str,
    constraints: Dict[str, Any],
    attempt: int
) -> str:
    """
    Enhances a base prompt with reinforced constraints for retries.
    This was referenced by artist_RES_v2.py but was missing.
    """
    if attempt <= 1:
        return base_prompt # No reinforcement on first attempt

    reinforcement_header = "\n\n--- CRITICAL: Previous attempt failed. Adhere to ALL constraints: ---\n"
    reinforcement_footer = "\n--- END CRITICAL CONSTRAINTS ---\n"
    
    constraint_lines = []
    
    if 'min_wc' in constraints and 'max_wc' in constraints:
        constraint_lines.append(
            f"**Word Count:** Must be *strictly* between {constraints['min_wc']} and {constraints['max_wc']} words."
        )
    
    if 'min_sc' in constraints and 'max_sc' in constraints:
        constraint_lines.append(
            f"**Sentence Count:** Must be *exactly* {constraints['min_sc']} to {constraints['max_sc']} sentences."
        )

    if not constraint_lines:
        return base_prompt # No constraints to reinforce
    
    return (
        base_prompt +
        reinforcement_header +
        "\n".join(constraint_lines) +
        reinforcement_footer
    )
