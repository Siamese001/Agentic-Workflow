# Deprecated Prompt Formats Archive

## Purpose

This archive contains deprecated prompt formats and patterns that are no longer
recommended for production use. Preserved for reference and migration support.

---

## Deprecated: Completion API Prompts (Pre-Chat Era)

**Deprecated Since**: 2023-Q2
**Reason**: Chat Completions API provides better control and safety

```python
# OLD - Do not use
response = openai.Completion.create(
    model="text-davinci-003",
    prompt="Translate to French: Hello world",
    max_tokens=100,
)

# NEW - Use this instead
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a translator."},
        {"role": "user", "content": "Translate to French: Hello world"},
    ],
)
```

---

## Deprecated: Unstructured System Prompts

**Deprecated Since**: 2024-Q1
**Reason**: Structured prompts improve reliability and safety

```python
# OLD - Vague instructions
system_prompt = "Be helpful and answer questions."

# NEW - Structured with clear boundaries
system_prompt = """
You are a customer support assistant for TechCorp.

## Capabilities
- Answer questions about our products
- Help with order status
- Provide troubleshooting steps

## Boundaries
- Do not discuss competitor products
- Do not make promises about refunds
- Escalate billing issues to human agents

## Response Format
- Keep responses under 200 words
- Use bullet points for lists
- Include relevant links when available
"""
```

---

## Deprecated: Manual JSON Extraction

**Deprecated Since**: 2024-Q2
**Reason**: JSON mode and structured outputs are more reliable

```python
# OLD - Unreliable parsing
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Return JSON with name and age"}],
)
# Manual parsing often failed

# NEW - Guaranteed JSON
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Extract name and age"}],
    response_format={"type": "json_object"},
)
```

---

## Migration Guide

For assistance migrating from deprecated patterns, see:
- `06_data/reference_playbooks/migrations/model_upgrade_playbook.md`
- `06_data/openai_best_practices/sdk_reference/`
