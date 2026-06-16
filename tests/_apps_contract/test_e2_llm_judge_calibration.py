"""E2.4 — Two-tier Spearman-rank calibration for apps_qna RAG judges.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-deferred-e5-f7a2b1.md E2.4

Two-tier calibration design
===========================

Tier 1 — Heuristic Sanity Baseline (``rag_judge_holdout.yaml``)
    Proves the deterministic heuristic fallback is stable and monotonic
    against examples designed for surface-level behaviour (overlap ratios,
    length, vocabulary diversity).  Passing this tier does NOT prove
    semantic quality alignment with human judgment.

Tier 2 — Human Semantic Alignment (``rag_judge_holdout_semantic.yaml``)
    Proves whether the judge tracks genuine human semantic quality.
    Labels represent whether the answer is responsive, complete, specific,
    and grounded.  This is the promotion-quality metric.

Calibration notes
-----------------
* Spearman compares **rank ordering**, not exact scores.
* Human semantic labels must NOT be modified to make a weak judge pass.
* A heuristic that cannot detect semantic relevance should not be promoted
  as a semantic judge.
* Passing heuristic sanity ≠ passing human-aligned semantic calibration.
* The ``answer_relevancy`` deterministic heuristic is expected to fail
  Tier 2 because it scores surface signals (word overlap, answer length,
  vocabulary uniqueness) rather than semantic relevance.  That failure is
  correct and informative — it classifies the heuristic as **fallback-only**.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from agentic_core.L0_routing.config.model_catalog import OPENAI_DEFAULT_MODEL_ID

from scipy.stats import spearmanr

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HOLDOUT_DIR = Path(__file__).resolve().parents[2] / "apps_qna" / "holdout"

HEURISTIC_SANITY_PATH = _HOLDOUT_DIR / "rag_judge_holdout.yaml"
SEMANTIC_ALIGNMENT_PATH = _HOLDOUT_DIR / "rag_judge_holdout_semantic.yaml"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"example_id", "judge_id", "query", "retrieved_context", "human_score", "labeler_id"}
VALID_JUDGE_IDS = {"context_recall", "context_precision", "answer_relevancy"}

# Tier 1 thresholds — heuristic sanity (all judges must pass)
TIER1_MIN_TOTAL = 90
TIER1_MIN_PER_JUDGE = 30
TIER1_OVERALL_SPEARMAN = 0.70
TIER1_PER_JUDGE_SPEARMAN = 0.60

# Tier 2 thresholds — semantic alignment (promotion gate)
TIER2_MIN_TOTAL = 60
TIER2_MIN_PER_JUDGE = 20
TIER2_OVERALL_SPEARMAN = 0.70
TIER2_PER_JUDGE_SPEARMAN = 0.60

# Judges whose deterministic heuristic is known to be fallback-only for
# semantic alignment.  Listed here so test names and skip reasons are
# explicit.  The LLM-backed path is the promotion candidate.
HEURISTIC_FALLBACK_ONLY_JUDGES = {"answer_relevancy"}


# ---------------------------------------------------------------------------
# Judge dispatch
# ---------------------------------------------------------------------------

def _build_run_context(
    example: dict[str, Any],
    provider_context: Any = None,
) -> dict[str, Any]:
    """Build a run_context dict from a holdout example."""
    ctx: dict[str, Any] = {
        "output": {
            "retrieval_sources": example.get("retrieved_context") or [],
            "required_sources": example.get("gold_context") or [],
            "cited_sources": example.get("gold_context") or [],
            "question": example.get("query", ""),
            "answer": example.get("answer", ""),
        },
    }
    if provider_context is not None:
        ctx["provider_context"] = provider_context
    return ctx


def _no_model_provider_context() -> Any:
    """Return a QnaProviderContext with no model_id — forces heuristic fallback."""
    from apps_qna.integrations.provider_adapter import QnaProviderContext
    return QnaProviderContext(model_id="", max_tokens=0, temperature=0.0)


def _run_judge(judge_id: str, example: dict[str, Any]) -> float | None:
    """Run the correct judge in heuristic-fallback mode, return score or None.

    Injects a no-model provider_context to prevent env-based LLM auto-build
    from activating during heuristic sanity / semantic-fallback tests.
    """
    run_context = _build_run_context(example, provider_context=_no_model_provider_context())

    if judge_id == "context_recall":
        from apps_qna.engines.judges.context_recall_judge import grade
        score, _ = grade(None, run_context)
    elif judge_id == "context_precision":
        from apps_qna.engines.judges.context_precision_judge import grade
        score, _ = grade(None, run_context)
    elif judge_id == "answer_relevancy":
        from apps_qna.engines.judges.answer_relevancy_judge import grade
        score, _ = grade(None, run_context)
    else:
        return None

    if isinstance(score, (int, float)) and not math.isnan(score):
        return float(score)
    return None


def _run_judge_llm(
    judge_id: str,
    example: dict[str, Any],
    provider_context: Any,
) -> float | None:
    """Run a judge with LLM-backed provider_context injected."""
    run_context = _build_run_context(example, provider_context=provider_context)

    if judge_id == "context_recall":
        from apps_qna.engines.judges.context_recall_judge import ContextRecallJudge
        score, evidence = ContextRecallJudge().grade(None, run_context)
    elif judge_id == "context_precision":
        from apps_qna.engines.judges.context_precision_judge import ContextPrecisionJudge
        score, evidence = ContextPrecisionJudge().grade(None, run_context)
    elif judge_id == "answer_relevancy":
        from apps_qna.engines.judges.answer_relevancy_judge import AnswerRelevancyJudge
        score, evidence = AnswerRelevancyJudge().grade(None, run_context)
    else:
        return None

    if isinstance(score, (int, float)) and not math.isnan(score):
        # Verify LLM path was actually used (not heuristic fallback)
        if any("llm_judge" in e for e in evidence):
            return float(score)
        # LLM path failed silently, dispatch returned "", fell through to heuristic
        return None
    return None


def _check_llm_provider_available() -> tuple[bool, str]:
    """Check if any LLM provider is available via env creds or vLLM endpoint.

    Returns:
        (available, description) — description names the provider found.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    google_key = os.getenv("GOOGLE_API_KEY", "").strip()
    judge_override = os.getenv("JUDGE_PROVIDER", "").strip().lower()

    if judge_override == "anthropic" and anthropic_key:
        return True, f"anthropic ({os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')})"
    if judge_override == "openai" and openai_key:
        return True, f"openai ({os.getenv('OPENAI_MODEL', OPENAI_DEFAULT_MODEL_ID)})"
    if judge_override in ("gemini", "google") and google_key:
        return True, f"gemini ({(os.getenv('GOOGLE_AI_PRO_MODEL') or os.getenv('GEMINI_PRO_MODEL') or 'gemini-3.1-pro-preview')})"
    if judge_override in ("qwen", "vllm"):
        return True, f"vllm ({os.getenv('QWEN_VLLM_MODEL') or os.getenv('VLLM_MODEL_NAME', 'Qwen/Qwen2.5-32B-Instruct-AWQ')})"

    if not judge_override:
        if anthropic_key:
            return True, f"anthropic ({os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')})"
        if openai_key:
            return True, f"openai ({os.getenv('OPENAI_MODEL', OPENAI_DEFAULT_MODEL_ID)})"
        if google_key:
            return True, f"gemini ({(os.getenv('GOOGLE_AI_PRO_MODEL') or os.getenv('GEMINI_PRO_MODEL') or 'gemini-3.1-pro-preview')})"

    # Fall back: check vLLM endpoint reachability
    try:
        import httpx as _httpx
        base_url = os.getenv("VLLM_BASE_URL", "http://localhost:8000")
        resp = _httpx.get(f"{base_url}/v1/models", timeout=5.0)
        if resp.status_code == 200:
            return True, f"vllm ({os.getenv('QWEN_VLLM_MODEL') or os.getenv('VLLM_MODEL_NAME', 'Qwen/Qwen2.5-32B-Instruct-AWQ')})"
    except Exception:
        pass

    return False, "no provider available"


