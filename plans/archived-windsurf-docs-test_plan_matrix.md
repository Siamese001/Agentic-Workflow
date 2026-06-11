---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\test_plan_matrix.md'
original_relative_path: 'test_plan_matrix.md'
source_sha256: 5c31dd8bcdf1ac6814f94bbbc7c770d7b9657decedd2d1855e7150dab79ed24f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W7 — Test Plan: Provider-matrix Golden Tests + Apply-Patch Schema Tests

**Plan**: `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`
**Waves closed**: W7 phases 7.1, 7.2
**Scope**: Spec regression tests for (a) provider-matrix rendering consistency
across Anthropic / OpenAI GPT-4.1 / OpenAI o-series / Gemini 3, and (b)
apply-patch output schema for code-editing agents.

## 1. Objectives

1. **Detect rendering drift** — any change to slot composition, delimiters, or
   adapter logic that alters a provider-rendered prompt triggers a golden diff.
2. **Enforce cache prefix stability** — `S0 + D0 + I0` prefix is byte-identical
   across two renders of the same BOM (closes G14 in CI).
3. **Enforce response-schema threading** — tests assert `response_schema` on
   `AgentSpec` surfaces as `response_format` / `response_schema` on the
   captured API request payload (not in prompt body).
4. **Lock the apply-patch schema** — `apps_rg` code-edit outputs parse under
   the apply-patch grammar and round-trip to a valid diff.

## 2. Test harness structure

Proposed location: `tests/unit/prompt_governance/providers/`

```
tests/unit/prompt_governance/providers/
├── __init__.py
├── conftest.py                        # Fixtures: PromptBOM factory, mocked provider clients
├── goldens/
│   ├── anthropic/
│   │   ├── rag_heavy.prompt.txt
│   │   ├── agentic_coding.prompt.txt
│   │   ├── long_context_hoist.prompt.txt
│   │   └── ...
│   ├── openai_gpt41/
│   │   └── ...
│   ├── openai_oseries/
│   │   └── ...
│   └── gemini/
│       └── ...
├── test_provider_matrix.py            # Parametrized golden tests
├── test_cache_prefix_stability.py     # G14 — two renders, byte-diff S0+D0+I0
├── test_response_schema_threading.py  # G8 — observed API payload check
└── test_apply_patch_schema.py         # G23 — apply-patch grammar round-trip
```

## 3. Fixture shape

```python
@dataclass(frozen=True)
class ProviderMatrixCase:
    case_id: str                   # "rag_heavy", "agentic_coding", ...
    bom: PromptBOM
    secret_key: bytes
    expected_providers: tuple[str, ...]  # which adapters to exercise
    response_schema: dict | None
```

Case IDs (initial coverage, extend in follow-on waves):

| Case ID | Intent class | Scenario |
|---------|--------------|----------|
| `rag_minimal` | `rag` | Single small must-use chunk, no optional chunks |
| `rag_heavy` | `research` | ≥ 8k chars across ≥ 5 must-use chunks — triggers long-context hoist |
| `agentic_coding` | `code` | Agentic reminders mixin active, tools attached |
| `healing_reentry` | `healing` | H0 slot populated, re-entry validation required |
| `thinking_high` | `reasoning` | `thinking_level="high"` on routing meta |
| `context_only` | `evaluation` | D0_CONTEXT_ONLY fence active |
| `context_plus_internal` | `chat` | D0_CONTEXT_PLUS_INTERNAL fence active |
| `o_series_reasoning` | `reasoning` | o-series adapter path; verifies `developer` role routing |
| `gemini_instructions_after` | `research` | Gemini adapter places instructions after data |
| `model_identity_exposed` | `chat` | `AgentSpec.expose_model_identity=True` |

## 4. Golden-diff policy

1. **Whitespace-normalized diff** — tests normalize trailing whitespace and
   line-ending style before compare (prevents cosmetic churn).
2. **Salted fields stripped** — `idempotency_nonce`, timestamps, and
   replay_keys are redacted to `<REDACTED>` in goldens.
3. **Rejection rule** — any diff beyond whitespace normalization fails the
   test. Regenerating a golden requires `PYTEST_REGENERATE_GOLDENS=1` set
   and a manual commit acknowledging the new golden.
