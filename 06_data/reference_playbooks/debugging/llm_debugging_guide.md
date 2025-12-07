# LLM Debugging Guide

## Common Issues and Solutions

### 1. Inconsistent Outputs

**Symptoms**: Same prompt produces different results

**Diagnosis**:
```python
# Test consistency
results = []
for _ in range(10):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,  # Deterministic
        seed=42,        # Fixed seed
    )
    results.append(response.choices[0].message.content)

# Check variance
unique_results = set(results)
print(f"Unique outputs: {len(unique_results)}/{len(results)}")
```

**Solutions**:
- Set `temperature=0` for deterministic outputs
- Use `seed` parameter for reproducibility
- Add explicit formatting instructions

---

### 2. Hallucinations

**Symptoms**: Model generates false information

**Diagnosis**:
```python
# Add citation requirements
system_prompt = """
You must cite sources for factual claims.
If you're uncertain, say "I'm not sure about this."
Never make up information.
"""

# Enable retrieval augmentation
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ],
)
```

**Solutions**:
- Use RAG for factual queries
- Add uncertainty acknowledgment instructions
- Implement fact-checking pipeline

---

### 3. Context Window Overflow

**Symptoms**: Model ignores early context, truncated responses

**Diagnosis**:
```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")
tokens = enc.encode(full_prompt)
print(f"Token count: {len(tokens)}")
print(f"Context limit: 128000")
print(f"Remaining: {128000 - len(tokens)}")
```

**Solutions**:
- Summarize long contexts
- Use chunking strategies
- Prioritize recent/relevant context

---

### 4. Tool Calling Failures

**Symptoms**: Model doesn't call tools or calls wrong tools

**Diagnosis**:
```python
# Verbose tool descriptions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location. "
                          "Use this when the user asks about weather, "
                          "temperature, or climate conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., 'Tokyo' or 'New York'"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

**Solutions**:
- Improve tool descriptions
- Add usage examples in descriptions
- Use `tool_choice` to force specific tools

---

### 5. Safety Over-Refusals

**Symptoms**: Model refuses benign requests

**Diagnosis**:
```python
# Test with explicit context
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant for a chemistry "
                   "education platform. Users are verified students."
    },
    {
        "role": "user",
        "content": "Explain the chemical reaction in baking soda and vinegar"
    }
]
```

**Solutions**:
- Provide appropriate context
- Use system prompts to establish legitimate use cases
- Report false positives to improve models

---

## Debugging Checklist

- [ ] Check token count vs context limit
- [ ] Verify temperature and seed settings
- [ ] Review system prompt clarity
- [ ] Test tool descriptions
- [ ] Examine conversation history
- [ ] Check for rate limiting
- [ ] Verify API key permissions
- [ ] Review error messages carefully