# ---------------------------------------------------------------------------
# Corpus loading helpers
# ---------------------------------------------------------------------------

def _load_corpus(path: Path) -> list[dict[str, Any]]:
    """Load and return a holdout YAML corpus, failing hard on problems."""
    assert path.exists(), f"Holdout corpus missing: {path}"
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, list), f"Holdout corpus must be a YAML list: {path.name}"
    return data


def _score_corpus(
    corpus: list[dict[str, Any]],
    judge_filter: set[str] | None = None,
) -> tuple[dict[str, tuple[list[float], list[float]]], list[str]]:
    """Run judges on corpus, return per-judge (auto, human) lists + failures."""
    by_judge: dict[str, tuple[list[float], list[float]]] = {
        jid: ([], []) for jid in VALID_JUDGE_IDS
    }
    failures: list[str] = []

    for ex in corpus:
        jid = ex["judge_id"]
        if judge_filter and jid not in judge_filter:
            continue
        auto = _run_judge(jid, ex)
        if auto is None:
            failures.append(f"{ex['example_id']}: judge returned non-numeric")
            continue
        by_judge[jid][0].append(auto)
        by_judge[jid][1].append(float(ex["human_score"]))

    return by_judge, failures


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def heuristic_corpus() -> list[dict[str, Any]]:
    return _load_corpus(HEURISTIC_SANITY_PATH)


