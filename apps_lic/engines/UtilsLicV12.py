# File: utils_LIC.py
# Description: General-purpose utilities for the LIC workflow.

__version__ = "12.0"

import re
from datetime import datetime, timedelta


# ============================================================================
# NEW v11.6: CIRCUIT BREAKER (FEATURE 4.1)
# ============================================================================


class CircuitBreaker:
    """
    Circuit breaker for API calls - prevents cascade failures
    FEATURE 4.1 from SUPREME_SPELL

    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are blocked
    - HALF_OPEN: Testing if service has recovered

    After failure_threshold consecutive failures, the circuit opens.
    After timeout_seconds, it transitions to HALF_OPEN to test recovery.
    A successful request in HALF_OPEN closes the circuit.
    """

    def __init__(self, failure_threshold: int = 3, timeout_seconds: int = 60):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening
            timeout_seconds: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitBreakerOpenError: If circuit is OPEN
            Exception: Any exception raised by func
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.last_failure_time and datetime.now() - self.last_failure_time > timedelta(
                seconds=self.timeout_seconds
            ):
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
                print("[CircuitBreaker] Transitioning to HALF_OPEN for recovery test")
            else:
                raise CircuitBreakerOpenError(
                    f"API circuit breaker is OPEN - waiting for recovery "
                    f"(failed {self.failure_count} times, will retry after {self.timeout_seconds}s)"
                )

        try:
            result = func(*args, **kwargs)

            if self.state == CircuitState.HALF_OPEN:
                # Test request succeeded, close circuit
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print("[CircuitBreaker] Recovery successful, circuit CLOSED")

            return result

        except Exception:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"[CircuitBreaker] Circuit OPEN after {self.failure_count} failures")
            else:
                print(f"[CircuitBreaker] Failure {self.failure_count}/{self.failure_threshold}")

            raise


# ============================================================================
# NEW v11.6: CONTEXT MANAGER (GAP 7.1-7.3)
# ============================================================================


class ContextManager:
    """
    Intelligent context window management with priority-based truncation
    GAP 7.1, 7.2, 7.3 from v10.22

    Different sections of context have different priorities:
    - Job description: Highest priority, never truncate
    - Recipient profile: High priority
    - Company context: Medium-high priority
    - Sender profile: Medium priority
    - RAG results: Lower priority, truncate oldest first
    - Examples: Lowest priority, truncate first
    """

    SECTION_PRIORITIES = {
        "job_description": 100,  # Highest - never truncate
        "recipient_profile": 90,
        "company_context": 80,
        "sender_profile": 70,
        "rag_recent": 60,
        "rag_historical": 40,
        "examples": 30,  # Lowest - truncate first
    }

    MAX_CONTEXT_TOKENS = 180000  # Conservative estimate for Gemini 1.5 Pro
    CHARS_PER_TOKEN = 4  # Rough estimate

    @classmethod
    def truncate_intelligently(
        cls, context_sections: dict[str, str], max_tokens: int = MAX_CONTEXT_TOKENS
    ) -> dict[str, str]:
        """
        Truncate context sections by priority if exceeding token limit.

        Args:
            context_sections: Dictionary of section_name -> section_text
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated context_sections dictionary
        """
        # Rough estimate: 4 chars = 1 token
        total_chars = sum(len(text) for text in context_sections.values())
        estimated_tokens = total_chars // cls.CHARS_PER_TOKEN

        if estimated_tokens <= max_tokens:
            return context_sections

        print(
            f"[ContextManager] Context exceeds limit ({estimated_tokens} > {max_tokens} tokens), truncating..."
        )

        # Sort sections by priority (highest first)
        sorted_sections = sorted(
            context_sections.items(),
            key=lambda x: cls.SECTION_PRIORITIES.get(x[0], 50),
            reverse=True,
        )

        truncated = {}
        running_tokens = 0
        token_budget = max_tokens

        for section_name, section_text in sorted_sections:
            section_tokens = len(section_text) // cls.CHARS_PER_TOKEN

            if running_tokens + section_tokens <= token_budget:
                # Section fits completely
                truncated[section_name] = section_text
                running_tokens += section_tokens
            else:
                # Truncate this section to fit remaining budget
                remaining_tokens = token_budget - running_tokens
                remaining_chars = remaining_tokens * cls.CHARS_PER_TOKEN

                if remaining_chars > 100:  # Only include if meaningful
                    truncated[section_name] = section_text[:remaining_chars] + "... [truncated]"
                    running_tokens = token_budget
                    print(f"[ContextManager] Truncated '{section_name}' to fit budget")
                else:
                    print(f"[ContextManager] Dropped '{section_name}' - insufficient space")
                break

        print(f"[ContextManager] Truncation complete: {running_tokens}/{token_budget} tokens used")
        return truncated

    @classmethod
    def detect_overflow(cls, context_text: str) -> tuple[bool, int]:
        """
        Detect if context exceeds safe limits.

        Args:
            context_text: Full context string

        Returns:
            (is_overflow, estimated_tokens)
        """
        estimated_tokens = len(context_text) // cls.CHARS_PER_TOKEN
        is_overflow = estimated_tokens > cls.MAX_CONTEXT_TOKENS

        if is_overflow:
            print(
                f"[ContextManager] WARNING: Context overflow detected ({estimated_tokens} tokens)"
            )

        return is_overflow, estimated_tokens


