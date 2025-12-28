#!/usr/bin/env python3
"""
Networking Utilities for Agentic Workflow
Provides P8 Egress Filter for strict domain whitelisting
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class EgressResult:
    """Result from egress filter check."""
    status: str  # "PASS" or "FAIL"
    reason: str
    host: str


class NetworkingUtility:
    """Provides networking utilities with P8 Egress Filter enforcement."""

    def __init__(self, allowed_hosts: Optional[Set[str]] = None):
        """
        Initialize networking utility.

        Args:
            allowed_hosts: Set of whitelisted hosts/domains
        """
        self.allowed_hosts = allowed_hosts or set()
        self.blocked_count = 0
        self.allowed_count = 0

    def strict_egress_filter(self, url: str, allowed: Optional[Set[str]] = None) -> EgressResult:
        """
        Check if URL is allowed by egress filter.

        Args:
            url: URL to check
            allowed: Optional override for allowed hosts

        Returns:
            EgressResult with status and reason
        """
        try:
            parsed = urlparse(url)
            host = parsed.hostname or ""

            # Use provided allowed list or instance default
            allowed_list = allowed or self.allowed_hosts

            # Check direct host match
            if host in allowed_list:
                self.allowed_count += 1
                logger.info(f"P8_PASS: Host {host} is whitelisted")
                return EgressResult(status="PASS", reason="Host whitelisted", host=host)

            # Check subdomain matches
            for allowed_host in allowed_list:
                if host.endswith(f".{allowed_host}") or host == allowed_host:
                    self.allowed_count += 1
                    logger.info(f"P8_PASS: Host {host} matches whitelisted {allowed_host}")
                    return EgressResult(status="PASS", reason=f"Subdomain of {allowed_host}", host=host)

            # Block non-whitelisted hosts
            self.blocked_count += 1
            logger.warning(f"P8_BLOCK: Host {host} is not whitelisted")
            return EgressResult(status="FAIL", reason=f"Host {host} not in whitelist", host=host)

        except Exception as e:
            logger.error(f"P8_ERROR: Failed to parse URL {url}: {e}")
            return EgressResult(status="FAIL", reason=f"Parse error: {str(e)}", host="unknown")

    def send_email(self, to: str, subject: str, body: str,
                   send_time: Optional[str] = None, dry_run: bool = True) -> dict:
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
            logger.info(f"EMAIL_DRY_RUN: Would send to {to}")
            logger.debug(f"Subject: {subject}")
            logger.debug(f"Body preview: {body[:100]}...")
            return {
                "status": "dry_run_success",
                "to": to,
                "sent_at": send_time or "immediate"
            }

        # Real email sending would go here
        # For now, always use dry run for safety
        logger.warning("EMAIL_SEND: Real email sending not implemented, using dry run")
        return self.send_email(to, subject, body, send_time, dry_run=True)

    def fetch_url(self, url: str, headers: Optional[dict] = None) -> dict:
        """
        Fetch URL content with P8 enforcement.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Fetch result with content or error
        """
        # Check egress filter first
        egress_result = self.strict_egress_filter(url)

        if egress_result.status == "FAIL":
            return {
                "status": "blocked",
                "reason": egress_result.reason,
                "host": egress_result.host
            }

        # For safety, return mock content
        logger.info(f"FETCH_DRY_RUN: Would fetch {url}")
        return {
            "status": "mock_success",
            "url": url,
            "content": f"Mock content for {url}",
            "host": egress_result.host
        }

    def get_stats(self) -> dict:
        """Get egress filter statistics."""
        return {
            "allowed_count": self.allowed_count,
            "blocked_count": self.blocked_count,
            "whitelisted_hosts": list(self.allowed_hosts)
        }


# Default allowed hosts for outreach
OUTREACH_ALLOWED_HOSTS = {
    "linkedin.com",
    "crunchbase.com",
    "techcrunch.com",
    "venturebeat.com",
    "company-websites.com",  # Placeholder for actual company domains
    "api.email-service.com"  # Placeholder for email API
}


# Singleton instance
_networking_instance = None


def get_networking_utility(allowed_hosts: Optional[Set[str]] = None) -> NetworkingUtility:
    """Get singleton networking utility instance."""
    global _networking_instance
    if _networking_instance is None:
        _networking_instance = NetworkingUtility(
            allowed_hosts or OUTREACH_ALLOWED_HOSTS
        )
    return _networking_instance


def strict_egress_filter(url: str, allowed: Optional[Set[str]] = None) -> EgressResult:
    """Convenience function for egress filter check."""
    return get_networking_utility().strict_egress_filter(url, allowed)


def send_email(to: str, subject: str, body: str,
               send_time: Optional[str] = None, dry_run: bool = True) -> dict:
    """Convenience function for sending email."""
    return get_networking_utility().send_email(to, subject, body, send_time, dry_run)
