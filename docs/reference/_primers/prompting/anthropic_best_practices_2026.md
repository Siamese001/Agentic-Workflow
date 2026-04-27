# Anthropic Claude — Prompting Best Practices (distilled, 2026-04)

Source: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>
(retrieved 2026-04-23 for Claude Opus 4.7 / Sonnet 4.6)

This is a distillation for internal cross-mapping against the agentic_core prompt
assembler. It is NOT a substitute for the upstream doc — re-fetch before major
prompt-engineering work.

---

## 1. General principles

### 1.1 Be clear and direct
- Treat Claude as a brilliant but new employee with no tribal context.
- Specify desired output format AND constraints.
- Use numbered lists when step order matters.
- Golden rule: if a colleague would be confused by the prompt, so will Claude.

### 1.2 Add context / motivation
- Explain *why* a rule exists, not just the rule. Claude generalises better
  from motivated rules.

### 1.3 Use examples effectively (few-shot / multishot)
- Few well-crafted examples > many mediocre ones.
- Examples must be **relevant** (mirror the actual use case),
  **diverse** (cover edge cases; vary enough that no unintended pattern is learned),
  and **structured**.
- Wrap in `<example>...</example>`; group multiple in `<examples>...</examples>`.

### 1.4 Structure prompts with XML tags (CORNERSTONE)
- XML tags disambiguate instructions from context from examples from input.
- Use consistent, descriptive names: `<instructions>`, `<context>`, `<input>`,
  `<example>`, `<documents>`, `<document index="n">`, `<thinking>`, `<answer>`.
- Nest when content has a natural hierarchy.
- This is the single most important structural recommendation.

### 1.5 Give Claude a role
- Set a role in the `system` parameter (not in the user turn).
- Even one sentence ("You are a helpful coding assistant specializing in Python.")
  measurably changes tone and focus.

### 1.6 Long context prompting (20k+ tokens)
- **Put longform data at the TOP** of the prompt, above queries, instructions, and
  examples. Up to 30% quality gain observed for multi-document tasks.
- Wrap each document: `<document><document_content>...</document_content><source>...</source></document>`.
- Ask Claude to **quote relevant passages first** before answering, for long-doc tasks.

---

## 2. Output and formatting

### 2.1 Tell Claude what to DO (not what NOT to do)
- Positive instructions outperform negative ones.
- "Write in flowing prose paragraphs" > "Do not use markdown."

### 2.2 XML format indicators for output
- "Write your response inside `<answer>...</answer>`" produces more reliable
  structure than prose-level instructions.

### 2.3 Match prompt style to desired output style
- Markdown in → markdown out. If you want plain prose, write the prompt in plain prose.

### 2.4 Prefill (migrating away on Claude 4.6+)
- Prefilling the last assistant turn is being deprecated on Claude 4.6+ /
  Mythos Preview (returns 400).
- Older models still support it. New code should rely on instruction-following
  and structured-output tags instead.

---

## 3. Tool use

### 3.1 Be explicit about action vs suggestion
- "Implement" vs "suggest changes" is a meaningful distinction Claude listens to.
- Use `<default_to_action>` or `<do_not_act_before_instructions>` XML blocks to
  pin the policy.

### 3.2 Don't over-scream at the model
- On Opus 4.5+ / 4.6+, "CRITICAL: YOU MUST ..." can cause over-triggering.
- Prefer calm, normal prompting.

### 3.3 Parallel tool calls
- Latest models parallelise well when the tools are independent.
- Instruct explicitly if you want parallel execution.

---

## 4. Thinking and reasoning

### 4.1 Adaptive thinking (Opus 4.6 / Sonnet 4.6)
- `thinking: {type: "adaptive"}` + `output_config.effort` ∈ {low, medium, high, max, xhigh}.
- Replaces older `thinking: {type: "enabled", budget_tokens: N}` pattern.
- Model decides when and how much to think. In Anthropic evals, adaptive beats
  manual budgets.

### 4.2 Prefer general over prescriptive
- "Think thoroughly" often outperforms a hand-written step-by-step plan.

### 4.3 Multishot examples work with thinking
- Put `<thinking>...</thinking>` tags inside few-shot examples. Claude generalises
  the demonstrated reasoning style into its own `<thinking>` blocks.

### 4.4 Manual CoT fallback (when thinking is off)
- Ask Claude to reason step by step.
- Structure with `<thinking>` and `<answer>` tags to separate reasoning from output.

### 4.5 Self-check
- Append "Before you finish, verify your answer against [criteria]."
- Catches errors reliably on coding and math.

---

## 5. Agentic systems

### 5.1 Long-horizon state tracking
- Claude 4.5/4.6 have **context awareness**: the model tracks remaining context
  window during the conversation.
- If your harness compacts or persists state, TELL the model so via system prompt
  — otherwise Claude may prematurely wrap up approaching the limit.

### 5.2 Multi-context-window workflows
- Use a different prompt for the first window (setup/tests) vs subsequent windows
  (iteration).
- Persist state to disk (`tests.json`, `progress.txt`, git logs).
- Prefer starting fresh over compaction — Claude 4.6 is excellent at rediscovering
  state from the filesystem.
- Provide verification tools (Playwright, computer-use) for autonomous runs.

### 5.3 Balance autonomy vs safety
- Explicit policy blocks about "when to ask" vs "when to act" are honoured.
- Dial them with positive ("default_to_action") or restraining ("do_not_act_before_instructions") XML blocks.

### 5.4 Reduce hallucinations in agentic coding
- Ground in repo truth: "Call `pwd`; only read/write inside this directory."
- Ask for verification: run tests, integration checks, before declaring done.

---

## 6. Claude Opus 4.7 specific tips

- **Literal instruction following**: 4.7 follows instructions more literally.
  Review existing prompts for instructions you no longer want strictly honoured.
- **Subagent spawning**: controllable via system prompt.
- **User-facing progress updates**: more literal unless told otherwise.
- **Design/frontend defaults**: stronger defaults; override explicitly if needed.

---

## Cross-map crib sheet (for this repo's assembler)

| Anthropic concept | Map to assembler slot | Notes |
|---|---|---|
| `system` role / persona | S0 + role block derived from AgentSpec | Currently S0 is generic |
| Constitutional / policy text | D0 (injection fence) | OK, but not XML-wrapped |
| Mixins / capabilities | I0 | Currently `\n\n` joined, not `<capabilities>`-wrapped |
| Few-shot examples | E0 (proposed new slot) | Currently mixed into I0 via GoldenContextMixin |
| Long documents / RAG | C0 | Anthropic says put at TOP, we put in middle |
| CoT / thinking scaffold | M0 (proposed new slot) | Currently missing entirely |
| User task | U0 | OK; already `<U0>...</U0>` wrapped |
| Healing proposal | H0 (proposed new slot) | Currently missing entirely |
| Structured output steering | Response schema / `<answer>` tags | Currently not enforced |
