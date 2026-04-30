# apps_qna — TEST_STRATEGY

## Test surface

| Layer | Tests | Coverage target |
|---|---|---|
| Templates | render-under-StrictUndefined for all 18 templates with the synthetic-mini fixture | 100% (every template renders) |
| Builder | smoke fixture → 4-card mini pack; full Drew canary fixture → 18-card pack | end-to-end |
| Linter | 6 negative fixtures (one per invariant) + 1 positive | one negative path per validator |
| Adapters | 3 round-trip tests against checked-in fixtures from each source app | every adapter |
| Types | pydantic schema export + JSON-schema diff | structural |
| CLI | argparse smoke + dry-run + lint subcommand | each codepath |

## Fixtures

```
apps_qna/tests/fixtures/
├── synthetic_mini/           # Wave 2 smoke (4 cards only)
│   ├── interview.yaml
│   ├── interviewers.yaml
│   ├── jd.md
│   └── experience.yaml
├── drew_clements/            # Wave 5 canary (18 cards full)
│   ├── interview.yaml
│   ├── interviewers.yaml
│   ├── company.yaml
│   ├── role.yaml
│   ├── jd.md
│   ├── experience.yaml
│   └── research_brief.md
├── invalid_packs/
│   ├── duplicate_primary/    # LINT-1 negative
│   ├── too_many_specialists/ # LINT-2 negative
│   ├── exceeds_context/      # LINT-3 negative
│   ├── missing_route/        # LINT-4 negative
│   ├── orphan_card/          # LINT-5 negative
│   └── header_drift/         # LINT-6 negative
└── valid_pack/               # all linter checks pass
```

## Test commands

```bash
# All tests
pytest apps_qna/

# Templates only (fast, no fixtures beyond synthetic_mini)
pytest apps_qna/tests/test_templates_render.py -v

# Linter — all 6 invariants
pytest apps_qna/tests/test_validators.py -v

# Drew canary
pytest apps_qna/tests/test_drew_canary.py -v

# Adapters
pytest apps_qna/tests/test_adapters.py -v
```

## Drew canary equivalence

The canary does **not** require byte-identical output to the hand-authored
Drew pack. It asserts **structural** equivalence:

- All 18 expected card filenames are emitted.
- Each emitted card's level-1 heading matches the hand-authored heading.
- Each emitted card's `## Purpose` paragraph mentions the same key concept
  (verified by keyword set).
- The emitted `pack_manifest.json` lists all 18 cards in numerical order.
- The route registry's load lists reference only emitted card filenames
  (LINT-4 + LINT-5 pass).

## What is NOT tested here

- ChatGPT 5.5-Thinking actually consuming the pack — that is a manual
  RUNBOOK §2d step.
- The substantive correctness of interview content — that is the user's
  responsibility (the experience YAML is theirs).
- Performance — packs are tiny (≤200KB total), no SLO needed.

## Test data hygiene

- Drew canary fixtures are **reverse-engineered** from the hand-authored cards
  at `C:\Users\amita\Documents\Dentsu\Drew Clements - 4.29.2026\`. The
  fixtures contain Amit's real experience data. They are checked into the
  repo because that hand-authored content is the validated baseline.
- Synthetic mini fixtures are **synthetic** — fictional company / role /
  experience. Safe for public CI.
