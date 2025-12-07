# Few-Shot Reasoning Exemplars
# Purpose: High-quality examples for in-context learning
# Version: 3.0

## Mathematical Reasoning

### Example 1: Multi-step Problem
**User**: A store sells apples for $2 each and oranges for $3 each. If Sarah buys 5 apples and some oranges, spending exactly $19, how many oranges did she buy?

**Assistant**: Let me solve this step by step.

1. **Calculate apple cost**: 5 apples × $2 = $10
2. **Find remaining budget**: $19 - $10 = $9
3. **Calculate oranges**: $9 ÷ $3 = 3 oranges

**Answer**: Sarah bought 3 oranges.

---

## Logical Reasoning

### Example 2: Deductive Logic
**User**: All mammals are warm-blooded. All dogs are mammals. Is a golden retriever warm-blooded?

**Assistant**: Let me trace the logical chain:

1. **Premise 1**: All mammals are warm-blooded
2. **Premise 2**: All dogs are mammals
3. **Fact**: A golden retriever is a type of dog
4. **Deduction**: Golden retriever → Dog → Mammal → Warm-blooded

**Answer**: Yes, a golden retriever is warm-blooded.

---

## Code Reasoning

### Example 3: Bug Analysis
**User**: Why does this code print "None"?
```python
def add(a, b):
    result = a + b

print(add(2, 3))
```

**Assistant**: Let me analyze the code:

1. **Function definition**: `add(a, b)` calculates `a + b`
2. **Missing return**: The result is stored but never returned
3. **Default behavior**: Python functions return `None` by default
4. **Fix**: Add `return result` after the calculation

**Answer**: The function lacks a `return` statement. Add `return result` to fix it.

---

## Best Practices for Few-Shot Prompting

1. **Diversity**: Include varied example types
2. **Clarity**: Use clear formatting and structure
3. **Relevance**: Match examples to target task domain
4. **Progression**: Order from simple to complex
5. **Consistency**: Maintain uniform response format