@pytest.fixture(scope="module")
def semantic_corpus() -> list[dict[str, Any]]:
    return _load_corpus(SEMANTIC_ALIGNMENT_PATH)


# ===================================================================
# TIER 1 — Heuristic Sanity Baseline
# ===================================================================

class TestTier1HeuristicSanitySchema:
    """Validate Tier 1 corpus structure."""

    def test_corpus_exists(self):
        assert HEURISTIC_SANITY_PATH.exists(), f"Missing: {HEURISTIC_SANITY_PATH}"

    def test_corpus_is_list(self, heuristic_corpus: list):
        assert isinstance(heuristic_corpus, list)

    def test_minimum_total(self, heuristic_corpus: list):
        assert len(heuristic_corpus) >= TIER1_MIN_TOTAL, (
            f"Tier 1 needs >= {TIER1_MIN_TOTAL} examples, got {len(heuristic_corpus)}"
        )

    def test_minimum_per_judge(self, heuristic_corpus: list):
        counts: dict[str, int] = {}
        for ex in heuristic_corpus:
            jid = ex.get("judge_id", "")
            counts[jid] = counts.get(jid, 0) + 1
        for jid in VALID_JUDGE_IDS:
            assert counts.get(jid, 0) >= TIER1_MIN_PER_JUDGE, (
                f"Tier 1 judge_id={jid} needs >= {TIER1_MIN_PER_JUDGE}, got {counts.get(jid, 0)}"
            )

    def test_required_fields(self, heuristic_corpus: list):
        for i, ex in enumerate(heuristic_corpus):
            missing = REQUIRED_FIELDS - set(ex.keys())
            assert not missing, f"T1 example {i} ({ex.get('example_id','?')}) missing: {missing}"

    def test_judge_ids_valid(self, heuristic_corpus: list):
        for ex in heuristic_corpus:
            assert ex["judge_id"] in VALID_JUDGE_IDS, (
                f"Invalid judge_id: {ex['judge_id']} in {ex['example_id']}"
            )

    def test_human_score_range(self, heuristic_corpus: list):
        for ex in heuristic_corpus:
            s = ex["human_score"]
            assert isinstance(s, (int, float)) and 0.0 <= float(s) <= 1.0, (
                f"T1 human_score out of range in {ex['example_id']}: {s}"
            )

    def test_ids_unique(self, heuristic_corpus: list):
        ids = [ex["example_id"] for ex in heuristic_corpus]
        assert len(ids) == len(set(ids)), "Duplicate example_id in Tier 1"


