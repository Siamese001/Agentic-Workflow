"""Evaluation judges package.

Two distinct abstractions live here side by side. They are NOT duplicates:

- ``llm_judge.py`` — synchronous RAG-evaluation harness (LJH2.1).
  Exposes the ``LLMJudge`` Protocol, ``JudgeScore`` immutable dataclass with
  deterministic digest, ``NullJudge`` stub, and ``GeminiJudge`` concrete
  implementation. Hardcoded RAG dimensions (faithfulness, answer_relevancy,
  context_precision, groundedness) with per-dimension CoT-first rubrics inlined
  as Python string constants in ``DIMENSION_RUBRICS``. Direct
  ``infrastructure.sdks_mcps.create_gemini_model`` binding.

- ``llm_judges.py`` (plural) — async ADG-governance review judges.
  Exposes async functions ``judge_gov_001``, ``judge_gov_003``, ``judge_sec_001``
  consuming ``EvidenceBundle`` + ``JudgeProvider`` + ``RubricEngine`` and
  producing ``JudgeVerdict``. Rubrics fetched from ``rubrics.json`` via
  ``RubricEngine``. Registered in ``LLM_JUDGES`` dict keyed by rubric_id.
  Pluggable backend (use ``provider_registry.py::create_default_registry``).

Do NOT consolidate. They serve different surfaces (RAG eval vs ADG-governance
review) and live at different abstraction levels (judge-impl vs judge-runner).

Default judge backend selection (audit 2026-05-02):
* ``provider_registry.create_default_registry(prefer_local=True)`` — local
  Qwen vLLM wins as default when registered (``VLLM_BASE_URL`` set) AND
  ``JUDGE_PROVIDER`` is not an explicit external override.
* External providers (Gemini, OpenAI, Anthropic) become escalation paths
  rather than the runtime default.
"""
