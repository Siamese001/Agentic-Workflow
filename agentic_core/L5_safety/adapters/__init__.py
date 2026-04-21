"""L5 human approval adapters for runtime HITL exit-control.

Per ADR-023 §3.3, ``HumanApprovalAdapter`` is the abstract base; each approval
surface (Notion, Slack, Orkes, email magic link, etc.) implements it.

Scope: RUNTIME HITL (v30 step [5]). NOT developer-loop Author-Gate.
"""

from agentic_core.L5_safety.adapters.human_approval_adapter import (
    AdapterError,
    ApprovalHandle,
    ApprovalOutcome,
    ApprovalOutcomeKind,
    HumanApprovalAdapter,
)
from agentic_core.L5_safety.adapters.email_magic_link_adapter import (
    EmailMagicLinkAdapter,
    EmailTransport,
    MagicLinkStore,
    StoredOutcome,
)
from agentic_core.L5_safety.adapters.notion_approval_adapter import (
    NotionApprovalAdapter,
    NotionTransport,
)
from agentic_core.L5_safety.adapters.orkes_approval_adapter import (
    OrkesApprovalAdapter,
    OrkesTransport,
)
from agentic_core.L5_safety.adapters.slack_approval_adapter import (
    SlackApprovalAdapter,
    SlackTransport,
)

__all__ = [
    "AdapterError",
    "ApprovalHandle",
    "ApprovalOutcome",
    "ApprovalOutcomeKind",
    "EmailMagicLinkAdapter",
    "EmailTransport",
    "HumanApprovalAdapter",
    "MagicLinkStore",
    "NotionApprovalAdapter",
    "NotionTransport",
    "OrkesApprovalAdapter",
    "OrkesTransport",
    "SlackApprovalAdapter",
    "SlackTransport",
    "StoredOutcome",
]
