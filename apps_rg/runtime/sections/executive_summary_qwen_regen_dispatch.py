"""Compat shim (ADR-082) — module renamed to ``executive_summary_regen_dispatch``.

The Qwen/vLLM provider was removed (PR #256); this dispatcher was always
provider-neutral (``generate_section`` → ``ProviderGateway``), so the module and its
public symbols dropped the misleading ``qwen`` naming
(plan apps-rg-aig-remaining-lanes-closeout-d4e1f7 qwen-rename sweep).
Import from ``apps_rg.runtime.sections.executive_summary_regen_dispatch`` instead.
Sunset: delete after one release with zero importers.
"""

from __future__ import annotations

import warnings

from apps_rg.runtime.sections.executive_summary_regen_dispatch import *  # noqa: F401,F403
from apps_rg.runtime.sections.executive_summary_regen_dispatch import (  # noqa: F401
    BudgetedQwenRegenOutcome,
    BudgetedRegenOutcome,
    budgeted_qwen_regen_call,
    budgeted_regen_call,
)

warnings.warn(
    "apps_rg.runtime.sections.executive_summary_qwen_regen_dispatch is deprecated; "
    "import apps_rg.runtime.sections.executive_summary_regen_dispatch (ADR-082 shim).",
    DeprecationWarning,
    stacklevel=2,
)