4. **Coverage guard** — missing golden for any declared `(case_id, provider)`
   tuple is a test error, not a skip.

## 5. Cache-prefix stability test (G14)

```python
def test_cache_prefix_stability_two_renders(matrix_case):
    artifact_a = AirlockAssembler.assemble_from_bom(matrix_case.bom, SECRET_KEY)
    artifact_b = AirlockAssembler.assemble_from_bom(matrix_case.bom, SECRET_KEY)

    prefix_a = _extract_prefix(artifact_a)   # S0 + D0 + I0 bytes
    prefix_b = _extract_prefix(artifact_b)

    assert prefix_a == prefix_b, "cache prefix drift detected"
    assert artifact_a.manifest_hash == artifact_b.manifest_hash
    assert artifact_a.idempotency_nonce != artifact_b.idempotency_nonce
```

Failure mode surfaced: any new dynamic content (timestamp, UUID, env-var
reference) inside S0/D0/I0 causes drift — caught in CI.

## 6. Response-schema threading test (G8)

Mock each provider client; capture the kwargs of the first `.create()` call;
assert the schema appears in the native API field, not inlined:

```python
def test_response_schema_threads_to_api_field(mock_openai_client, matrix_case):
    _dispatch_artifact(matrix_case.artifact, provider="openai_gpt41")
    captured = mock_openai_client.chat.completions.create.call_args.kwargs
    assert "response_format" in captured
    assert captured["response_format"]["type"] == "json_schema"
    # Assert NOT stringified into user content
    assert "response_schema" not in captured["messages"][-1]["content"]
```

Symmetric tests for Anthropic (`response_format` via tool-use JSON-mode
shape), and Gemini (`response_schema` field).

## 7. Apply-patch schema test (G23)

```python
APPLY_PATCH_SAMPLE = """\
*** Begin Patch
*** Update File: foo/bar.py
@@
-old_line
+new_line
*** End Patch
"""

def test_apply_patch_roundtrips(tmp_path):
    validator = ApplyPatchValidator()
    assert validator.validate(APPLY_PATCH_SAMPLE).ok
    # Round-trip: parse → re-serialize → byte-match
    parsed = validator.parse(APPLY_PATCH_SAMPLE)
    assert validator.serialize(parsed).strip() == APPLY_PATCH_SAMPLE.strip()


@pytest.mark.parametrize("malformed", [
    "not a patch",
    "*** Begin Patch\n*** End Patch\n",  # empty body
    "*** Begin Patch\n@@\n+missing file header\n*** End Patch\n",
])
def test_apply_patch_rejects_malformed(malformed):
    validator = ApplyPatchValidator()
    assert not validator.validate(malformed).ok
```

## 8. CI integration

- **Gate**: `ops_scripts/ci/check_provider_matrix_goldens.py` — runs the matrix
  suite; fails on missing golden or diff beyond whitespace normalization.
- **Gate**: `ops_scripts/ci/check_cache_prefix_stability.py` — standalone
  prefix-stability check; runs on PRs that touch `assembly_stage.py`,
  `prompt_assembler.py`, mixin registry, or template catalog.
- **Gate**: `ops_scripts/ci/check_apply_patch_schema.py` — validates any
  committed golden patch samples parse cleanly.

## 9. Execution dependencies

1. ADR-PROMPT-ASSEMBLY-001 adapters must be implemented first (W2 of
   `reception-hardening-9c4e2b`); tests build on adapter interfaces.
2. Provider-aware token counter (ADR-PA-002 §6) must exist before
   `rag_heavy` case can assert realistic token estimates.
3. `AgentSpec.response_schema` + `AgentSpec.parallel_tool_calls` fields must
   be landed before their tests are meaningful.

## 10. Success criteria

- ≥ 10 matrix cases landed with goldens for all four providers.
- Cache-prefix stability test runs green on 3 consecutive CI runs.
- Response-schema threading test passes across all four providers.
- Apply-patch schema test covers both valid and malformed samples.
- CI gate additions cost ≤ 15 s total per full run.
