# Healer Retry Hardening Specification

## SCOPE
Governs: **L2 Execution Layer** (Healer Retry Logic, Semantic Diff Scoring, Scope Lock)

Defines healer retry hardening with strictness escalation and scope enforcement.

---

Retry strictness escalation, semantic diff distance scoring, and scope lock enforcement.

---

## Retry Strictness Escalation

```python
@dataclass
class RetryConfig:
    max_attempts: int = 3
    strictness_escalation: List[float] = field(default_factory=lambda: [0.7, 0.85, 0.95])
    timeout_escalation: List[int] = field(default_factory=lambda: [30, 20, 10])
    scope_lock: bool = True

class HealerRetryManager:
    """Manage healer retries with strictness escalation"""

    def __init__(self, config: RetryConfig):
        self.config = config
        self.attempt_history = []

    def execute_with_retry(self, violation: Dict[str, Any],
                          healer_func: Callable) -> HealingResult:
        """
        Execute healing with retry escalation.

        REQUIREMENTS:
        - Strictness increases with each retry
        - Timeout decreases with each retry
        - Scope cannot widen across retries
        - Abort if plan divergence increases
        """

        for attempt in range(self.config.max_attempts):
            # Get strictness for this attempt
            strictness = self.config.strictness_escalation[attempt]
            timeout = self.config.timeout_escalation[attempt]

            # Execute healing attempt
            result = self._execute_attempt(
                violation,
                healer_func,
                attempt,
                strictness,
                timeout
            )

            # Record attempt
            self.attempt_history.append({
                'attempt': attempt,
                'strictness': strictness,
                'timeout': timeout,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })

            # Check if successful
            if result.success:
                return result

            # Check if should retry
            if not self._should_retry(attempt, result):
                break

        # All retries exhausted
        return HealingResult(
            success=False,
            error="Max retries exhausted",
            attempts=self.attempt_history
        )

    def _execute_attempt(self, violation: Dict[str, Any],
                        healer_func: Callable,
                        attempt: int, strictness: float,
                        timeout: int) -> HealingResult:
        """Execute single healing attempt with strictness"""

        import signal

        # Set timeout
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Healing attempt {attempt} timed out after {timeout}s")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        try:
            # Execute healing with strictness
            result = healer_func(violation, strictness=strictness)

            # Validate result
            if not self._validate_result(result, attempt):
                result.success = False
                result.error = "Result validation failed"

            return result

        except TimeoutError as e:
            return HealingResult(
                success=False,
                error=str(e),
                timeout=True
            )
        except Exception as e:
            return HealingResult(
                success=False,
                error=str(e),
                exception=True
            )
        finally:
            signal.alarm(0)  # Cancel timeout

    def _should_retry(self, attempt: int, result: HealingResult) -> bool:
        """Determine if should retry based on result"""

        # Don't retry if max attempts reached
        if attempt >= self.config.max_attempts - 1:
            return False

        # Don't retry if timeout (likely systemic issue)
        if result.timeout:
            return False

        # Don't retry if exception (likely code bug)
        if result.exception:
            return False

        # Retry if healing failed but recoverable
        return True

    def _validate_result(self, result: HealingResult, attempt: int) -> bool:
        """Validate healing result"""

        # Check scope lock
        if self.config.scope_lock and attempt > 0:
            if not self._validate_scope_lock(result):
                return False

        # Check plan divergence
        if attempt > 0:
            if not self._validate_plan_convergence(result):
                return False

        return True

    def _validate_scope_lock(self, result: HealingResult) -> bool:
        """Validate scope has not widened"""

        if not self.attempt_history:
            return True

        previous_result = self.attempt_history[-1]['result']

        # Compare file counts
        previous_files = set(previous_result.files_modified)
        current_files = set(result.files_modified)

        # Scope must not widen
        if len(current_files) > len(previous_files):
            return False

        # Current files must be subset of previous
        if not current_files.issubset(previous_files):
            return False

        return True

    def _validate_plan_convergence(self, result: HealingResult) -> bool:
        """Validate plan is converging, not diverging"""

        if len(self.attempt_history) < 2:
            return True

        # Get last two attempts
        prev_result = self.attempt_history[-1]['result']
        prev_prev_result = self.attempt_history[-2]['result']

        # Calculate semantic distances
        prev_distance = self._calculate_semantic_distance(
            prev_prev_result.plan,
            prev_result.plan
        )

        current_distance = self._calculate_semantic_distance(
            prev_result.plan,
            result.plan
        )

        # Plan must be converging (distance decreasing)
        if current_distance > prev_distance:
            return False

        return True

    def _calculate_semantic_distance(self, plan_a: str, plan_b: str) -> float:
        """Calculate semantic distance between two plans"""

        # Tokenize plans
        tokens_a = set(plan_a.lower().split())
        tokens_b = set(plan_b.lower().split())

        # Jaccard distance
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b

        if not union:
            return 1.0

        jaccard_similarity = len(intersection) / len(union)
        jaccard_distance = 1.0 - jaccard_similarity

        return jaccard_distance
```

