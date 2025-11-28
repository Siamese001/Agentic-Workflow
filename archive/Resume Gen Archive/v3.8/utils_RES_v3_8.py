# File: utils_RES_v3_8.py
# Version: 3.8.0 - Complete V3.8 Migration
# Utilities module for Resume Workflow
# Contains logging, text utilities, data loading, and helper functions
#
# V3.8 TOOL INTEGRATION:
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
from dataclasses import asdict

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None  # Add a placeholder for type hints

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None  # Placeholder
    cosine_similarity = None  # Placeholder

# Import required classes from other modules
from models_RES import ThematicAnalysis, ValidationResult, ValidationSeverity

# V3.8 Migration: Import from config_RES_v3_8
from config_RES_v3_8 import (
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


def setup_workflow_logging(workflow_id: Optional[str] = None, 
                         log_file_path: Optional[str] = None, 
                         test_mode: bool = False) -> Tuple[logging.Logger, str]:
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
            test_mode = True  # Fallback to console-only
    
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
        invalid_starts = ["At ", "As ", "In ", "The ", "This "]
        return not any(text.startswith(start) for start in invalid_starts)

    @staticmethod
    def detect_intro_phrases(text: str) -> List[str]:
        """
        Detects common introductory phrases that should be avoided.
        """
        intro_patterns = [
            r"^(At|As|In|The|This)\s+\w+",
            r"^(During my time|While working|As a)",
            r"^(I am|I was|I have been)",
            r"^(Responsible for|Tasked with)"
        ]
        
        found_phrases = []
        for pattern in intro_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found_phrases.append(match.group(0))
        
        return found_phrases


# Create global instance for convenience
text_utils = TextUtils()


# ============================================================================
# TEXT SANITIZATION
# ============================================================================

class TextSanitizer:
    """Sanitizes LLM-generated text to remove artifacts."""
    
    @staticmethod
    def remove_llm_artifacts(text: str) -> str:
        """
        Removes common LLM artifacts from generated text.
        This includes:
        - Markdown code fences
        - JSON wrapper
        - Common phrases like "Here's", "I'll", etc.
        """
        if not text:
            return text
        
        # Remove markdown fences
        text = TextUtils.strip_markdown_fences(text)
        
        # Remove JSON wrapper if present
        if text.startswith('{') and text.endswith('}'):
            try:
                # Try to parse as JSON and extract text fields
                data = json.loads(text)
                if isinstance(data, dict):
                    # Look for common text fields
                    for key in ['text', 'content', 'result', 'output']:
                        if key in data:
                            text = data[key]
                            break
            except:
                pass  # Not valid JSON, keep as is
        
        # Remove common LLM prefixes
        llm_prefixes = [
            r"^Here's?\s+",
            r"^I'll\s+",
            r"^I've\s+",
            r"^Let me\s+",
            r"^Sure,?\s+",
            r"^Certainly,?\s+",
            r"^Of course,?\s+"
        ]
        
        for prefix in llm_prefixes:
            text = re.sub(prefix, '', text, flags=re.IGNORECASE)
        
        # Remove quotes if entire text is quoted
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        return text.strip()
    
    @staticmethod
    def sanitize_bullet_point(text: str) -> str:
        """
        Sanitizes a bullet point text.
        Removes leading dashes/bullets and normalizes spacing.
        """
        if not text:
            return text
        
        # Remove leading bullet markers
        text = re.sub(r'^[-•*·]\s*', '', text.strip())
        
        # Normalize whitespace
        text = TextUtils.normalize_whitespace(text)
        
        return text
    
    @staticmethod
    def clean_section_text(text: str) -> str:
        """
        Cleans text for a resume section.
        Removes artifacts but preserves formatting.
        """
        if not text:
            return text
        
        # Remove LLM artifacts
        text = TextSanitizer.remove_llm_artifacts(text)
        
        # Remove excessive newlines but preserve paragraph breaks
        text = TextUtils.remove_extra_newlines(text)
        
        return text.strip()


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

class DuplicateDetector:
    """Detects duplicate or near-duplicate content using TF-IDF similarity."""
    
    def __init__(self, threshold: float = 0.85):
        """
        Initialize duplicate detector.
        
        Args:
            threshold: Similarity threshold for duplicate detection (0-1)
        """
        self.threshold = threshold
        
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 3)
            )
        else:
            self.vectorizer = None
    
    def find_duplicates(self, texts: List[str]) -> List[Tuple[str, str, float]]:
        """
        Find duplicate pairs in a list of texts.
        
        Returns:
            List of (text1, text2, similarity_score) tuples
        """
        if not SKLEARN_AVAILABLE:
            logging.warning("Sklearn not available - duplicate detection disabled")
            return []
        
        if len(texts) < 2:
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
    
    def find_duplicates_in_list(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Find duplicates and return detailed information.
        
        Returns:
            List of dictionaries with duplicate information
        """
        duplicates = self.find_duplicates(texts)
        
        result = []
        for text1, text2, score in duplicates:
            result.append({
                "text1": text1[:100] + "..." if len(text1) > 100 else text1,
                "text2": text2[:100] + "..." if len(text2) > 100 else text2,
                "similarity": round(score, 3)
            })
        
        return result


# ============================================================================
# SIGNAL SCORING
# ============================================================================

def calculate_signal_score(
    generated_content: str,
    thematic_analysis: ThematicAnalysis,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculates a 'signal score' based on theme and keyword presence.
    
    Args:
        generated_content: The generated text to score
        thematic_analysis: Theme analysis containing keywords and themes
        weights: Optional weights for different components
        
    Returns:
        Signal score between 0 and 1
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
    if thematic_analysis.primary_theme:
        primary_theme = thematic_analysis.primary_theme.get('name', '').lower()
        if primary_theme and primary_theme in content_lower:
            score += weights.get("primary_theme", 0.5)

    # 2. Primary Keywords
    if thematic_analysis.primary_theme:
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


# ============================================================================
# TELEMETRY LOGGING
# ============================================================================

class TelemetryLogger:
    """
    Logs telemetry data to a structured JSONL file for analysis.
    V3.8 enhanced version with better error handling.
    """
    def __init__(self, log_path: str = None):
        if log_path is None:
            log_path = str(CACHE_DIR / "telemetry_log.jsonl")
        self.log_path = log_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        log_dir = os.path.dirname(self.log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    def log(self, telemetry_data: Any):
        """Logs a telemetry event."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": type(telemetry_data).__name__,
                "data": asdict(telemetry_data) if hasattr(telemetry_data, '__dataclass_fields__') else str(telemetry_data)
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
    
    Args:
        reasoning_config: Configuration for reasoning strategies
        section_id: ID of the section being processed
        
    Returns:
        Dictionary of API parameters
    """
    params = {}
    
    if reasoning_config.self_consistency > 1:
        # In a real system, this might trigger multiple parallel calls
        # For Gemini, we might adjust temperature for diversity
        params["temperature_adjustment"] = 0.2
    
    if reasoning_config.tot_branches > 1:
        # Suggests a request for more diverse outputs
        params["top_k"] = 50
    
    # Add section-specific parameters
    params["section_id"] = section_id
    
    return params


def enhance_system_prompt_with_reasoning(
    system_prompt: str,
    reasoning_config: ReasoningConfig
) -> str:
    """
    Enhances a system prompt with reasoning directives based on the config.
    
    Args:
        system_prompt: Base system prompt
        reasoning_config: Configuration for reasoning strategies
        
    Returns:
        Enhanced system prompt
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
    
    Args:
        base_prompt: Base generation prompt
        constraints: Constraints dictionary with min/max values
        attempt: Current attempt number (1-indexed)
        
    Returns:
        Enhanced prompt with reinforced constraints
    """
    if attempt <= 1:
        return base_prompt  # No reinforcement on first attempt

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
    
    if 'required_keywords' in constraints:
        constraint_lines.append(
            f"**Required Keywords:** Must include ALL of: {', '.join(constraints['required_keywords'])}"
        )
    
    if 'forbidden_phrases' in constraints:
        constraint_lines.append(
            f"**Forbidden Phrases:** Must NOT include: {', '.join(constraints['forbidden_phrases'])}"
        )

    if not constraint_lines:
        return base_prompt  # No constraints to reinforce
    
    return (
        base_prompt +
        reinforcement_header +
        "\n".join(constraint_lines) +
        reinforcement_footer
    )


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # File utilities
    'create_directory_if_missing',
    'sanitize_filename',
    
    # Logging
    'WorkflowLogFilter',
    'setup_workflow_logging',
    'TelemetryLogger',
    
    # Text utilities
    'TextUtils',
    'text_utils',
    'TextSanitizer',
    
    # Duplicate detection
    'DuplicateDetector',
    
    # Signal scoring
    'calculate_signal_score',
    
    # Reasoning utilities
    'reasoning_config_to_api_params',
    'enhance_system_prompt_with_reasoning',
    'build_generation_prompt_with_reinforced_constraints',
    
    # Feature flags
    'GEMINI_AVAILABLE',
    'SKLEARN_AVAILABLE'
]
