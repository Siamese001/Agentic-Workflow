"""C7 G4: BUILD ACCESS TICKET - Generate capability_token and sandbox_envelope.

10C-REQ-158: Generate capability_token sandbox_envelope bounded scope expiration timeout
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccessTicket:
    """Access ticket with capability token and sandbox envelope.

    10C-REQ-158: capability_token, sandbox_envelope, bounded scope, expiration, timeout.
    """
    capability_token: str
    sandbox_envelope: str
    scope: list[str]
    expiration: float
    timeout_seconds: int
    actor_id: str
    issued_at: float

    def is_expired(self) -> bool:
        """Check if ticket is expired."""
        return time.time() > self.expiration

    def is_valid_for(self, operation: str) -> bool:
        """Check if ticket is valid for operation."""
        if self.is_expired():
            return False

        # Check if operation is in scope
        for scope_pattern in self.scope:
            if operation.startswith(scope_pattern) or scope_pattern == "*":
                return True
        return False


class TicketBuilder:
    """C7 G4: Access ticket builder.

    10C-REQ-158: Build access tickets with bounded scope and expiration.
    """

    DEFAULT_TIMEOUT = 300  # 5 minutes
    DEFAULT_SCOPE = ["read", "execute"]

    def __init__(self, master_secret: str | None = None) -> None:
        self._master_secret = master_secret or secrets.token_hex(32)
        self._issued_tickets: dict[str, AccessTicket] = {}

    def build(
        self,
        actor_id: str,
        scope: list[str] | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT,
    ) -> AccessTicket:
        """Build access ticket for actor."""
        scope = scope or self.DEFAULT_SCOPE
        issued_at = time.time()
        expiration = issued_at + timeout_seconds

        # Generate capability token
        token_data = f"{actor_id}:{':'.join(scope)}:{issued_at}:{self._master_secret}"
        capability_token = hashlib.sha256(token_data.encode()).hexdigest()[:32]

        # Build sandbox envelope
        envelope_data = {
            "actor": actor_id,
            "scope": scope,
            "issued": issued_at,
            "expires": expiration,
            "timeout": timeout_seconds,
        }
        envelope_raw = json.dumps(envelope_data, sort_keys=True)
        sandbox_envelope = hashlib.sha256(envelope_raw.encode()).hexdigest()[:32]

        ticket = AccessTicket(
            capability_token=capability_token,
            sandbox_envelope=sandbox_envelope,
            scope=scope,
            expiration=expiration,
            timeout_seconds=timeout_seconds,
            actor_id=actor_id,
            issued_at=issued_at,
        )

        self._issued_tickets[capability_token] = ticket
        return ticket

    def verify(self, capability_token: str) -> AccessTicket | None:
        """Verify and return ticket if valid."""
        ticket = self._issued_tickets.get(capability_token)
        if not ticket:
            return None

        if ticket.is_expired():
            return None

        return ticket

    def revoke(self, capability_token: str) -> bool:
        """Revoke a ticket."""
        if capability_token in self._issued_tickets:
            del self._issued_tickets[capability_token]
            return True
        return False

    def get_active_tickets(self) -> list[AccessTicket]:
        """Get all non-expired tickets."""
        current_time = time.time()
        return [
            t for t in self._issued_tickets.values()
            if t.expiration > current_time
        ]
