from __future__ import annotations

"""
Airlock Protocol - Zero Trust Human Authorization

Provides human-in-the-loop verification for high-risk actions.
Prevents autonomous execution of dangerous or irreversible operations.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path

LOGGER = logging.getLogger(__name__)

class AirlockProtocol:
    """
    Implements human authorization checkpoints for high-risk tool calls.

    When a risky action is requested, the agent pauses execution and
    waits for explicit human approval before proceeding.
    """

    def __init__(self,
                 risk_threshold: int = 5,
                 pending_dir: str = "./airlock/pending",
                 approved_dir: str = "./airlock/approved",
                 rejected_dir: str = "./airlock/rejected",
                 timeout_minutes: int = 30):
        """
        Initialize the airlock protocol.

        Args:
            risk_threshold: Minimum risk score requiring approval
            pending_dir: Directory for pending requests
            approved_dir: Directory for approved requests
            rejected_dir: Directory for rejected requests
            timeout_minutes: Maximum time to wait for approval
        """
        self.threshold = risk_threshold
        self.timeout = timedelta(minutes=timeout_minutes)

        # Create directories
        self.pending_dir = Path(pending_dir)
        self.approved_dir = Path(approved_dir)
        self.rejected_dir = Path(rejected_dir)

        for dir_path in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Risk registry for common tools
        self.risk_registry = {
            # File operations
            "write_file": 3,
            "delete_file": 6,
            "create_file": 3,
            "move_file": 4,

            # Git operations
            "git_push": 8,
            "git_commit": 5,
            "git_reset": 9,
            "git_force_push": 10,

            # System operations
            "run_command": 7,
            "execute_script": 8,
            "install_package": 6,

            # Network operations
            "send_email": 7,
            "api_call": 5,
            "webhook": 6,

            # Financial operations
            "transfer_funds": 10,
            "make_payment": 10,
            "purchase": 9,

            # Data operations
            "delete_database": 10,
            "modify_database": 7,
            "export_data": 6,
        }

        LOGGER.info(f"AirlockProtocol initialized with threshold={risk_threshold}")

    async def acquire_permission(self,
                                tool_name: str,
                                args: dict,
                                risk_score: int | None = None) -> bool:
        """
        Request Permission to execute a potentially dangerous action.

        Args:
            tool_name: Name of the tool being called
            args: Arguments passed to the tool
            risk_score: Optional override risk score

        Returns:
            True if approved, raises PermissionError if rejected or timeout

        Raises:
            PermissionError: If action is rejected or times out
            TimeoutError: If approval times out
        """
        # Determine risk score
        if risk_score is None:
            risk_score = self.risk_registry.get(tool_name, 5)

        # Auto-approve low-risk actions
        if risk_score < self.threshold:
            LOGGER.debug(f"Auto-approved low-risk action: {tool_name} (score={risk_score})")
            return True

        # High-risk action - create ticket
        ticket_id = str(uuid.uuid4())
        ticket = {
            "ticket_id": ticket_id,
            "tool_name": tool_name,
            "args": args,
            "risk_score": risk_score,
            "status": "PENDING_APPROVAL",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + self.timeout).isoformat(),
            "requester": "autonomous_agent"
        }

        # Write ticket to pending directory
        ticket_path = self.pending_dir / f"{ticket_id}.json"
        with open(ticket_path, "w") as f:
            json.dump(ticket, f, indent=2)

        LOGGER.warning("[!] HIGH RISK ACTION TRAPPED in AIRLOCK")
        LOGGER.warning(f"Ticket ID: {ticket_id}")
        LOGGER.warning(f"Action: {tool_name} with risk score {risk_score}")
        LOGGER.warning(f"Args: {json.dumps(args, indent=2)}")

        # Wait for human decision
        return await self._wait_for_approval(ticket_id, ticket_path)

    async def _wait_for_approval(self, ticket_id: str, ticket_path: Path) -> bool:
        """
        Wait for human approval of a pending ticket.

        Args:
            ticket_id: Unique ticket identifier
            ticket_path: Path to the ticket file

        Returns:
            True if approved

        Raises:
            PermissionError: If rejected
            TimeoutError: If times out
        """
        start_time = datetime.now()

        while True:
            # Check timeout
            if datetime.now() - start_time > self.timeout:
                # Move to rejected due to timeout
                self._move_ticket(ticket_path, self.rejected_dir, "TIMEOUT")
                raise TimeoutError(f"Airlock request timed out after {self.timeout}")

            # Check if ticket still exists in pending
            if not ticket_path.exists():
                # Ticket was moved - check where it went
                approved_path = self.approved_dir / f"{ticket_id}.json"
                rejected_path = self.rejected_dir / f"{ticket_id}.json"

                if approved_path.exists():
                    LOGGER.info(f"[OK] Airlock request {ticket_id} approved by human")
                    return True
                elif rejected_path.exists():
                    with open(rejected_path) as f:
                        data = json.load(f)
                    reason = data.get("reason", "No reason provided")
                    raise PermissionError(f"Human rejected action: {reason}")
                else:
                    # Ticket lost
                    raise PermissionError("Airlock request lost or corrupted")

            # Check ticket status directly
            try:
                with open(ticket_path) as f:
                    data = json.load(f)

                if data.get("status") == "APPROVED":
                    # Move to approved directory
                    self._move_ticket(ticket_path, self.approved_dir)
                    return True
                elif data.get("status") == "REJECTED":
                    reason = data.get("reason", "No reason provided")
                    # Move to rejected directory
                    self._move_ticket(ticket_path, self.rejected_dir, reason)
                    raise PermissionError(f"Human rejected action: {reason}")

            except (OSError, json.JSONDecodeError):
                # Ticket file may be corrupted or unreadable, continue waiting
                pass

            # Wait before next check
            await asyncio.sleep(5)

    def _move_ticket(self,
                    ticket_path: Path,
                    destination: Path,
                    reason: str | None = None):
        """
        Move ticket to destination directory with optional reason.

        Args:
            ticket_path: Current ticket location
            destination: Target directory
            reason: Optional rejection reason
        """
        try:
            with open(ticket_path) as f:
                data = json.load(f)

            if reason:
                data["reason"] = reason
                data["rejected_at"] = datetime.now().isoformat()
            elif destination == self.approved_dir:
                data["approved_at"] = datetime.now().isoformat()

            dest_path = destination / ticket_path.name
            with open(dest_path, "w") as f:
                json.dump(data, f, indent=2)

            ticket_path.unlink()

        except Exception as e:
            LOGGER.error(f"Error moving ticket: {e}")

    def get_pending_requests(self) -> list:
        """Get all pending airlock requests."""
        pending = []
        for ticket_file in self.pending_dir.glob("*.json"):
            try:
                with open(ticket_file) as f:
                    data = json.load(f)
                pending.append(data)
            except Exception:
                continue
        return pending

    def approve_request(self, ticket_id: str, approver: str = "human"):
        """
        Manually approve a pending request (for testing/CLI).

        Args:
            ticket_id: Ticket to approve
            approver: Who is approving
        """
        ticket_path = self.pending_dir / f"{ticket_id}.json"
        if ticket_path.exists():
            with open(ticket_path) as f:
                data = json.load(f)
            data["status"] = "APPROVED"
            data["approved_by"] = approver
            with open(ticket_path, "w") as f:
                json.dump(data, f, indent=2)
            LOGGER.info(f"Approved airlock request {ticket_id}")
        else:
            raise ValueError(f"Ticket {ticket_id} not found")

    def reject_request(self, ticket_id: str, reason: str = "Rejected by operator"):
        """
        Manually reject a pending request.

        Args:
            ticket_id: Ticket to reject
            reason: Reason for rejection
        """
        ticket_path = self.pending_dir / f"{ticket_id}.json"
        if ticket_path.exists():
            with open(ticket_path) as f:
                data = json.load(f)
            data["status"] = "REJECTED"
            data["reason"] = reason
            with open(ticket_path, "w") as f:
                json.dump(data, f, indent=2)
            LOGGER.info(f"Rejected airlock request {ticket_id}: {reason}")
        else:
            raise ValueError(f"Ticket {ticket_id} not found")

# Utility functions for CLI/web interface
def create_airlock_interface():
    """Create a simple CLI interface for managing airlock requests."""
    import argparse

    parser = argparse.ArgumentParser(description="Airlock Request Manager")
    parser.add_argument("action", choices=["list", "approve", "reject"])
    parser.add_argument("--ticket-id", help="Ticket ID to approve/reject")
    parser.add_argument("--reason", help="Reason for rejection")

    args = parser.parse_args()

    airlock = AirlockProtocol()

    if args.action == "list":
        pending = airlock.get_pending_requests()
        if pending:
            LOGGER.info("Pending Airlock Requests:")
            for req in pending:
                LOGGER.info(f"  {req['ticket_id']}: {req['tool_name']} (risk={req['risk_score']})")
        else:
            LOGGER.info("No pending requests")

    elif args.action == "approve":
        if not args.ticket_id:
            LOGGER.error("Error: --ticket-id required for approval")
            return
        airlock.approve_request(args.ticket_id)
        LOGGER.info(f"Approved ticket {args.ticket_id}")

    elif args.action == "reject":
        if not args.ticket_id:
            LOGGER.error("Error: --ticket-id required for rejection")
            return
        reason = args.reason or "Rejected via CLI"
        airlock.reject_request(args.ticket_id, reason)
        LOGGER.info(f"Rejected ticket {args.ticket_id}: {reason}")

if __name__ == "__main__":
    create_airlock_interface()
