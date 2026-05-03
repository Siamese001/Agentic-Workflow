# apps_qna — RUNBOOK

Operational guide for **building a card pack** and **loading it into a
ChatGPT 5.5-Thinking Project** for live interview use.

## 1. Build a card pack

### 1a. Gather inputs

You need five inputs for any interview:

1. **Interview slug** — short kebab-case identifier (e.g. `drew-clements`).
2. **Company profile** — name, division/practice, key anchors and vocabulary.
   Either via `--company <name>` plus YAML, or via
   `--research-from <apps_research artifact>`.
3. **Role** — title, level, JD as a markdown file (or text).
4. **Interviewers** — YAML file, one entry per interviewer:
   - `name`, `title`, `team`
   - `public_signals` (LinkedIn posts, talks, blog posts)
   - `technical_depth` (low / medium / high)
   - `hot_buttons` (topics they'll probe hard)
   - `lens` (their executive bias — e.g. "trust", "speed", "platform reuse")
5. **My experience** — YAML file with relevant achievements, STAR proofs, and
   leadership stories. Best built from `apps_rg` outputs.

### 1b. Run the builder

```bash
python -m apps_qna \
  --interview drew-clements \
  --company dentsu \
  --role "VP Decisioning Engineering" \
  --jd inputs/drew/jd.md \
  --interviewers inputs/drew/interviewers.yaml \
  --experience inputs/drew/my_experience.yaml \
  --research-from reports/research/research_brief_dentsu.md \
  --output reports/qna/drew-clements
```

### 1c. Lint the emitted pack

```bash
python -m apps_qna lint reports/qna/drew-clements
```

The linter enforces the routing-manifest invariants:

- One primary route per question class (no card collapses two primary routes).
- ≤2 specialist cards per route load.
- Max-context rule: no answer would load >3 cards (1 primary + 2 specialist).
- All 9 routes have at least one primary card.
- No orphan card (every emitted card is referenced by some route's load list).
- Always-on header is identical across all 18 cards.

Linter exit code:

- `0` — pack passes
- `1` — at least one invariant violated; per-card error messages emitted

## 2. Load into ChatGPT 5.5-Thinking

### 2a. Create a Project

ChatGPT → **Projects** → **New project** → name it after the interview slug.

### 2b. Set the model

Project settings → Model → **GPT-5.5 Thinking Standard**.

### 2c. Paste the pack as project instructions

The Drew Clements pack uses an **18-card concatenation** as the project
instruction set. Order matters — paste in numerical order (00, 01, 02, …, 17).

ChatGPT Project instructions have a length cap. If the full 18-card pack
exceeds the cap:

1. Paste cards 00, 01, 02 (always-on runtime spine) and 03 (Interviewer Lens)
   as project instructions.
2. Pin cards 04 (Company Overlay) and 14 (STAR Bank) as project files.
3. Load the rest as project files. ChatGPT will fetch the relevant ones
   per-route based on the routing manifest in card 01.

### 2d. Verify the runtime

Open a project chat and type:

> testing

ChatGPT must reply exactly:

> ingested

This confirms the non-q gate is active. If it answers with anything else, the
runtime is leaking — re-paste cards 00 and 02.

Then test a real q:

> q how would you build a governed agent for media planning?

ChatGPT should produce a route-4 (Architecture) answer in 4–5 bullets per the
release-gate spec.

## 3. Live interview operating procedure

- **q-prefix everything you want answered.** Notes typed without `q` are
  ingested silently and inform later answers.
- **One question at a time.** Don't stack qs.
- **For multi-interviewer panels**, the lens card for each interviewer is in
  the pack (`03_INTERVIEWER_LENS_<NAME>.md`). Tell the runtime which
  interviewer is speaking by typing `lens: <name>` (no q-prefix — this is a
  runtime hint, not a question).
- **For cross-exam follow-ups**, repeat the q-prefix. The runtime will route
  to card 16 (Cross-Exam) and go one technical level deeper.

## 4. Updating a pack mid-interview

If the interviewer reveals a new hot button (e.g. they ask three questions in
a row about MLflow), inject it as an ingest note:

> mlflow keeps coming up — emphasize model lifecycle in next answer

The runtime will silently bias toward card 10 (DS-to-Platform / MLOps) for
subsequent answers without re-routing.

## 5. Post-interview

```bash
# Archive the pack with the date
mv reports/qna/drew-clements reports/qna/drew-clements-2026-04-29

# Rebuild for the next round if there is one
python -m apps_qna --interview drew-clements-r2 ...
```

## 6. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| ChatGPT answers a non-q note as if it's a question | Card 02 not pasted or out of order | Re-paste cards 00–02 in order |
| Answers leak old interview names (e.g. say "Visa" during a Dentsu interview) | "No old-context gate" not loaded | Re-paste card 02 |
| Answers stack architecture + STAR + governance in one reply | Route purity check failed at build time | `python -m apps_qna lint <pack>` and rebuild |
| Linter reports orphan card | Template references not in any route's load list | Add to `route_registry.yaml` or remove the template |

## 7. References

- Source pattern: `C:\Users\amita\Documents\Dentsu\Drew Clements - 4.29.2026\`
- Bootstrap plan: `.windsurf/plans/apps-qna-bootstrap-c4f2a8.md`
- Routing manifest SSOT: `apps_qna/config/route_registry.yaml`

## Eval Harness (apps-eval-harness-closeout-b7c9d2 W3.P1)

The app-specific evaluation rubric and threshold profile live under
`apps_qna/config/domain_contract/` and are authoritative via the L4
`AppEvalRubricRecord` + `AppThresholdProfileRecord` registered through
UWG.

**Rubric**: `apps_qna/config/domain_contract/eval_rubrics.yaml`
**Threshold profile**: `apps_qna/config/domain_contract/threshold_profiles.yaml`
**Grader roster**: `apps_qna/config/domain_contract/grader_roster.yaml`

**HITL policy**: see `threshold_profiles.yaml` `hitl_policy` field
(`none` | `required_on_low` | `required_always`). Soft below-threshold
failures escalate when `required_on_low`; hard guardrail failures always
DENY regardless of policy.

**Run the advisory CI gate**:

`ash
python ops_scripts/ci/check_app_domain_harness_parity.py
`

Exit 0 with JSON report at `artifacts/ci/app_domain_harness_parity.json`.
Fail-closed mode via `APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=1`.

**Ledger**: per-run outcomes land in
`artifacts/ledgers/eval_harness_outcome.sqlite` (fail-soft — Exit pipeline
is never blocked by ledger errors). Weekly rollup:

`ash
python ops_scripts/calibration/eval_harness_weekly_report.py
`

Emits JSON + Markdown under `docs/reports/eval_harness/<YYYY-Www>.md`.
