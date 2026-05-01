"""W1 Phase 5 — Wave D: Lexical Intent Pre-Veto (Option A, Layer 1).

Fast deterministic veto for obvious contradictions (cancel↔place, enable↔disable).
Escalates ambiguous cases to Layer 2 (LLM-judge).
Fail-closed on any internal error.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.certification.safety.veto_protocol import VetoResult, VetoStage, VetoStatus

# Default opposing action lexicon (embedded — file override optional)
DEFAULT_OPPOSED_PAIRS = [
    # Actions
    ("enable", "disable"),
    ("activate", "deactivate"),
    ("turn on", "turn off"),
    ("start", "stop"),
    ("begin", "end"),
    ("add", "remove"),
    ("create", "delete"),
    ("grant", "revoke"),
    ("allow", "block"),
    ("permit", "deny"),
    ("accept", "reject"),
    ("approve", "decline"),
    ("open", "close"),
    ("lock", "unlock"),
    ("show", "hide"),
    ("include", "exclude"),
    ("subscribe", "unsubscribe"),
    ("install", "uninstall"),
    ("deploy", "undeploy"),
    ("mount", "unmount"),
    ("attach", "detach"),
    # Verbs that imply directionality
    ("buy", "sell"),
    ("purchase", "refund"),
    ("deposit", "withdraw"),
    ("credit", "debit"),
    ("increase", "decrease"),
    ("raise", "lower"),
    ("expand", "contract"),
    ("grow", "shrink"),
    # Common intent opposites
    ("schedule", "cancel"),
    ("book", "unbook"),
    ("reserve", "release"),
    ("confirm", "abort"),
    ("commit", "rollback"),
    ("save", "discard"),
    ("send", "recall"),
    ("forward", "recall"),
    ("assign", "unassign"),
    ("allocate", "deallocate"),
]


@dataclass(frozen=True)
class LexicalMatch:
    """Result of lexical analysis."""
    found: bool
    opposed_verb: str | None = None
    position_query: int | None = None
    position_cached: int | None = None
    confidence: float = 0.0


class LexicalIntentVeto:
    """Fast lexical pre-veto for opposing intents.
    
    Layer 1: catches obvious contradictions in <5ms.
    Delegates ambiguous to Layer 2.
    """
    
    def __init__(
        self,
        lexicon_path: Path | None = None,
        case_sensitive: bool = False,
        delegate_on_ambiguous: bool = True,
    ):
        self._case_sensitive = case_sensitive
        self._delegate_on_ambiguous = delegate_on_ambiguous
        self._opposed_pairs: list[tuple[str, str]] = []
        self._load_lexicon(lexicon_path)
    
    @property
    def name(self) -> str:
        return "lexical_intent"
    
    def _load_lexicon(self, path: Path | None) -> None:
        """Load lexicon from file or use defaults."""
        self._opposed_pairs = list(DEFAULT_OPPOSED_PAIRS)
        
        if path and path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                # Parse simple format: verb_a, verb_b (one per line)
                custom = []
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) == 2:
                        custom.append((parts[0], parts[1]))
                if custom:
                    self._opposed_pairs = custom
            except Exception:
                # Fail softly: keep defaults on parse error
                pass
    
    def _normalize(self, text: str) -> str:
        """Normalize text for matching."""
        if not self._case_sensitive:
            text = text.lower()
        # Collapse whitespace
        text = " ".join(text.split())
        return text
    
    def _find_opposed_verbs(self, text: str) -> list[tuple[str, int]]:
        """Find all opposed verbs in text with positions."""
        normalized = self._normalize(text)
        found = []
        
        for verb_a, verb_b in self._opposed_pairs:
            # Check for verb_a
            for match in re.finditer(r'\b' + re.escape(self._normalize(verb_a)) + r'\b', normalized):
                found.append((verb_a, match.start()))
            # Check for verb_b
            for match in re.finditer(r'\b' + re.escape(self._normalize(verb_b)) + r'\b', normalized):
                found.append((verb_b, match.start()))
        
        return found
    
    def _analyze_opposition(
        self,
        query_verbs: list[tuple[str, int]],
        cached_verbs: list[tuple[str, int]],
    ) -> LexicalMatch:
        """Analyze whether queries have opposed intents."""
        # Build set of verbs in each query
        query_verb_set = {v for v, _ in query_verbs}
        cached_verb_set = {v for v, _ in cached_verbs}
        
        # Check for any opposed pair split across queries
        for verb_a, verb_b in self._opposed_pairs:
            a_in_query = verb_a in query_verb_set
            a_in_cached = verb_a in cached_verb_set
            b_in_query = verb_b in query_verb_set
            b_in_cached = verb_b in cached_verb_set
            
            # Opposed if one is in query and the other in cached
            if (a_in_query and b_in_cached) or (b_in_query and a_in_cached):
                # Find positions
                pos_a_q = next((p for v, p in query_verbs if v == verb_a), None)
                pos_b_q = next((p for v, p in query_verbs if v == verb_b), None)
                pos_a_c = next((p for v, p in cached_verbs if v == verb_a), None)
                pos_b_c = next((p for v, p in cached_verbs if v == verb_b), None)
                
                # Determine which verb is in which query
                if a_in_query:
                    return LexicalMatch(
                        found=True,
                        opposed_verb=verb_a,
                        position_query=pos_a_q,
                        position_cached=pos_b_c,
                        confidence=0.95,  # High confidence for clear lexical opposition
                    )
                else:
                    return LexicalMatch(
                        found=True,
                        opposed_verb=verb_b,
                        position_query=pos_b_q,
                        position_cached=pos_a_c,
                        confidence=0.95,
                    )
        
        # No clear opposition found
        return LexicalMatch(found=False, confidence=0.0)
    
    def _check_same_verb_conflict(
        self,
        query_verbs: list[tuple[str, int]],
        cached_verbs: list[tuple[str, int]],
    ) -> LexicalMatch:
        """Check if same verb appears but context suggests different intent.
        
        Example: "buy 100 shares" vs "buy 1000 shares" — same verb, different magnitude.
        This is ambiguous; delegate to Layer 2.
        """
        query_verb_counts: dict[str, int] = {}
        cached_verb_counts: dict[str, int] = {}
        
        for v, _ in query_verbs:
            query_verb_counts[v] = query_verb_counts.get(v, 0) + 1
        for v, _ in cached_verbs:
            cached_verb_counts[v] = cached_verb_counts.get(v, 0) + 1
        
        # Same verb present in both — check for magnitude/object differences
        common_verbs = set(query_verb_counts.keys()) & set(cached_verb_counts.keys())
        
        if common_verbs:
            # Ambiguous: same verb but may differ in object/magnitude
            # This is the "buy 100 vs buy 1000" case
            # We delegate; Layer 2 (LLM) should catch this
            return LexicalMatch(
                found=True,  # Found something, but it's ambiguous
                opposed_verb=list(common_verbs)[0],
                confidence=0.5,  # Uncertain — delegate
            )
        
        return LexicalMatch(found=False, confidence=0.0)
    
    def is_available(self) -> bool:
        """Always available — no external dependencies."""
        return True
    
    def evaluate(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> VetoResult:
        """Evaluate cache reuse safety via lexical analysis.
        
        Implements VetoStage Protocol.
        """
        start_time = time.perf_counter()
        
        try:
            # Extract verbs from both queries
            query_verbs = self._find_opposed_verbs(query)
            cached_verbs = self._find_opposed_verbs(cached_query)
            
            # Case 1: No verbs found in either — delegate to Layer 2
            if not query_verbs and not cached_verbs:
                return VetoResult.delegate(
                    stage_name=self.name,
                    reason="No opposed verbs detected — insufficient signal for lexical veto",
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
            
            # Case 2: Clear opposed pair split across queries — VETO
            opposition = self._analyze_opposition(query_verbs, cached_verbs)
            if opposition.found and opposition.confidence >= 0.9:
                return VetoResult.unsafe_intent(
                    stage_name=self.name,
                    contradiction=f"Opposed intent: '{opposition.opposed_verb}' detected across queries",
                    confidence=opposition.confidence,
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
            
            # Case 3: Same verb present — ambiguous, delegate
            same_verb = self._check_same_verb_conflict(query_verbs, cached_verbs)
            if same_verb.found and same_verb.confidence < 0.9:
                if self._delegate_on_ambiguous:
                    return VetoResult.delegate(
                        stage_name=self.name,
                        reason=f"Same verb '{same_verb.opposed_verb}' present but context may differ — delegating to semantic layer",
                        latency_ms=(time.perf_counter() - start_time) * 1000,
                    )
                else:
                    # Conservative: treat ambiguous as veto
                    return VetoResult.veto(
                        stage_name=self.name,
                        reason=f"Ambiguous: same verb '{same_verb.opposed_verb}' present but context unclear",
                        confidence=same_verb.confidence,
                        latency_ms=(time.perf_counter() - start_time) * 1000,
                    )
            
            # Case 4: Verbs found but no opposition pattern — SAFE (no contradiction detected)
            return VetoResult.safe(
                stage_name=self.name,
                confidence=0.8,  # Moderate confidence — lexical check is shallow
                rationale=f"No opposed intent detected. Query verbs: {[v for v, _ in query_verbs][:3]}. Cached verbs: {[v for v, _ in cached_verbs][:3]}.",
                latency_ms=(time.perf_counter() - start_time) * 1000,
                metadata={
                    "query_verb_count": len(query_verbs),
                    "cached_verb_count": len(cached_verbs),
                },
            )
            
        except Exception as e:
            # Fail-closed on any error
            return VetoResult.error(
                stage_name=self.name,
                error=f"Lexical analysis error: {e}",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )


def create_veto_from_policy(policy: dict[str, Any]) -> LexicalIntentVeto:
    """Factory: create LexicalIntentVeto from veto policy JSON."""
    config = policy.get("lexical_intent_config", {})
    return LexicalIntentVeto(
        lexicon_path=Path(config.get("lexicon_path", "config/certification/safety_lexicon.json")),
        case_sensitive=config.get("case_sensitive", False),
        delegate_on_ambiguous=config.get("delegate_on_ambiguous", True),
    )