class TestTier1HeuristicSanitySpearman:
    """Tier 1: prove heuristic fallback is stable and monotonic.

    Limitation: passing this tier does NOT prove semantic alignment.
    It only proves the deterministic heuristic produces a stable rank
    ordering against heuristic-aligned examples.
    """

    def test_overall_spearman(self, heuristic_corpus: list):
        by_judge, failures = _score_corpus(heuristic_corpus)
        assert not failures, "Non-numeric outputs:\n" + "\n".join(failures)

        all_auto = [s for jid in VALID_JUDGE_IDS for s in by_judge[jid][0]]
        all_human = [s for jid in VALID_JUDGE_IDS for s in by_judge[jid][1]]
        assert len(all_auto) >= TIER1_MIN_TOTAL

        corr, p = spearmanr(all_auto, all_human)
        assert corr >= TIER1_OVERALL_SPEARMAN, (
            f"Tier 1 overall Spearman FAILED: {corr:.4f} < {TIER1_OVERALL_SPEARMAN}"
        )

    def test_per_judge_spearman(self, heuristic_corpus: list):
        by_judge, failures = _score_corpus(heuristic_corpus)
        assert not failures, "Non-numeric outputs:\n" + "\n".join(failures)

        failing: list[str] = []
        results: dict[str, float] = {}
        for jid in VALID_JUDGE_IDS:
            a, h = by_judge[jid]
            assert len(a) >= TIER1_MIN_PER_JUDGE, f"T1 {jid}: too few ({len(a)})"
            corr, _ = spearmanr(a, h)
            results[jid] = round(corr, 4)
            if corr < TIER1_PER_JUDGE_SPEARMAN:
                failing.append(f"  {jid}: {corr:.4f} < {TIER1_PER_JUDGE_SPEARMAN}")

        if failing:
            pytest.fail(
                f"Tier 1 per-judge Spearman FAILED (heuristic sanity)\n"
                f"  results: {results}\n" + "\n".join(failing)
            )

    def test_tier1_summary(self, heuristic_corpus: list):
        """Emit Tier 1 summary for visibility."""
        by_judge, _ = _score_corpus(heuristic_corpus)
        all_auto = [s for jid in VALID_JUDGE_IDS for s in by_judge[jid][0]]
        all_human = [s for jid in VALID_JUDGE_IDS for s in by_judge[jid][1]]
        overall, _ = spearmanr(all_auto, all_human)

        per_judge = {}
        for jid in VALID_JUDGE_IDS:
            a, h = by_judge[jid]
            if len(a) >= 2:
                c, _ = spearmanr(a, h)
                per_judge[jid] = round(c, 4)

        print(f"\n{'='*60}")
        print("Tier 1 — Heuristic Sanity Baseline")
        print(f"{'='*60}")
        print(f"  corpus: {HEURISTIC_SANITY_PATH.name}")
        print(f"  total_examples: {len(all_auto)}")
        print(f"  overall_spearman: {overall:.4f}  (threshold: {TIER1_OVERALL_SPEARMAN})")
        print(f"  per_judge: {per_judge}")
        print(f"  NOTE: Passing Tier 1 proves heuristic stability, NOT semantic alignment.")
        print(f"{'='*60}")


# ===================================================================
# TIER 2 — Human Semantic Alignment Baseline
# ===================================================================

