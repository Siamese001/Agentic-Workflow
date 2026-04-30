# apps_qna — SVP_ENGINEERING_REVIEW

## Charter

`apps_qna` builds reusable interview-prep card packs from typed inputs. It
generalizes a manually-validated pattern (the Drew Clements / Dentsu pack)
into a library + CLI so the next interview costs minutes, not hours.

## Why this is an SVP-worthy app, scoped tight

This is a **single-user, offline tool**. It does not run in production. It
does not serve clients. It produces markdown files and validates them.

That scope is the architectural decision (Author-Gate, 2026-04-30,
confidence 0.88, no precedent): "Card-based runtime — runtime cards are the
deliverable, not an engine."

The trade-off accepted: no programmatic ChatGPT API call, no governance plane
integration, no source register / claim-type labels. The cost is paying the
apps_* contract minimum (this doc set, types, tests, lint discipline) while
deliberately **not** paying the apps_research contract for source register
and provenance.

## Operational simplicity

- No subprocess except via the documented CLI argparse.
- No network. No API keys.
- No state outside the `--output` directory and a `pack_manifest.json`.
- No cross-app coupling at import time (adapters lazy-load).
- Six required apps_* contract docs are scoped to what this app actually
  needs, not padded to match apps_research.

## Dependency hygiene

- Runtime deps: `pydantic>=2`, `jinja2`, `pyyaml`. All already in the repo.
- Test deps: `pytest` (already pinned).
- No new third-party deps. No local LLMs. No database.

## Archival over deletion

If this module is deprecated:

- The card pattern itself is documented (RUNBOOK.md + TECHNICAL_SPEC.md), so
  the knowledge survives.
- The 18 templates are the durable artifact.
- Move the module to `archives/apps_qna_<DATE>/` per the constitutional
  archival pattern. Don't `rm -rf`.

## ADRs in scope

This bootstrap does NOT propose an ADR. It is a single-user offline tool
adding a new `apps_*` module under the existing apps_* contract — that
contract was set by ADR-001 (apps_* layer separation) and ADR-005 (typed
artifact discipline). No architecture invariant is changed.

If a Wave 4 adapter exposes an unanticipated coupling between
`apps_research` and `apps_qna`, that adapter design will get its own ADR
before merge.

## Zero-regression posture

This app is a **net-add**:

- No existing file is modified.
- No existing test is altered.
- No existing CI gate is touched.
- No existing apps_* artifact format is changed (adapters are read-only).

If Wave 4 finds a legitimate need to extend `apps_research` artifacts (e.g.
a new section type), that extension goes back through `apps_research`'s own
review, not through `apps_qna`.

## What an SVP would push back on

- **"Why a custom Jinja template library?"** — Because the Drew pack is
  validated and we are generalizing exactly that shape. Anything more
  abstract (e.g. a card-DSL) over-builds for a one-developer use case.
- **"Why not just hand-edit the Drew pack each time?"** — We already feel
  the cost of doing that. The next 3+ interviews amortize this build.
- **"Why not call the ChatGPT API directly?"** — User explicitly chose a
  ChatGPT-Project-paste workflow because GPT-5.5-Thinking Standard via the
  Project UI gives them the model behavior they want without API/billing
  plumbing. This is documented in the Author-Gate decision.
- **"Why no governance / source register?"** — Because the artifacts are
  pasted into ChatGPT and read by a human under interview pressure. They
  are not a system of record. Adding governance pays a tax this use case
  doesn't owe.

## Acceptance for SVP

The bootstrap is acceptable when:

- All 5 waves of the bootstrap plan complete green.
- Drew canary regenerates 18 structurally-equivalent cards from typed inputs.
- `pytest apps_qna/` is green.
- `python -m apps_qna lint reports/qna/drew-clements` exits 0.
- The next real interview's pack takes < 30 minutes of human work end-to-end.