---

## Semantic Diff Distance Scoring

```python
class SemanticDiffScorer:
    """Score semantic distance between healing attempts"""

    def __init__(self):
        self.diff_history = []

    def score_diff(self, original: str, modified: str) -> float:
        """
        Score semantic distance between original and modified code.

        RETURNS:
        - 0.0 = identical
        - 1.0 = completely different
        """

        # Tokenize
        original_tokens = self._tokenize(original)
        modified_tokens = self._tokenize(modified)

        # Calculate token-level distance
        token_distance = self._token_distance(original_tokens, modified_tokens)

        # Calculate line-level distance
        line_distance = self._line_distance(original, modified)

        # Calculate AST-level distance (if valid Python)
        ast_distance = self._ast_distance(original, modified)

        # Weighted average
        if ast_distance is not None:
            return (token_distance * 0.3 + line_distance * 0.3 + ast_distance * 0.4)
        else:
            return (token_distance * 0.5 + line_distance * 0.5)

    def _tokenize(self, code: str) -> List[str]:
        """Tokenize code into semantic tokens"""
        import re

        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

        # Tokenize
        tokens = re.findall(r'\w+|[^\w\s]', code)

        return tokens

    def _token_distance(self, tokens_a: List[str], tokens_b: List[str]) -> float:
        """Calculate token-level Jaccard distance"""

        set_a = set(tokens_a)
        set_b = set(tokens_b)

        intersection = set_a & set_b
        union = set_a | set_b

        if not union:
            return 0.0

        jaccard_similarity = len(intersection) / len(union)
        return 1.0 - jaccard_similarity

    def _line_distance(self, code_a: str, code_b: str) -> float:
        """Calculate line-level Levenshtein distance"""

        lines_a = code_a.strip().split('\n')
        lines_b = code_b.strip().split('\n')

        # Levenshtein distance
        distance = self._levenshtein_distance(lines_a, lines_b)

        # Normalize by max length
        max_len = max(len(lines_a), len(lines_b))
        if max_len == 0:
            return 0.0

        return distance / max_len

    def _levenshtein_distance(self, seq_a: List[str], seq_b: List[str]) -> int:
        """Calculate Levenshtein distance between sequences"""

        m, n = len(seq_a), len(seq_b)

        # Create distance matrix
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Initialize
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # Fill matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq_a[i-1] == seq_b[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # deletion
                        dp[i][j-1],    # insertion
                        dp[i-1][j-1]   # substitution
                    )

        return dp[m][n]

    def _ast_distance(self, code_a: str, code_b: str) -> Optional[float]:
        """Calculate AST-level distance"""

        import ast

        try:
            tree_a = ast.parse(code_a)
            tree_b = ast.parse(code_b)
        except SyntaxError:
            return None

        # Extract AST node types
        nodes_a = [type(node).__name__ for node in ast.walk(tree_a)]
        nodes_b = [type(node).__name__ for node in ast.walk(tree_b)]

        # Jaccard distance on node types
        set_a = set(nodes_a)
        set_b = set(nodes_b)

        intersection = set_a & set_b
        union = set_a | set_b

        if not union:
            return 0.0

        jaccard_similarity = len(intersection) / len(union)
        return 1.0 - jaccard_similarity

    def track_convergence(self, attempt: int, diff_score: float):
        """Track diff convergence across retries"""

        self.diff_history.append({
            'attempt': attempt,
            'diff_score': diff_score,
            'timestamp': datetime.now().isoformat()
        })

    def is_converging(self) -> bool:
        """Check if diffs are converging"""

        if len(self.diff_history) < 2:
            return True

        # Check if scores are decreasing
        for i in range(1, len(self.diff_history)):
            if self.diff_history[i]['diff_score'] > self.diff_history[i-1]['diff_score']:
                return False

        return True
```

---

## Scope Lock Enforcement