class TestTier2SemanticSchema:
    """Validate Tier 2 corpus structure."""

    def test_corpus_exists(self):
        assert SEMANTIC_ALIGNMENT_PATH.exists(), f"Missing: {SEMANTIC_ALIGNMENT_PATH}"

    def test_corpus_is_list(self, semantic_corpus: list):
        assert isinstance(semantic_corpus, list)

    def test_minimum_total(self, semantic_corpus: list):
        assert len(semantic_corpus) >= TIER2_MIN_TOTAL, (
            f"Tier 2 needs >= {TIER2_MIN_TOTAL} examples, got {len(semantic_corpus)}"
        )

    def test_minimum_per_judge(self, semantic_corpus: list):
        counts: dict[str, int] = {}
        for ex in semantic_corpus:
            jid = ex.get("judge_id", "")
            counts[jid] = counts.get(jid, 0) + 1
        for jid in VALID_JUDGE_IDS:
            assert counts.get(jid, 0) >= TIER2_MIN_PER_JUDGE, (
                f"Tier 2 judge_id={jid} needs >= {TIER2_MIN_PER_JUDGE}, got {counts.get(jid, 0)}"
            )

    def test_required_fields(self, semantic_corpus: list):
        for i, ex in enumerate(semantic_corpus):
            missing = REQUIRED_FIELDS - set(ex.keys())
            assert not missing, f"T2 example {i} ({ex.get('example_id','?')}) missing: {missing}"

    def test_ids_unique(self, semantic_corpus: list):
        ids = [ex["example_id"] for ex in semantic_corpus]
        assert len(ids) == len(set(ids)), "Duplicate example_id in Tier 2"

    def test_no_cross_corpus_id_collision(self, heuristic_corpus: list, semantic_corpus: list):
        t1_ids = {ex["example_id"] for ex in heuristic_corpus}
        t2_ids = {ex["example_id"] for ex in semantic_corpus}
        overlap = t1_ids & t2_ids
        assert not overlap, f"ID collision between Tier 1 and Tier 2: {overlap}"


