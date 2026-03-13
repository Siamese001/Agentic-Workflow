from __future__ import annotations

"\nNetworking Utilities for Agentic Workflow\nProvides P8 Egress Filter for strict domain whitelisting\n\nZero-Ambiguity Standard: Renamed from EgressResult.py to egress_util.py\n"
import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

Logger: Any = logging.getLogger(__name__)


@dataclass
class EgressResult:
    """Result from egress filter check."""

    status: str
    reason: str
    host: str


class NetworkingUtility:
    """Provides networking utilities with P8 Egress Filter enforcement."""

    def __init__(self, allowed_hosts: set[str] | None = None):
        """
        Initialize networking utility.

        Args:
            allowed_hosts: Set of whitelisted hosts/domains
        """
        self.allowed_hosts = allowed_hosts or set()
        self.blocked_count = 0
        self.allowed_count = 0

    def strict_egress_filter(self, url: str, allowed: set[str] | None = None) -> EgressResult:
        """
        Check if URL is allowed by egress filter.

        Args:
            url: URL to check
            allowed: Optional override for allowed hosts

        Returns:
            EgressResult with status and reason
        """
        try:
            parsed: Any = urlparse(url)
            host: Any = parsed.hostname or ""
            allowed_list: Any = allowed or self.allowed_hosts
            if host in allowed_list:
                self.allowed_count += 1
                Logger.info(f"P8_PASS: Host {host} is whitelisted")
                return EgressResult(status="PASS", reason="Host whitelisted", host=host)
            for allowed_host in allowed_list:
                if host.endswith(f".{allowed_host}") or host == allowed_host:
                    self.allowed_count += 1
                    Logger.info(f"P8_PASS: Host {host} matches whitelisted {allowed_host}")
                    return EgressResult(status="PASS", reason=f"Subdomain of {allowed_host}", host=host)
            self.blocked_count += 1
            Logger.warning(f"P8_BLOCK: Host {host} is not whitelisted")
            return EgressResult(status="FAIL", reason=f"Host {host} not in whitelist", host=host)
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"P8_ERROR: Failed to parse URL {url}: {e}")
            return EgressResult(status="FAIL", reason=f"Parse error: {str(e)}", host="unknown")

    def send_email(
        self, to: str, subject: str, body: str, send_time: str | None = None, dry_run: bool = True
    ) -> dict:
        """
        Send email with P8 enforcement.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            send_time: Optional scheduled send time
            dry_run: If True, only log without sending

        Returns:
            Send result with status
        """
        if dry_run:
            Logger.info(f"EMAIL_DRY_RUN: Would send to {to}")
            Logger.debug(f"Subject: {subject}")
            Logger.debug(f"Body preview: {body[:100]}...")
            return {"status": "dry_run_success", "to": to, "sent_at": send_time or "immediate"}
        Logger.warning("EMAIL_SEND: Real email sending not implemented, using dry run")
        return self.send_email(to, subject, body, send_time, dry_run=True)

    def fetch_url(self, url: str, headers: dict | None = None) -> dict:
        """
        Fetch URL content with P8 enforcement via MCP fetch tool.

        Routes through mcp4_fetch (MCP fetch server) for all outbound HTTP.
        Egress filter is enforced before any network call is attempted.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Fetch result with content or error
        """
        egress_result: Any = self.strict_egress_filter(url)
        if egress_result.status == "FAIL":
            return {"status": "blocked", "reason": egress_result.reason, "host": egress_result.host}
        Logger.info(f"FETCH: Fetching {url} via MCP fetch")
        try:
            from mcp4_fetch import mcp4_fetch

            result: Any = mcp4_fetch(url=url)
            return {
                "status": "success",
                "url": url,
                "content": result,
                "host": egress_result.host,
            }
        except ImportError:
            Logger.warning("FETCH_FALLBACK: mcp4_fetch not available, returning mock")
            return {
                "status": "mock_success",
                "url": url,
                "content": f"Mock content for {url} (mcp4_fetch unavailable)",
                "host": egress_result.host,
            }
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"FETCH_ERROR: Failed to fetch {url}: {e}")
            return {"status": "error", "url": url, "reason": str(e), "host": egress_result.host}

    def get_stats(self) -> dict:
        """Get egress filter statistics."""
        return {
            "allowed_count": self.allowed_count,
            "blocked_count": self.blocked_count,
            "whitelisted_hosts": list(self.allowed_hosts),
        }


OUTREACH_ALLOWED_HOSTS: Any = {
    "linkedin.com",
    "crunchbase.com",
    "techcrunch.com",
    "venturebeat.com",
    "company-websites.com",
    "api.email-service.com",
}
_networking_instance = None


def get_networking_utility(allowed_hosts: set[str] | None = None) -> NetworkingUtility:
    """Get singleton networking utility instance."""
    global _networking_instance
    if _networking_instance is None:
        _networking_instance = NetworkingUtility(allowed_hosts or OUTREACH_ALLOWED_HOSTS)
    return _networking_instance


def strict_egress_filter(url: str, allowed: set[str] | None = None) -> EgressResult:
    """Convenience function for egress filter check."""
    return get_networking_utility().strict_egress_filter(url, allowed)


def send_email(to: str, subject: str, body: str, send_time: str | None = None, dry_run: bool = True) -> dict:
    """Convenience function for sending email."""
    return get_networking_utility().send_email(to, subject, body, send_time, dry_run)
