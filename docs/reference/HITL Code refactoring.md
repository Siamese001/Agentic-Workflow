Objective

Implement a lightweight, repo-local "Refactor Review Gate" for Windsurf that surfaces design options only when there is real refactor ambiguity.
This is NOT HITL.
Do not use HITL terminology, agentic approval semantics, or probabilistic human-in-the-loop concepts for this feature.
This is a deterministic refactor decision checkpoint for Windsurf behavior during code changes.

Critical rename / cleanup requirement

First, find and remove or rewrite any prior repo content that incorrectly uses HITL language for refactoring behavior.
If prior files, rules, comments, docs, prompts, workflows, hooks, or configs describe refactor ambiguity handling as HITL, rename and normalize them to:
- Refactor Review Gate
- Design Decision Checkpoint
- Refactor Decision Review

Do not leave mixed terminology behind.
The repo should clearly separate:
- true HITL for future agentic / high-risk approval flows
from
- this refactor-specific design review checkpoint

What I want functionally

I want Windsurf to:
1. Proceed normally when there is one clearly dominant refactor path.
2. Pause and surface options only when there are multiple materially different refactor approaches with meaningful tradeoffs.
3. Avoid fake option spam when there is one obvious recommendation and the alternatives are weak.
4. Present a bounded decision packet when ambiguity is real:
   - recommended approach
   - 1 to 2 plausible alternatives
   - tradeoffs
   - blast radius
   - rollback difficulty
   - why this is ambiguous
5. Prefer planning before implementation for ambiguous refactors.
6. Log these decision points so the heuristic can be tuned later.
7. Keep this lightweight. No ML model. No heavy scoring framework. No overengineering.

Implementation target

Implement this with the correct Windsurf primitives:
- behavior policy in workspace rules and/or AGENTS.md
- enforcement / telemetry in hooks
- use Plan mode semantics as the intended user-facing decision checkpoint
- do NOT implement this primarily as a Skill or Workflow unless absolutely required
- if a Skill or Workflow already exists for this and it is the wrong abstraction, remove or downgrade it

Required repo changes

1. Audit current repo
Search for all existing references to:
- HITL
- human in the loop
- approval gate
- review gate
- ambiguity
- refactor decision
- refactor checkpoint
inside:
- .windsurf/
- repo docs
- prompts
- hook scripts
- workflow files
- AGENTS.md files
- comments related to Windsurf behavior

Produce a short findings summary first:
- what exists now
- what is misnamed
- what should be removed
- what should be retained and renamed

2. Implement rule layer
Create or update a workspace rule for the refactor decision policy.
Suggested file:
.windsurf/rules/refactor-review-gate.md

Intent of the rule:
- if refactor is straightforward, continue
- if there are multiple materially different valid approaches, stop and present a design checkpoint
- prefer concise options
- avoid presenting low-quality or obviously inferior alternatives
- if ambiguity is architectural or cross-cutting, prefer planning before write actions
- after user choice, continue implementation aligned to the selected option

Keep the rule concise, explicit, and behavior-oriented.
Do not write vague principles.
Do not use the term HITL anywhere in this file.

If appropriate, also use AGENTS.md only for directory-scoped reinforcement, not as the primary repo-wide policy.

3. Implement hook layer
Create or update:
.windsurf/hooks.json

Use hooks only where they fit:
- pre_write_code to gate risky writes when a real design checkpoint should have occurred first
- pre_run_command if necessary for risky refactor-related command execution
- post_cascade_response and/or post_cascade_response_with_transcript for telemetry / audit logging
- keep hooks fast and minimal

Important:
- do not create hooks that spam or block routine edits
- only enforce around meaningful ambiguity / larger refactor cases
- if needed, use simple heuristics such as edit breadth, number of files touched, protected paths, architectural files, dependency changes, or broad interface shifts
- avoid brittle overfitting

4. Add lightweight telemetry
Implement a minimal logging path for later refinement.
This can be JSONL or SQLite, whichever is simpler and already idiomatic in the repo.

Log fields like:
- timestamp
- trajectory / execution id if available
- files touched
- checkpoint triggered yes/no
- reason
- recommended option
- user-selected option if observable
- whether revert happened later if inferable
- whether hook blocked a write or command

No ML training pipeline.
Just structured data capture for future tuning.

5. Remove or rewrite wrong abstractions
If there are Skills or Workflows that were previously used to simulate this behavior and they are not the right abstraction:
- remove them, or
- reduce them to optional helpers only
But the primary implementation must live in:
- rules / AGENTS for behavior
- hooks for enforcement and telemetry

6. Update documentation
Create or update a short repo doc that explains:
- what Refactor Review Gate is
- what it is not
- why it is not HITL
- where it lives in Windsurf config
- how it triggers
- what gets logged
- how to tune it later

Suggested doc name:
.windsurf/docs/refactor_review_gate.md
or another existing documentation location if there is a stronger SSOT

Decision policy to encode

Use this lightweight logic:

Trigger the Refactor Review Gate only when one or more are true:
- multiple materially different implementation paths are plausible
- tradeoffs involve architecture, shared interfaces, dependency boundaries, or large blast radius
- change touches many files or core framework / platform files
- rollback is non-trivial
- command execution or writes would commit to a design path that is costly to reverse

Do NOT trigger when:
- there is one clearly dominant low-risk option
- alternatives are cosmetic or obviously worse
- the change is local, reversible, and narrow

Expected output packet when triggered

When the gate triggers, Windsurf should present something like:
- Recommended path
- Alternative A
- Alternative B if genuinely plausible
- Why this is a real decision
- Tradeoffs
- Blast radius
- Rollback difficulty
- Proposed next action

Do not dump excessive prose.
Do not fabricate three options if only one or two are real.

Constraints

- Preserve existing repo conventions where reasonable
- Minimize implementation complexity
- Prefer modification over proliferation of new files
- Keep rules concise
- Keep hooks fast
- No fake probabilistic confidence numbers
- No HITL language
- No agentic approval framework language
- No large framework build-out
- No speculative ML calibration system

Execution mode

Work in two phases.

Phase 1:
- inspect current repo state
- summarize findings
- propose exact file changes

Phase 2:
- implement the changes
- show diffs
- explain any removed or renamed prior HITL artifacts

Deliverables

Return:
1. audit summary
2. implementation plan
3. files created / updated
4. exact terminology changes made
5. final explanation of how the Refactor Review Gate now works

Success criteria

This succeeds only if:
- the repo no longer conflates refactor review with HITL
- Windsurf behavior for this feature is implemented in the right configuration surfaces
- the solution is lightweight and practical
- ambiguity triggers a review checkpoint
- routine refactors do not get spammed
- telemetry exists for future tuning