class TestTier2SemanticSpearman:
    """Tier 2: prove judges track human semantic quality ranking.

    This is the **promotion-quality metric**.  A judge that passes Tier 2
    is eligible for production semantic scoring.  A judge that fails is
    classified as **fallback-only** (cheap regression sanity only).

    For ``answer_relevancy``, the deterministic heuristic is expected to
    fail because it scores surface signals, not semantic relevance.  That
    failure is asserted explicitly — it is not a bug.
    """

    def test_semantic_overall_spearman_promotable_judges(self, semantic_corpus: list):
        """Overall Spearman excluding fallback-only judges."""
        promotable = VALID_JUDGE_IDS - HEURISTIC_FALLBACK_ONLY_JUDGES
        by_judge, failures = _score_corpus(semantic_corpus, judge_filter=promotable)
        assert not failures, "Non-numeric outputs:\n" + "\n".join(failures)

        all_auto = [s for jid in promotable for s in by_judge[jid][0]]
        all_human = [s for jid in promotable for s in by_judge[jid][1]]
        assert len(all_auto) >= TIER2_MIN_PER_JUDGE * len(promotable)

        corr, _ = spearmanr(all_auto, all_human)
        assert corr >= TIER2_OVERALL_SPEARMAN, (
            f"Tier 2 overall Spearman FAILED (promotable judges only): "
            f"{corr:.4f} < {TIER2_OVERALL_SPEARMAN}"
        )

    def test_semantic_context_recall(self, semantic_corpus: list):
        """context_recall heuristic is semantically meaningful — should pass."""
        by_judge, failures = _score_corpus(semantic_corpus, judge_filter={"context_recall"})
        assert not failures
        a, h = by_judge["context_recall"]
        assert len(a) >= TIER2_MIN_PER_JUDGE
        corr, _ = spearmanr(a, h)
        assert corr >= TIER2_PER_JUDGE_SPEARMAN, (
            f"Tier 2 context_recall Spearman: {corr:.4f} < {TIER2_PER_JUDGE_SPEARMAN}"
        )

    def test_semantic_context_precision(self, semantic_corpus: list):
        """context_precision heuristic is semantically meaningful — should pass."""
        by_judge, failures = _score_corpus(semantic_corpus, judge_filter={"context_precision"})
        assert not failures
        a, h = by_judge["context_precision"]
        assert len(a) >= TIER2_MIN_PER_JUDGE
        corr, _ = spearmanr(a, h)
        assert corr >= TIER2_PER_JUDGE_SPEARMAN, (
            f"Tier 2 context_precision Spearman: {corr:.4f} < {TIER2_PER_JUDGE_SPEARMAN}"
        )

    def test_semantic_answer_relevancy_heuristic_is_fallback_only(self, semantic_corpus: list):
        """answer_relevancy deterministic heuristic fails Tier 2 — this is expected.

        The heuristic scores word overlap, length, and vocabulary uniqueness.
        It does NOT detect semantic relevance.  This test asserts the heuristic
        is BELOW the semantic threshold, confirming it is fallback-only.

        If this test starts failing (heuristic passes), either:
        (a) the heuristic was improved to detect semantic relevance → promote it, or
        (b) the semantic labels were gamed → fix the labels.
        """
        by_judge, failures = _score_corpus(semantic_corpus, judge_filter={"answer_relevancy"})
        assert not failures

        a, h = by_judge["answer_relevancy"]
        if len(a) < TIER2_MIN_PER_JUDGE:
            pytest.skip(f"Insufficient answer_relevancy examples ({len(a)})")

        corr, _ = spearmanr(a, h)

        # We ASSERT the heuristic is below threshold — it is fallback-only.
        # If this assertion fails, the heuristic has become semantically
        # aligned and can be reconsidered for promotion.
        assert corr < TIER2_PER_JUDGE_SPEARMAN, (
            f"answer_relevancy deterministic heuristic unexpectedly PASSED "
            f"Tier 2 semantic alignment (Spearman {corr:.4f} >= "
            f"{TIER2_PER_JUDGE_SPEARMAN}).  If the heuristic was improved, "
            f"remove it from HEURISTIC_FALLBACK_ONLY_JUDGES and promote. "
            f"If labels were gamed, fix the labels."
        )

    def _run_llm_judge_calibration(
        self,
        judge_id: str,
        corpus: list,
        provider_ctx: Any,
        min_per_judge: int,
        threshold: float,
    ) -> None:
        """Shared helper: run LLM-backed calibration for a single judge_id."""
        examples = [ex for ex in corpus if ex["judge_id"] == judge_id]
        assert len(examples) >= min_per_judge, (
            f"Need >= {min_per_judge} {judge_id} examples, got {len(examples)}"
        )

        auto_scores: list[float] = []
        human_scores: list[float] = []
        llm_failures: list[str] = []

        for ex in examples:
            score = _run_judge_llm(judge_id, ex, provider_ctx)
            if score is None:
                llm_failures.append(ex["example_id"])
                continue
            auto_scores.append(score)
            human_scores.append(float(ex["human_score"]))

        max_failures = max(1, len(examples) // 5)
        if len(llm_failures) > max_failures:
            pytest.fail(
                f"Too many LLM judge failures for {judge_id} "
                f"({len(llm_failures)}/{len(examples)}): {llm_failures[:5]}..."
            )

        if len(auto_scores) < min_per_judge:
            pytest.skip(
                f"{judge_id}: too few successful LLM scores ({len(auto_scores)}) "
                f"after {len(llm_failures)} failures."
            )

        corr, _ = spearmanr(auto_scores, human_scores)
        print(
            f"\n  {judge_id} (LLM-backed): "
            f"spearman={corr:.4f}, n={len(auto_scores)}, failures={len(llm_failures)}"
        )
        assert corr >= threshold, (
            f"LLM-backed {judge_id} Spearman FAILED: {corr:.4f} < {threshold}"
        )

    def test_semantic_context_recall_llm_path(self, semantic_corpus: list):
        """LLM-backed context_recall is the semantic promotion candidate."""
        available, desc = _check_llm_provider_available()
        if not available:
            pytest.skip(
                "LLM-backed context_recall judge requires provider creds in env. "
                "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, or JUDGE_PROVIDER=vllm."
            )
        from apps_qna.integrations.provider_adapter import build_judge_provider_context_from_env
        provider_ctx = build_judge_provider_context_from_env()
        assert provider_ctx is not None, f"No provider context built despite {desc}"
        print(f"\n  provider: {desc}")
        self._run_llm_judge_calibration(
            "context_recall", semantic_corpus, provider_ctx,
            TIER2_MIN_PER_JUDGE, TIER2_PER_JUDGE_SPEARMAN,
        )

    def test_semantic_context_precision_llm_path(self, semantic_corpus: list):
        """LLM-backed context_precision is the semantic promotion candidate."""
        available, desc = _check_llm_provider_available()
        if not available:
            pytest.skip(
                "LLM-backed context_precision judge requires provider creds in env. "
                "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, or JUDGE_PROVIDER=vllm."
            )
        from apps_qna.integrations.provider_adapter import build_judge_provider_context_from_env
        provider_ctx = build_judge_provider_context_from_env()
        assert provider_ctx is not None, f"No provider context built despite {desc}"
        print(f"\n  provider: {desc}")
        self._run_llm_judge_calibration(
            "context_precision", semantic_corpus, provider_ctx,
            TIER2_MIN_PER_JUDGE, TIER2_PER_JUDGE_SPEARMAN,
        )

    def test_semantic_answer_relevancy_llm_path(self, semantic_corpus: list):
        """LLM-backed answer_relevancy is the semantic promotion candidate.

        Requires any LLM provider creds in env (ANTHROPIC_API_KEY, OPENAI_API_KEY,
        GOOGLE_API_KEY, or JUDGE_PROVIDER=vllm with reachable endpoint).
        When no provider is available, skips explicitly — does NOT pass silently.
        """
        available, desc = _check_llm_provider_available()
        if not available:
            pytest.skip(
                "LLM-backed answer_relevancy judge requires provider creds in env. "
                "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, or JUDGE_PROVIDER=vllm."
            )

        from apps_qna.integrations.provider_adapter import build_judge_provider_context_from_env
        provider_ctx = build_judge_provider_context_from_env()
        assert provider_ctx is not None, f"No provider context built despite {desc}"
        print(f"\n  provider: {desc}")
        self._run_llm_judge_calibration(
            "answer_relevancy", semantic_corpus, provider_ctx,
            TIER2_MIN_PER_JUDGE, TIER2_PER_JUDGE_SPEARMAN,
        )

    def test_tier2_summary(self, semantic_corpus: list):
        """Emit Tier 2 summary for visibility."""
        by_judge, _ = _score_corpus(semantic_corpus)

        per_judge: dict[str, dict[str, Any]] = {}
        for jid in VALID_JUDGE_IDS:
            a, h = by_judge[jid]
            if len(a) >= 2:
                corr, _ = spearmanr(a, h)
                is_fallback = jid in HEURISTIC_FALLBACK_ONLY_JUDGES
                passed = corr >= TIER2_PER_JUDGE_SPEARMAN
                per_judge[jid] = {
                    "spearman": round(corr, 4),
                    "n": len(a),
                    "promotion_eligible": passed and not is_fallback,
                    "status": (
                        "FALLBACK_ONLY (expected)" if is_fallback and not passed
                        else "PASS (promotion eligible)" if passed
                        else "FAIL"
                    ),
                }

        print(f"\n{'='*60}")
        print("Tier 2 — Human Semantic Alignment Baseline")
        print(f"{'='*60}")
        print(f"  corpus: {SEMANTIC_ALIGNMENT_PATH.name}")
        print(f"  total_examples: {sum(d['n'] for d in per_judge.values())}")
        for jid, info in sorted(per_judge.items()):
            print(f"  {jid}:")
            print(f"    spearman={info['spearman']}, n={info['n']}")
            print(f"    promotion_eligible={info['promotion_eligible']}")
            print(f"    status={info['status']}")
        print(f"{'='*60}")