```python
class ScopeLock:
    """Enforce scope lock across healing retries"""

    def __init__(self, initial_scope: Set[str]):
        """
        Initialize scope lock with initial file set.

        REQUIREMENTS:
        - Scope cannot widen across retries
        - New files cannot be added
        - Only subset of initial files allowed
        """
        self.initial_scope = initial_scope
        self.current_scope = initial_scope.copy()

    def validate_scope(self, proposed_scope: Set[str]) -> bool:
        """Validate proposed scope does not widen"""

        # Proposed scope must be subset of initial
        if not proposed_scope.issubset(self.initial_scope):
            return False

        # Proposed scope must not be larger than current
        if len(proposed_scope) > len(self.current_scope):
            return False

        return True

    def update_scope(self, new_scope: Set[str]):
        """Update current scope (must be narrower)"""

        if not self.validate_scope(new_scope):
            raise ValueError("Scope lock violation: cannot widen scope")

        self.current_scope = new_scope

    def get_allowed_files(self) -> Set[str]:
        """Get currently allowed files"""
        return self.current_scope.copy()

    def is_file_allowed(self, file_path: str) -> bool:
        """Check if file is within scope"""
        return file_path in self.current_scope

# Usage in healer
class HealerWithScopeLock:
    def __init__(self, violation: Dict[str, Any]):
        # Extract initial scope from violation
        initial_files = self._extract_affected_files(violation)
        self.scope_lock = ScopeLock(initial_files)

    def heal_with_retry(self, violation: Dict[str, Any]) -> HealingResult:
        """Heal with scope lock enforcement"""

        retry_manager = HealerRetryManager(RetryConfig(scope_lock=True))

        def healing_func(v, strictness):
            # Generate healing plan
            plan = self._generate_plan(v, strictness)

            # Extract files from plan
            proposed_files = self._extract_files_from_plan(plan)

            # Validate scope
            if not self.scope_lock.validate_scope(proposed_files):
                raise ValueError(
                    f"Scope lock violation: proposed files {proposed_files} "
                    f"exceed allowed scope {self.scope_lock.get_allowed_files()}"
                )

            # Execute plan
            result = self._execute_plan(plan)

            # Update scope on success
            if result.success:
                self.scope_lock.update_scope(proposed_files)

            return result

        return retry_manager.execute_with_retry(violation, healing_func)
```

---

## Root Cause Classification Persistence

```python
@dataclass
class RootCauseClassification:
    violation_type: str
    root_cause_category: str
    confidence: float
    evidence: List[str]
    timestamp: str

class RootCauseClassifier:
    """Classify and persist root causes across retries"""

    def __init__(self):
        self.classifications = []

    def classify_root_cause(self, violation: Dict[str, Any],
                           attempt: int) -> RootCauseClassification:
        """
        Classify root cause of violation.

        CATEGORIES:
        - IMPORT_CYCLE: Circular import dependency
        - TYPE_MISMATCH: Type annotation error
        - MISSING_DEPENDENCY: Missing import or module
        - SYNTAX_ERROR: Python syntax error
        - LOGIC_ERROR: Incorrect logic or algorithm
        - CONFIGURATION_ERROR: Configuration mismatch
        """

        # Analyze violation
        violation_type = violation['type']
        message = violation['message']

        # Pattern matching for root cause
        root_cause = self._match_root_cause_pattern(violation_type, message)

        # Calculate confidence
        confidence = self._calculate_classification_confidence(violation, root_cause)

        # Extract evidence
        evidence = self._extract_evidence(violation, root_cause)

        # Create classification
        classification = RootCauseClassification(
            violation_type=violation_type,
            root_cause_category=root_cause,
            confidence=confidence,
            evidence=evidence,
            timestamp=datetime.now().isoformat()
        )

        # Persist classification
        self.classifications.append(classification)

        return classification

    def _match_root_cause_pattern(self, violation_type: str,
                                  message: str) -> str:
        """Match violation to root cause category"""

        patterns = {
            'IMPORT_CYCLE': [
                r'circular import',
                r'import cycle',
                r'cyclic dependency'
            ],
            'TYPE_MISMATCH': [
                r'type.*mismatch',
                r'expected.*got',
                r'incompatible types'
            ],
            'MISSING_DEPENDENCY': [
                r'module.*not found',
                r'cannot import',
                r'no module named'
            ],
            'SYNTAX_ERROR': [
                r'syntax error',
                r'invalid syntax',
                r'unexpected.*token'
            ],
            'LOGIC_ERROR': [
                r'assertion.*failed',
                r'incorrect.*result',
                r'unexpected.*behavior'
            ],
            'CONFIGURATION_ERROR': [
                r'configuration.*error',
                r'setting.*invalid',
                r'config.*mismatch'
            ]
        }

        import re

        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message, re.IGNORECASE):
                    return category

        return 'UNKNOWN'

    def _calculate_classification_confidence(self, violation: Dict[str, Any],
                                            root_cause: str) -> float:
        """Calculate confidence in classification"""

        # Base confidence
        confidence = 0.5

        # Boost if violation type matches root cause
        if violation['type'] in root_cause:
            confidence += 0.3

        # Boost if file path provides context
        if 'file_path' in violation:
            confidence += 0.1

        # Boost if stack trace available
        if 'stack_trace' in violation:
            confidence += 0.1

        return min(1.0, confidence)

    def _extract_evidence(self, violation: Dict[str, Any],
                         root_cause: str) -> List[str]:
        """Extract evidence for classification"""

        evidence = []

        # Add violation message
        evidence.append(f"Message: {violation['message']}")

        # Add file path
        if 'file_path' in violation:
            evidence.append(f"File: {violation['file_path']}")

        # Add line number
        if 'line' in violation:
            evidence.append(f"Line: {violation['line']}")

        # Add stack trace
        if 'stack_trace' in violation:
            evidence.append(f"Stack: {violation['stack_trace'][:200]}")

        return evidence

    def get_persistent_classification(self, violation_type: str) -> Optional[RootCauseClassification]:
        """Get most recent classification for violation type"""

        for classification in reversed(self.classifications):
            if classification.violation_type == violation_type:
                return classification

        return None

    def is_classification_stable(self, violation_type: str) -> bool:
        """Check if classification is stable across retries"""

        # Get all classifications for this type
        type_classifications = [
            c for c in self.classifications
            if c.violation_type == violation_type
        ]

        if len(type_classifications) < 2:
            return True

        # Check if all have same root cause
        root_causes = set(c.root_cause_category for c in type_classifications)
        return len(root_causes) == 1
```

