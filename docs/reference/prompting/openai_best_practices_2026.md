# OpenAI — Prompting Best Practices (distilled, 2026-04)

Sources (retrieved 2026-04-23):
- GPT-4.1 Prompting Guide: <https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide>
- Reasoning best practices (o1/o3/o-series): <https://developers.openai.com/api/docs/guides/reasoning-best-practices>

This is a distillation for internal cross-mapping against the agentic_core prompt
assembler. Re-fetch before major prompt-engineering work.

---

## 1. Instruction hierarchy (model spec)

OpenAI's chain of command:
1. **Developer** messages (highest — new in o1-2024-12-17; replaces `system` for reasoning models)
2. **System** messages (still used for GPT-4.1)
3. **User** messages
4. **Tool / function** messages

GPT-4.1 and o-series are trained to honour this hierarchy. If D0-style policy
fences need to *outrank* I0 capability text, they must live in the
developer/system slot, not in user content.

---

## 2. Prompt structure (GPT-4.1 recommended skeleton)

```
# Role and Objective
# Instructions
## Sub-categories for more detailed instructions
# Reasoning Steps
# Output Format
# Examples
## Example 1
# Context
# Final instructions and prompt to think step by step
```

Delete sections that don't apply; reorder only with care.

---

## 3. Delimiters

Ranked by performance (OpenAI internal testing):

1. **Markdown headings** (#, ##, ###) — start here.
2. **XML tags** — improved adherence in GPT-4.1. Best for nested examples:
   ```xml
   <examples>
     <example1 type="Abbreviate">
       <input>San Francisco</input>
       <output>SF</output>
     </example1>
   </examples>
   ```
3. **JSON** — strong in code contexts but verbose; poor in long-context RAG (escaping overhead).

For **RAG / many documents**, XML wins:
- Good: `<doc id='1' title='The Fox'>...</doc>`
- Good: `ID: 1 | TITLE: The Fox | CONTENT: ...`
- Poor: `[{"id": 1, ...}]` (JSON)

---

## 4. GPT-4.1 instruction following

### 4.1 Literal interpretation
- GPT-4.1 follows instructions more literally than GPT-4o.
- A single sentence firmly clarifying desired behaviour is usually enough.

### 4.2 Recommended workflow
1. Start with high-level `# Instructions` / `# Response Rules`.
2. Add sub-sections (`## Sample Phrases`) for specific behaviours.
3. Use ordered lists for required step sequences.
4. If behaviour is still wrong:
   - Check for **conflicting** or underspecified instructions — GPT-4.1 follows
     the one **closer to the end** when they conflict.
   - Add demonstrating examples; ensure rules cited in examples also appear
     in the explicit rule list.
   - **Avoid** all-caps, bribes, tips — they can cause over-triggering.

### 4.3 Common failure modes
- "You MUST call a tool before responding" → tool hallucinations with null args.
  Add "if you don't have enough info, ask the user" to mitigate.
- Sample phrases used verbatim → repetitive output. Instruct variation.
- Unsolicited explanation prose → give an explicit output format rule.

---

## 5. Long context (up to 1M tokens on GPT-4.1)

### 5.1 Context reliance tuning
- Internal-knowledge-only:
  > "Only use the documents in the provided External Context to answer the
  > User Query. If you don't know the answer based on this context, respond
  > 'I don't have the information needed to answer that'."
- Mixed:
  > "By default, use the provided external context, but use your own knowledge
  > if needed and you're confident."

### 5.2 Prompt organisation for long context
- Place instructions at **both the beginning AND end** of the provided context
  (outperforms either-only in OpenAI's tests).
- If only once, above > below.

---

## 6. Chain of Thought (GPT-4.1 — non-reasoning model)

GPT-4.1 is not a reasoning model, but benefits from explicit CoT for complex tasks.

**Basic trigger** (end of prompt):
> "First, think carefully step by step about what documents are needed to
> answer the query. Then, print out the TITLE and ID of each document. Then,
> format the IDs into a list."

**Structured reasoning strategy** (when basic CoT drifts):
```
# Reasoning Strategy
1. Query Analysis: ...
2. Context Analysis: ...
   a. Analysis: ...
   b. Relevance rating: [high, medium, low, none]
3. Synthesis: ...
```

Audit failure modes (intent misunderstanding, insufficient context gathering,
weak step-by-step logic) and codify fixes into explicit `# Reasoning Strategy`
sub-steps.

---

## 7. Reasoning models (o1, o3, o-series) — DIFFERENT rules

### 7.1 Developer messages replace system messages
Starting with `o1-2024-12-17`, reasoning models use **developer** role, not system.

### 7.2 Prompting principles INVERTED from GPT-4.1
- **Keep prompts simple and direct** — brief, clear instructions.
- **Avoid CoT prompts** — reasoning happens internally. "Think step by step" can *hurt* performance.
- **Zero-shot first, few-shot only if needed** — examples often unnecessary and risk conflicting with instructions.
- **Use delimiters** for clarity (markdown, XML, section titles).
- **Be very specific about the end goal** — give testable success criteria.
- **Explicit constraints** — "under $500", "JSON only", etc.
- **Markdown disabled by default** on `o1-2024-12-17+` — add `Formatting re-enabled` on the first line of the developer message to enable it.

### 7.3 When to use reasoning vs GPT models
Reasoning models excel at:
- Ambiguous tasks
- Needle-in-haystack retrieval
- Finding relationships in large datasets
- Multi-step agentic planning
- Visual reasoning
- Code review / debugging
- Benchmark / evaluator roles

GPT models (GPT-4.1) remain better for: high-throughput, latency-sensitive,
explicit workflows, cost-sensitive paths.

---

## 8. Agentic workflows (GPT-4.1)

### 8.1 System prompt reminders
- Persistence: "You are an agent; please keep going until the query is fully
  resolved, before ending your turn."
- Tool-calling: "If you're not sure, read files or ask — do not guess."
- Planning: induce planning explicitly if reliability matters — improves
  SWE-bench scores in OpenAI's tests.

### 8.2 Tool calls
- Use the `tools` API field, NOT stuffed into prompt text.
- Give clear names, descriptions, arg schemas.
- For complex tools, add an `# Examples` section in the system prompt showing
  how and when they should be invoked.

---

## Cross-map crib sheet (for this repo's assembler)

| OpenAI concept | Map to assembler slot | Notes |
|---|---|---|
| Developer role (reasoning) | D0 / S0 | We currently lump both into system; need provider-aware routing |
| System role (GPT-4.1) | S0 | OK |
| `# Instructions` | I0 | OK but currently plain-text joined |
| `# Reasoning Steps` / `# Reasoning Strategy` | M0 (proposed new slot) | Missing |
| `# Examples` with `<example>` XML | E0 (proposed new slot) | Currently mixed into I0 |
| `# Context` / RAG docs | C0 | Must use `<doc id='...' title='...'>` wrapping |
| `# Output Format` | Structured-output binding | Currently not enforced |
| User query | U0 | OK |
| Tools schema | `allowed_tools_schema` on artifact | Already plumbed |
| Instruction-at-top-AND-bottom (long context) | Assembler-level feature | Missing |