# ============================================================================
# NEW v11.6: ADAPTIVE TEMPERATURE CONTROLLER (FEATURE 2.2)
# ============================================================================


class AdaptiveTemperatureController:
    """
    Progressive temperature escalation for retry attempts.
    FEATURE 2.2 from SUPREME_SPELL

    Each archetype has a base temperature. On retry attempts,
    temperature increases by ESCALATION_STEP to encourage more
    creative solutions, up to MAX_TEMPERATURE.

    Example:
    - Attempt 1: 0.45 (base for C_LEVEL)
    - Attempt 2: 0.60 (base + 0.15)
    - Attempt 3: 0.75 (base + 0.30)
    - Attempt 4+: 0.95 (capped at MAX)
    """

    BASE_TEMPERATURES = {
        Archetype.C_LEVEL: 0.45,
        Archetype.EXECUTIVE: 0.50,
        Archetype.SENIOR_TA: 0.55,
        Archetype.RECRUITER: 0.65,
    }
    ESCALATION_STEP = 0.15
    MAX_TEMPERATURE = 0.95

    def __init__(self):
        """Initialize temperature controller with history tracking"""
        self.attempt_history: dict[str, list[float]] = defaultdict(list)
        self.success_temperatures: dict[str, float] = {}

    def get_temperature(self, component: str, archetype: Archetype, attempt: int) -> float:
        """
        Get temperature for this generation attempt.

        Args:
            component: Component identifier (e.g., "body", "cta")
            archetype: Recipient archetype
            attempt: Attempt number (1-indexed)

        Returns:
            Temperature value for LLM generation
        """
        base_temp = self.BASE_TEMPERATURES[archetype]
        escalated_temp = min(self.MAX_TEMPERATURE, base_temp + (attempt - 1) * self.ESCALATION_STEP)

        # Track history
        key = f"{archetype.value}_{component}"
        self.attempt_history[key].append(escalated_temp)

        if attempt > 1:
            print(
                f"[TempController] Escalating temperature for {component}: {escalated_temp:.2f} (attempt {attempt})"
            )

        return escalated_temp

    def record_success(self, component: str, archetype: Archetype, temperature: float):
        """
        Record which temperature succeeded for learning.

        Args:
            component: Component identifier
            archetype: Recipient archetype
            temperature: Temperature that succeeded
        """
        key = f"{archetype.value}_{component}"
        self.success_temperatures[key] = temperature
        print(f"[TempController] Success recorded for {component} at temp {temperature:.2f}")

    def get_success_rate(self, component: str, archetype: Archetype) -> float | None:
        """
        Get average success temperature for component+archetype.

        Args:
            component: Component identifier
            archetype: Recipient archetype

        Returns:
            Average successful temperature, or None if no history
        """
        key = f"{archetype.value}_{component}"
        if key in self.success_temperatures:
            return self.success_temperatures[key]
        return None