---

## Abort Conditions

```python
class RetryAbortConditions:
    """Conditions that trigger retry abort"""

    @staticmethod
    def should_abort(attempt_history: List[Dict],
                    current_result: HealingResult) -> Tuple[bool, str]:
        """
        Determine if should abort retries.

        ABORT CONDITIONS:
        1. Plan divergence increasing
        2. Scope widening detected
        3. Same error repeated 3 times
        4. Timeout on all attempts
        5. Root cause classification unstable
        """

        # Check plan divergence
        if RetryAbortConditions._is_plan_diverging(attempt_history):
            return True, "Plan divergence increasing across retries"

        # Check scope widening
        if RetryAbortConditions._is_scope_widening(attempt_history):
            return True, "Scope widening detected"

        # Check repeated errors
        if RetryAbortConditions._has_repeated_errors(attempt_history):
            return True, "Same error repeated 3 times"

        # Check timeouts
        if RetryAbortConditions._all_timeouts(attempt_history):
            return True, "All attempts timed out"

        # Check classification stability
        if RetryAbortConditions._is_classification_unstable(attempt_history):
            return True, "Root cause classification unstable"

        return False, ""

    @staticmethod
    def _is_plan_diverging(attempt_history: List[Dict]) -> bool:
        """Check if plan is diverging"""

        if len(attempt_history) < 3:
            return False

        # Get last 3 diff scores
        scores = [h['result'].diff_score for h in attempt_history[-3:]]

        # Check if increasing
        return scores[-1] > scores[-2] > scores[-3]

    @staticmethod
    def _is_scope_widening(attempt_history: List[Dict]) -> bool:
        """Check if scope is widening"""

        if len(attempt_history) < 2:
            return False

        # Get file counts
        counts = [len(h['result'].files_modified) for h in attempt_history]

        # Check if increasing
        return counts[-1] > counts[-2]

    @staticmethod
    def _has_repeated_errors(attempt_history: List[Dict]) -> bool:
        """Check if same error repeated"""

        if len(attempt_history) < 3:
            return False

        # Get last 3 errors
        errors = [h['result'].error for h in attempt_history[-3:]]

        # Check if all same
        return len(set(errors)) == 1

    @staticmethod
    def _all_timeouts(attempt_history: List[Dict]) -> bool:
        """Check if all attempts timed out"""

        if not attempt_history:
            return False

        return all(h['result'].timeout for h in attempt_history)

    @staticmethod
    def _is_classification_unstable(attempt_history: List[Dict]) -> bool:
        """Check if root cause classification is unstable"""

        if len(attempt_history) < 3:
            return False

        # Get last 3 classifications
        classifications = [
            h['result'].root_cause_classification
            for h in attempt_history[-3:]
        ]

        # Check if all different
        return len(set(classifications)) == 3
```

---

## Invariants

1. **Strictness increases with each retry**
2. **Timeout decreases with each retry**
3. **Scope cannot widen across retries**
4. **Plan must converge (distance decreasing)**
5. **Root cause classification must persist**
6. **Abort if divergence detected**

---

## Monitoring Requirements

All retry operations must emit:
- Attempt number
- Strictness level
- Timeout value
- Diff score
- Scope size
- Root cause classification
- Convergence status
- Abort reason (if aborted)

---

## Failure Modes

| Failure | Action | Recovery |
|---------|--------|----------|
| Plan diverging | Abort retries | Manual intervention |
| Scope widening | Abort retries | Reduce scope |
| Repeated errors | Abort retries | Fix underlying issue |
| All timeouts | Abort retries | Increase timeout |
| Classification unstable | Abort retries | Manual classification |
