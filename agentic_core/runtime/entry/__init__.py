"""Runtime entry adapters (U1 chat, U2 HTTP, U3 batch, U4 webhook).

Every U0 request source MUST route through one of these adapters so the
ingress envelope gate cannot be bypassed. See
``docs/reference/01_Request_Intake/01_request_intake.md``.
"""

from agentic_core.runtime.entry.batch_adapter import BatchIngressAdapter
from agentic_core.runtime.entry.chat_adapter import ChatIngressAdapter
from agentic_core.runtime.entry.http_adapter import HttpIngressAdapter
from agentic_core.runtime.entry.webhook_adapter import WebhookIngressAdapter

__all__ = [
    "BatchIngressAdapter",
    "ChatIngressAdapter",
    "HttpIngressAdapter",
    "WebhookIngressAdapter",
]
