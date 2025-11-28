# File: utils_RES.py
# Version: 16.32 - Centralized Path Management
# Utilities module for Resume Workflow
# Contains logging, text utilities, data loading, and helper functions

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
from config_RES import (
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


# Create a global instance for convenience
text_utils = TextUtils()

class TextSanitizer:
    """
    Sanitizes text content to remove unwanted artifacts.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self):
        self.sanitization_counts = defaultdict(int)

    def sanitize_text(self, text: str) -> str:
        """
        Runs a single string through all sanitization rules.
        """
        if not isinstance(text, str):
            return text
        
        original_text = text
        
        # Rule 1: Strip markdown fences
        text = text_utils.strip_markdown_fences(text)
        if len(text) < len(original_text):
            self.sanitization_counts["markdown_fences"] += 1

        # Rule 2: Remove conversational fillers
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
                self.sanitization_counts["conversational_fillers"] += 1
                break # Only remove one filler from the start

        # Rule 3: Remove trailing explanations
        # (More complex, as it risks removing real content)
        # This is a safer, more targeted removal
        text = re.sub(r"\n\nNote: This content.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"\n\nI have ensured this meets.*$", "", text, flags=re.DOTALL | re.IGNORECASE)

        return text.strip()

    def sanitize_buffer(self, buffer: 'ImmutableStagingBuffer') -> Tuple[List[ValidationResult], Dict[str, Any]]:
        """
        Recursively sanitizes all string values within the staging buffer's data.
        
        Args:
            buffer: The locked ImmutableStagingBuffer
            
        Returns:
            A tuple of (validation_results, sanitized_data_dict)
        """
        if not buffer.is_locked():
            return [ValidationResult(
                rule_id="SANITIZATION_BUFFER_UNLOCKED",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Sanitization must run on a locked buffer."
            )], buffer.data

        sanitized_data = {}
        
        def _recursive_sanitize(item: Any) -> Any:
            """Recursively traverses and sanitizes data."""
            if isinstance(item, str):
                return self.sanitize_text(item)
            elif isinstance(item, dict):
                return {k: _recursive_sanitize(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [_recursive_sanitize(v) for v in item]
            else:
                return item # Not a sanitizable type (int, bool, etc.)

        sanitized_data = _recursive_sanitize(buffer.data)
        
        v_results = []
        total_fixes = sum(self.sanitization_counts.values())
        
        if total_fixes > 0:
            v_results.append(ValidationResult(
                rule_id="SANITIZATION_FIXES_APPLIED",
                passed=True, # This is a "fix", not a "failure"
                severity=ValidationSeverity.INFO,
                message=f"Applied {total_fixes} sanitization fixes.",
                details=dict(self.sanitization_counts)
            ))
        else:
            v_results.append(ValidationResult(
                rule_id="SANITIZATION_PASSED",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="No sanitization artifacts found."
            ))
            
        return v_results, sanitized_data

# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

class DuplicateDetector:
    """Detects duplicate or near-duplicate content."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold: Threshold above which content is considered duplicate
        """
        self.similarity_threshold = similarity_threshold
    
    def is_duplicate(self, text1: str, text2: str) -> bool:
        """
        Checks if two texts are duplicates based on similarity threshold.
        """
        similarity = text_utils.calculate_similarity(text1, text2)
        return similarity >= self.similarity_threshold
    
    def find_duplicates_in_list(self, texts: List[str]) -> List[Tuple[int, int]]:
        """
        Finds all duplicate pairs in a list of texts.
        
        Returns:
            List of tuples (index1, index2) indicating duplicate pairs
        """
        duplicates = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                if self.is_duplicate(texts[i], texts[j]):
                    duplicates.append((i, j))
        return duplicates


# ============================================================================
# HASH UTILITIES
# ============================================================================

def compute_content_hash(content: str) -> str:
    """
    Computes SHA-256 hash of content for integrity checking.
    
    Args:
        content: String content to hash
        
    Returns:
        Hex string of SHA-256 hash
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def compute_dict_hash(data: Dict) -> str:
    """
    Computes SHA-256 hash of a dictionary for integrity checking.
    Dictionary is converted to JSON (with sorted keys) before hashing.
    
    Args:
        data: Dictionary to hash
        
    Returns:
        Hex string of SHA-256 hash
    """
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


# ============================================================================
# REASONING CONFIG UTILITIES
# ============================================================================

def build_reasoning_prompt_addendum(config: ReasoningConfig) -> str:
    """
    Builds a prompt addendum string based on reasoning configuration.
    This addendum is appended to the base prompt to enforce reasoning parameters.
    
    Args:
        config: ReasoningConfig object with reasoning parameters
        
    Returns:
        String containing the reasoning directives
    """
    addendum_parts = [PROMPT_ADDENDUM_CONFIG.HEADER]
    
    # Chain-of-Thought directives
    if config.cot_min_paths > 0:
        for threshold, directive_template in PROMPT_ADDENDUM_CONFIG.COT_DIRECTIVES:
            if config.cot_min_paths >= threshold:
                addendum_parts.append(directive_template.format(cot=config.cot_min_paths))
                break
    
    # Tree-of-Thought Breadth directives
    if config.tot_branches > 1:
        for threshold, directive_template in PROMPT_ADDENDUM_CONFIG.TOT_B_DIRECTIVES:
            if config.tot_branches >= threshold:
                addendum_parts.append(directive_template.format(tot_b=config.tot_branches))
                break
    
    # Tree-of-Thought Depth directives
    if config.min_tot_depth > 1:
        for threshold, directive_template in PROMPT_ADDENDUM_CONFIG.TOT_D_DIRECTIVES:
            if config.min_tot_depth >= threshold:
                addendum_parts.append(directive_template.format(tot_d=config.min_tot_depth))
                break
    
    # Reflexion directives
    if config.reflexion and config.max_reflexion_loops > 0:
        for threshold, directive_template in PROMPT_ADDENDUM_CONFIG.REFLEXION_DIRECTIVES:
            if config.max_reflexion_loops >= threshold:
                addendum_parts.append(directive_template.format(max_loops=config.max_reflexion_loops))
                break
    
    addendum_parts.append(PROMPT_ADDENDUM_CONFIG.FOOTER)
    
    return ''.join(addendum_parts)

# --- START: ADDED MISSING FUNCTIONS ---

def reasoning_config_to_api_params(config: ReasoningConfig) -> Dict[str, Any]:
    """
    Converts a ReasoningConfig object into a dictionary for the Gemini API.
    
    Args:
        config: The ReasoningConfig object.
        
    Returns:
        A dictionary with "generation_config" (a GenerationConfig object)
        and "sc" (self-consistency candidate count).
    """
    if not GEMINI_AVAILABLE:
        # Return a non-functional default if API is not loaded
        return {"generation_config": {}, "sc": 1}
        
    gen_config = genai.GenerationConfig()
    sc_count = 1
    
    if config.self_consistency > 1:
        sc_count = config.self_consistency
        gen_config.candidate_count = sc_count
        # Use a high temperature to get diverse responses for self-consistency
        gen_config.temperature = 1.0 
    else:
        # Use the default temperature when not doing self-consistency
        gen_config.temperature = DEFAULT_GENERATION_TEMPERATURE

    # Note: top_k and top_p are not currently defined in ReasoningConfig
    # gen_config.top_k = config.top_k
    # gen_config.top_p = config.top_p
    
    return {
        "generation_config": gen_config,
        "sc": sc_count  # Pass the self-consistency count
    }


def enhance_system_prompt_with_reasoning(
    system_prompt: str,
    config: ReasoningConfig,
    section_id: str
) -> str:
    """
    Enhances a system prompt with reasoning directives, avoiding duplication.
    
    Args:
        system_prompt: The base system prompt.
        config: The ReasoningConfig object.
        section_id: The ID of the section (for logging).
        
    Returns:
        The enhanced system prompt.
    """
    reasoning_addendum = build_reasoning_prompt_addendum(config)
    
    # Check if the prompt *already* has directives (e.g., from a retry)
    if PROMPT_ADDENDUM_CONFIG.HEADER in system_prompt:
        logging.debug(f"System prompt for {section_id} already contains directives. Skipping addendum.")
        return system_prompt
        
    return f"{system_prompt}\n{reasoning_addendum}"

# --- END: ADDED MISSING FUNCTIONS ---

# ============================================================================
# LLM GENERATION UTILITIES
# ============================================================================

def generate_with_reasoning(
    prompt: str,
    config: ReasoningConfig,
    model: str = "gemini-2.5-pro",
    temperature: float = None,
    max_tokens: int = 8192
) -> str:
    """
    Generates LLM response with reasoning configuration applied.
    
    Args:
        prompt: Base prompt
        config: ReasoningConfig with reasoning parameters
        model: Model name to use
        temperature: Temperature override (uses DEFAULT_GENERATION_TEMPERATURE if None)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text
        
    Raises:
        RuntimeError: If Gemini API is not available
    """
    if not GEMINI_AVAILABLE:
        raise RuntimeError("Gemini API not available. Cannot generate content.")
    
    # Build full prompt with reasoning addendum
    reasoning_addendum = build_reasoning_prompt_addendum(config)
    full_prompt = prompt + reasoning_addendum
    
    # Use default temperature if not specified
    if temperature is None:
        temperature = DEFAULT_GENERATION_TEMPERATURE
    
    # Generate content
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        return response.text
    except Exception as e:
        logging.error(f"Error generating content with reasoning: {e}")
        raise


def generate_with_self_consistency(
    prompt: str,
    config: ReasoningConfig,
    model: str = "gemini-2.5-pro",
    temperature: float = None,
    max_tokens: int = 8192,
    synthesis_prompt_builder: Optional[callable] = None
) -> str:
    """
    Generates content using self-consistency: multiple samples + synthesis.
    
    Args:
        prompt: Base prompt
        config: ReasoningConfig (uses self_consistency parameter)
        model: Model name
        temperature: Temperature override
        max_tokens: Max tokens per generation
        synthesis_prompt_builder: Optional function to build synthesis prompt
        
    Returns:
        Synthesized final response
    """
    if config.self_consistency <= 1:
        # No self-consistency, just generate once
        return generate_with_reasoning(prompt, config, model, temperature, max_tokens)
    
    # Generate multiple candidate responses
    candidates = []
    for i in range(config.self_consistency):
        try:
            response = generate_with_reasoning(prompt, config, model, temperature, max_tokens)
            candidates.append(response)
        except Exception as e:
            logging.warning(f"Failed to generate candidate {i+1}/{config.self_consistency}: {e}")
    
    if not candidates:
        raise RuntimeError("All self-consistency generation attempts failed")
    
    if len(candidates) == 1:
        return candidates[0]
    
    # Synthesize candidates
    if synthesis_prompt_builder:
        synthesis_prompt = synthesis_prompt_builder(prompt, candidates)
    else:
        # Default synthesis prompt
        synthesis_prompt = f"""Given the following candidate responses to the prompt, synthesize the best final answer:

ORIGINAL PROMPT:
{prompt}

CANDIDATE RESPONSES:
"""
        for i, candidate in enumerate(candidates):
            synthesis_prompt += f"\n\n--- Candidate {i+1} ---\n{candidate}"
        
        synthesis_prompt += "\n\nProvide the synthesized final answer:"
    
    # Generate synthesis (without self-consistency to avoid recursion)
    synthesis_config = ReasoningConfig(
        cot_min_paths=config.cot_min_paths,
        tot_branches=config.tot_branches,
        min_tot_depth=config.min_tot_depth,
        self_consistency=1,  # No nested self-consistency
        reflexion=False
    )
    
    return generate_with_reasoning(synthesis_prompt, synthesis_config, model, temperature, max_tokens)


# ============================================================================
# CODE INTERPRETER TOOL (NEW - Phase 3)
# ============================================================================

class CodeInterpreterTool:
    """
    Code Interpreter for deterministic operations on LLM outputs.
    Provides Python execution environment for validation and transformation tasks.
    """
    
    def __init__(self):
        """Initialize Code Interpreter."""
        self.enabled = True
        self.sandbox_globals = {
            'json': json,
            're': re,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'sorted': sorted,
            'sum': sum,
            'max': max,
            'min': min,
        }
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute Python code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            context: Optional context dictionary to inject into execution environment
            
        Returns:
            Result of the execution
            
        Raises:
            Exception: If code execution fails
        """
        if not self.enabled:
            raise RuntimeError("Code Interpreter is disabled")
        
        # Merge context with sandbox globals
        exec_globals = self.sandbox_globals.copy()
        if context:
            exec_globals.update(context)
        
        # Execute code and capture result
        exec_locals = {}
        try:
            exec(code, exec_globals, exec_locals)
        except Exception as e:
            logging.error(f"CodeInterpreter execution failed: {e}\nCode:\n{code}")
            raise
        
        # Return 'result' variable if it exists
        return exec_locals.get('result', None)

    def run(self, script: str) -> Tuple[bool, str]:
        """
        Runs a Python script in a sandboxed environment and captures stdout.
        This is the preferred method for complex operations.

        Args:
            script: The Python script to execute.

        Returns:
            Tuple[bool, str]: (success, output)
                             If success is True, output is the stdout.
                             If success is False, output is the stderr.
        """
        if not self.enabled:
            return False, "Code Interpreter is disabled"

        # Create a temporary file to hold the script
        try:
            with open("temp_code_interpreter_script.py", "w", encoding="utf-8") as f:
                f.write(script)

            # Execute the script using a subprocess with a timeout
            # This is safer as it isolates the execution completely
            result = subprocess.run(
                [sys.executable, "temp_code_interpreter_script.py"],
                capture_output=True,
                text=True,
                timeout=10,  # 10-second timeout
                encoding="utf-8"
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, "Code execution timed out (10 seconds)"
        except Exception as e:
            return False, f"Code execution failed: {e}"
        finally:
            # Clean up the temporary file
            if os.path.exists("temp_code_interpreter_script.py"):
                os.remove("temp_code_interpreter_script.py")

    
    def validate_word_count(self, text: str, min_words: int, max_words: int) -> Tuple[bool, int]:
        """
        Validates word count deterministically.
        
        Args:
            text: Text to validate
            min_words: Minimum word count
            max_words: Maximum word count
            
        Returns:
            Tuple of (is_valid, actual_count)
        """
        code = f"""
text = {json.dumps(text)}
word_count = len(text.split())
is_valid = {min_words} <= word_count <= {max_words}
print(json.dumps({{"is_valid": is_valid, "word_count": word_count}}))
"""
        success, output = self.run(code)
        if success:
            try:
                res = json.loads(output)
                return res["is_valid"], res["word_count"]
            except (json.JSONDecodeError, KeyError):
                return False, -1
        return False, -1
    
    def reorder_bullets_by_score(self, bullets: List[str], scores: List[float]) -> List[str]:
        """
        Reorders bullets by score deterministically.
        
        Args:
            bullets: List of bullet strings
            scores: List of relevance scores (same length as bullets)
            
        Returns:
            Reordered list of bullets
        """
        code = f"""
bullets = {json.dumps(bullets)}
scores = {json.dumps(scores)}
paired = list(zip(bullets, scores))
sorted_pairs = sorted(paired, key=lambda x: x[1], reverse=True)
result = [bullet for bullet, score in sorted_pairs]
print(json.dumps(result))
"""
        success, output = self.run(code)
        if success:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return bullets # Return original on failure
        return bullets # Return original on failure


# ============================================================================
# SIGNAL SCORING
# ============================================================================

def calculate_signal_score(text: str, thematic_analysis: ThematicAnalysis) -> float:
    """
    Calculates a signal quality score for text based on thematic analysis keywords.
    
    Args:
        text: Text to score
        thematic_analysis: ThematicAnalysis object with keywords
        
    Returns:
        Float score between 0.0 and 1.0
    """
    try:
        comp_intel = getattr(thematic_analysis, 'competitive_intelligence', None)
        differentiators = set()
        if comp_intel:
            diff_kw = getattr(comp_intel, 'differentiator_keywords', [])
            if isinstance(diff_kw, list):
                differentiators = set(kw.lower() for kw in diff_kw if kw)

        primary_theme_data = thematic_analysis.primary_theme or {}
        primary_words = set(kw.lower() for kw in primary_theme_data.get('keywords', []) if kw)

        all_jd_words = differentiators.union(primary_words)

    except (AttributeError, KeyError, TypeError) as e:
        logging.warning(f"Error accessing keywords in thematic_analysis for signal score calculation: {e}")
        return 0.0

    if not all_jd_words:
        return 0.0
    
    text_lower = text.lower()
    words_in_text = set(re.findall(r'\b\w+\b', text_lower))
    matches = words_in_text.intersection(all_jd_words)
    score = len(matches) / 10.0 # Base score

    primary_matches = words_in_text.intersection(primary_words)
    score += len(primary_matches) * 0.1 # Bonus for primary theme

    return min(1.0, score)


# ============================================================================
# TELEMETRY
# ============================================================================

class TelemetryLogger:
    """Logger for RAG telemetry data."""
    
    def __init__(self, log_dir: str = str(CACHE_DIR / "rag_telemetry")):
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

# --- ADDED: sys import for CodeInterpreterTool ---
import sys