# ============================================================================
# TEXT PROCESSING UTILITIES
# ============================================================================


class TextProcessor:
    """Utility functions for text processing and analysis"""

    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.

        Args:
            text: Input text

        Returns:
            Word count
        """
        return len(text.split())

    @staticmethod
    def count_chars(text: str) -> int:
        """
        Count characters in text.

        Args:
            text: Input text

        Returns:
            Character count
        """
        return len(text)

    @staticmethod
    def extract_sentences(text: str) -> list[str]:
        """
        Extract sentences from text.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting on period, exclamation, question mark
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def extract_metrics(text: str) -> list[str]:
        """
        Extract quantitative metrics from text.

        Args:
            text: Input text

        Returns:
            List of metrics (percentages, multipliers, large numbers)
        """
        metric_pattern = r"\b\d+%|\b\d+x\b|\b\d+\s*(million|billion|thousand|k)\b"
        return re.findall(metric_pattern, text, re.IGNORECASE)

    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """
        Remove extra whitespace from text.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        return text.strip()

    @staticmethod
    def truncate_text(text: str, max_chars: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum character length.

        Args:
            text: Input text
            max_chars: Maximum characters
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_chars:
            return text
        return text[: max_chars - len(suffix)] + suffix


# ============================================================================
# VALIDATION HELPERS
# ============================================================================


class ValidationHelper:
    """Helper functions for validation logic"""

    @staticmethod
    def check_word_count_range(text: str, min_words: int, max_words: int) -> tuple[bool, str]:
        """
        Check if text is within word count range.

        Args:
            text: Input text
            min_words: Minimum word count
            max_words: Maximum word count

        Returns:
            (is_valid, message)
        """
        word_count = len(text.split())

        if word_count < min_words:
            return False, f"Word count {word_count} below minimum {min_words}"
        elif word_count > max_words:
            return False, f"Word count {word_count} exceeds maximum {max_words}"

        return True, f"Word count {word_count} within range [{min_words}, {max_words}]"

    @staticmethod
    def check_char_limit(text: str, max_chars: int) -> tuple[bool, str]:
        """
        Check if text exceeds character limit.

        Args:
            text: Input text
            max_chars: Maximum characters

        Returns:
            (is_valid, message)
        """
        char_count = len(text)

        if char_count > max_chars:
            return False, f"Character count {char_count} exceeds limit {max_chars}"

        return True, f"Character count {char_count} within limit {max_chars}"

    @staticmethod
    def find_placeholders(text: str) -> list[str]:
        """
        Find placeholder patterns in text.

        Args:
            text: Input text

        Returns:
            List of placeholder patterns found
        """
        patterns = [
            r"\[.*?\]",  # [PLACEHOLDER]
            r"\{.*?\}",  # {PLACEHOLDER}
            r"<.*?>",  # <PLACEHOLDER>
            r"\bPLACEHOLDER\b",
            r"\bTODO\b",
            r"\bXXX\b",
            r"\bFIXME\b",
        ]

        found = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)

        return found

    @staticmethod
    def calculate_checksum(text: str) -> str:
        """
        Calculate simple checksum for text.

        Args:
            text: Input text

        Returns:
            Hexadecimal checksum string
        """
        import hashlib

        return hashlib.md5(text.encode()).hexdigest()[:16]


# ============================================================================
# TIMING UTILITIES
# ============================================================================


class Timer:
    """Simple timer for measuring execution time"""

    def __init__(self):
        """Initialize timer"""
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None

    def start(self):
        """Start timer"""
        self.start_time = datetime.now()

    def stop(self) -> float:
        """
        Stop timer and return elapsed seconds.

        Returns:
            Elapsed time in seconds
        """
        self.end_time = datetime.now()
        if self.start_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    def elapsed(self) -> float:
        """
        Get elapsed time without stopping timer.

        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()
