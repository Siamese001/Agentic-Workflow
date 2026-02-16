# Phase 7 — Model ID Propagation to LLM Call Seam Evidence

## Wave 7.1 — Heal LLM Call Seam Types (Stdlib Only)

### File Created

`agentic_core/L5_safety/types/heal_llm_seam.py`

### Contents

```python
"""Heal LLM call seam types for heal policy integrations.

Pure type definitions only (stdlib-only, no environment access or SDK imports).
Phase 7 Wave 7.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class HealLlmRequest:
    """Typed request payload for heal LLM calls.

    Attributes:
        prompt: The prompt text to send to the LLM.
        model_id: Optional model identifier; None means use the default model.
        metadata: Arbitrary metadata for observability/instrumentation.
    """

    prompt: str
    model_id: str | None
    metadata: dict[str, Any]


HealLlmCaller = Callable[[HealLlmRequest], str]


# Default LLM caller seam for heal flows (not wired by default).
DEFAULT_HEAL_LLM_CALLER: HealLlmCaller | None = None
```

### python -c sanity check

```bash
python -c "from agentic_core.L5_safety.types.heal_llm_seam import HealLlmRequest; print('ok')"
```

```text
ok
```

### pytest -q

```text
===================== 142 passed in 20.33s =====================
```

Exit code: 0

**WAVE 7.1 ACCEPTANCE**: All tests pass. Heal LLM call seam types added (stdlib-only, no SDK/import side effects).
