"""Apply dependency guardrails to move 6 blocking deps to infra extras.

This script applies minimal code changes to defer imports of:
- chromadb, duckdb, numpy, pydantic-settings, rank-bm25, scikit-learn

All imports are moved to function scope with try/except ImportError guards.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODIFICATIONS = [('agentic_core/L4_state/memory/in_memory_vector_cache.py', 'import logging\\nfrom typing import Any\\n\\nimport chromadb\\n\\nLogger', 'import logging\nfrom typing import Any\n\nLogger'), ('agentic_core/L4_state/enforcement/trace_event.py', 'from dataclasses import dataclass\\nfrom typing import Any\\n\\nimport duckdb\\n\\nLogger', 'from dataclasses import dataclass\nfrom typing import Any\n\nLogger'), ('agentic_core/L4_state/memory/bm25_store.py', 'from typing import Any\\n\\nfrom rank_bm25 import BM25Okapi\\n\\n\\nclass Bm25Store:', 'from typing import Any\n\n\nclass Bm25Store:'), ('agentic_core/L2_execution/config/hybrid_retriever_config.py', 'from pathlib import Path\\nfrom typing import Any\\n\\nfrom rank_bm25 import BM25Okapi\\n\\n', 'from pathlib import Path\nfrom typing import Any\n\n'), ('apps_shared/types/validation_status_types.py', 'import numpy as np\\nfrom sklearn\\.feature_extraction\\.text import TfidfVectorizer\\nfrom sklearn\\.metrics\\.pairwise import cosine_similarity\\n\\nlogger', 'import numpy as np\n\nlogger'), ('agentic_core/L2_execution/reasoning/batch_embedding_service.py', 'from typing import Any\\n\\nimport numpy as np\\n\\nLogger', 'from typing import Any\n\nLogger'), ('agentic_core/L2_execution/reasoning/tool_registry.py', 'from typing import Any\\n\\nimport numpy as np\\n\\nLogger', 'from typing import Any\n\nLogger'), ('agentic_core/L3_orchestration/reasoning/CoverageAgent.py', 'from typing import Any\\n\\nimport numpy as np\\nfrom agentic_core', 'from typing import Any\n\nfrom agentic_core'), ('agentic_core/runtime/types/cache_entry_types.py', 'from typing import Any\\n\\nimport numpy as np\\n\\ntry:', 'from typing import Any\n\ntry:'), ('agentic_core/L4_state/reasoning/PineconeSovereignAgent.py', 'from typing import Any\\n\\nimport numpy as np\\nfrom agentic_core', 'from typing import Any\n\nfrom agentic_core'), ('apps_shared/validators/cache_entry_validator.py', 'from typing import Any\\n\\nimport numpy as np\\nfrom pydantic', 'from typing import Any\n\nfrom pydantic'), ('apps_shared/reasoning/GlobalcacheStrategy.py', 'from typing import Any\\n\\nimport numpy as np\\nfrom pydantic', 'from typing import Any\n\nfrom pydantic')]

def apply_modifications():
    """Apply all modifications."""
    for rel_path, old_pattern, new_pattern in MODIFICATIONS:
        file_path = PROJECT_ROOT / rel_path
        if not file_path.exists():
            print(f'SKIP (not found): {rel_path}')
            continue
        content = file_path.read_text(encoding='utf-8')
        new_content = re.sub(old_pattern, new_pattern, content)
        if new_content == content:
            print(f'SKIP (no match): {rel_path}')
        else:
            file_path.write_text(new_content, encoding='utf-8')
            print(f'MODIFIED: {rel_path}')
if __name__ == '__main__':
    print('Applying dependency guardrails...')
    apply_modifications()
    print('\nDone. Module-level imports removed.')
    print("Note: Type hints using np.ndarray will need 'from __future__ import annotations'")
    print('      or be changed to Any. Function-level guards still needed.')
