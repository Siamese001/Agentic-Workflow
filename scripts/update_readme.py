#!/usr/bin/env python3
"""
Auto-update README.md when sovereign code changes.
Called by pre-commit hook - only stages README, does NOT commit (avoids recursion).
"""

import subprocess
import sys
from pathlib import Path

README_CONTENT = '''# Agentic-Workflow: Subatomic Canon 2025 — Eternal Agentic Architecture

[![40/40 Subatomic Perfection](https://img.shields.io/badge/40/40-PERFECT-ED1C24)](https://github.com/Siamese001/Agentic-Workflow) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)

## Overview

**Agentic-Workflow** is a production-hardened, subatomic agentic architecture for high-precision workflows (200–300 resumes/day). Built on OpenAI, Anthropic, and Google Gemini, it enforces **immutable separation of concerns** for cognition, execution, orchestration, memory, and safety.

**Core Philosophy (Subatomic Canon 2025):**

- **L1/L2/L3 Only in Code**: Pure logic in `agentic_core/` and `apps/`.
- **L4 Memory**: Long-term in `data/semantic_cache/` (immune); short-term in `agentic_core/memory/`.
- **L5 Safety**: Global in `prompt_governance/`; app-specific in `apps/*/safety/`.
- **40/40 Enforcement**: Sovereign code (8 folders) judged by 40 keys; non-sovereign by Light Canon (12 checks); `data/` & `archives/` immune.
- **Zero Loss**: All data versioned, manifested, reproducible.

This repo achieves **40/40 Subatomic Perfection** — code + data + safety — eternal.

## Architecture — Subatomic Layers

| Layer | Responsibility | Location | 40 Keys? |
|-------|----------------|----------|----------|
| **L1 Cognition** | Plan, score, decide, reason | `agentic_core/L1_cognition/` | YES |
| **L2 Execution** | Generate, tool call, structured output | `agentic_core/L2_execution/` | YES |
| **L3 Orchestration** | Route, retry, coordinate | `agentic_core/L3_orchestration/` | YES |
| **L4 Memory** | Long-term persisted vectors | `data/semantic_cache/` | NO (immune) |
| **L5 Safety** | Global guardrails | `prompt_governance/` | YES |

## Folder Structure

```text
Agentic-Workflow/
├── agentic_core/                 # Universal brain (L1-L3)
│   ├── L1_cognition/             # Plan, score, decide
│   ├── L2_execution/             # Generate, tool call
│   └── L3_orchestration/         # Route, retry, coordinate
├── apps_lic/                     # LIC workflow app
├── apps_rg/                      # RG workflow app
├── apps_shared/                  # Shared app logic
├── data/                         # Immutable truth (immune)
│   └── semantic_cache/           # Long-term L4 memory
├── prompt_governance/            # Global L5 safety (sovereign)
├── schemas/                      # Contracts (sovereign)
├── observability/                # Tracing (sovereign)
├── config/                       # Runtime truth (sovereign)
└── tests/, scripts/, archives/   # Non-sovereign
```

## Sovereign Folders (Full 40 Keys)

`agentic_core/`, `apps_lic/`, `apps_rg/`, `apps_shared/`, `schemas/`, `prompt_governance/`, `observability/`, `config/`

Everything else → Light Canon or immune.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Siamese001/Agentic-Workflow.git
cd Agentic-Workflow
pip install -r requirements.txt

# Validate 40/40 Canon
python canon_validator.py
```

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**40/40 — PURE — FINAL — ETERNAL**
'''


def main() -> int:
    """Update README.md and stage it."""
    root = Path(__file__).parent.parent
    readme_path = root / "README.md"
    
    # Check if sovereign code changed (already filtered by pre-commit files pattern)
    # Just update and stage README
    print("Sovereign code changed → updating README.md")
    
    readme_path.write_text(README_CONTENT, encoding="utf-8")
    
    # Stage README.md (do NOT commit - let the original commit include it)
    result = subprocess.run(
        ["git", "add", "README.md"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print(f"Failed to stage README.md: {result.stderr}", file=sys.stderr)
        return 1
    
    print("README.md updated and staged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
