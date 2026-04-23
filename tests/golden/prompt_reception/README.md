# Prompt-Reception Golden-Replay Fixtures

**Plan:** `.windsurf/plans/prompt-reception-followups-a7b3c4.md`, phase RH5B.2.

## Purpose

Freeze byte-exact `PromptMessages` IR outputs for the 8 apps so regressions in
any of the following land as a test failure rather than silent drift:

- Slot assembly order (`CompiledPromptArtifact.slots_used`)
- Per-slot content rendering
- Adapter projection (`PromptMessages.slot_map` keys + values)
- Replay-key digest scheme (`rkslot-v1-…` prefix)
- E0 exemplar parsing (`USER:/ASSISTANT:` pairs)

## Fixture shape

Each fixture is a JSON file named `<app>__<scenario>.json` containing:

```json
{
  "fixture_schema_version": 1,
  "app": "apps_research",
  "scenario": "brief_thematic_minimal",
  "inputs": {
    "adapter_version": "v2",
    "exemplar_task_class": null,
    "raw_u0": "…",
    "raw_c0": "…",
    "slots": [["S0", "…"], ["U0", "…"]]
  },
  "expected": {
    "slots_used": ["S0", "U0"],
    "slot_map": {"S0": "…", "U0": "…"},
    "ordered_slots": ["S0", "U0"],
    "replay_key_prefix": "rkslot-v1-",
    "replay_key_digest_length": 64
  }
}
```

The digest itself is NOT asserted byte-exactly, only `prefix` and
`digest_length`, so trivial canonicalization changes (e.g. a trailing
whitespace tweak) don't rotate every fixture.

## Harness

`tests/golden/prompt_reception/test_golden_replay.py` walks every
`fixtures/*.json` file and:

1. Reconstructs a `CompiledPromptArtifact` and slots from `inputs`.
2. Projects to `PromptMessages` via `artifact.to_prompt_messages(slots=...)`.
3. Asserts each field in `expected`.

A missing-fixture case (empty `fixtures/` dir) is a warning, not a
failure, so the harness is landable before every app has a recorded
fixture — onboarding is incremental.

## Recording a new fixture

Use the helper in `tests/golden/prompt_reception/_recorder.py`:

```python
from tests.golden.prompt_reception._recorder import record_fixture

record_fixture(
    app="apps_rfp",
    scenario="proposal_section_draft",
    slots={"S0": "…", "U0": "…"},
    output_dir="tests/golden/prompt_reception/fixtures",
)
```

The recorder snapshots the current `PromptMessages` shape and writes a
fixture file. Run once against known-good assembly output, then commit.

## Deferred

- **Pre-commit wiring** — a hook that runs the harness on every commit is
  captured as deferred scope. Runtime cost is non-trivial (imports
  pydantic + agentic_core.L2_execution) and the harness is CI-friendly.
  Until we have representative fixtures for ≥ 3 apps, pre-commit wiring
  adds cost without catching anything.
- **One fixture per app** — the initial commit lands with ONE
  representative fixture (`apps_research__brief_thematic_minimal.json`)
  to prove the harness. Recording the remaining 4 app fixtures is
  deferred scope.
