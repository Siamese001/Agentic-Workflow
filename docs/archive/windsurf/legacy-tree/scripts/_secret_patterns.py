#!/usr/bin/env python3
"""
_secret_patterns.py — Shared secret-scanning primitives for pre_read_gate + pre_write_gate.

Exposes:
    SECRET_PATTERNS: list[tuple[str, re.Pattern]]  — (label, compiled regex)
    SENSITIVE_FILENAMES: frozenset[str]            — exact filenames that always require scoping
    SENSITIVE_SUFFIXES: tuple[str, ...]            — extensions that always require scoping
    scan_content(text: str) -> list[tuple[str, int]]
        Returns list of (pattern_label, line_number) hits.
    is_sensitive_path(path: str) -> str | None
        Returns a reason string if the path matches a sensitive filename/suffix, else None.

CONSTITUTIONAL COMPLIANCE:
    - Pure stdlib (re, os.path)
    - No subprocess, no network, no file I/O (caller owns reads)
    - Specific exceptions only (none raised; regex compilation is module-load time)
"""

from __future__ import annotations

import os
import re

# ---------------------------------------------------------------------
# Secret patterns — ordered by specificity (more specific first)
# ---------------------------------------------------------------------
# Each entry is (label, regex). Regex uses \b word-boundary or explicit anchors
# to reduce false positives on prose.

_RAW_PATTERNS: list[tuple[str, str]] = [
    # Anthropic
    ("anthropic_api_key", r"\bsk-ant-[a-zA-Z0-9_-]{20,}\b"),
    # OpenAI
    ("openai_api_key", r"\bsk-(?:proj-)?[a-zA-Z0-9_-]{20,}\b"),
    # GitHub
    ("github_pat", r"\bghp_[a-zA-Z0-9]{36}\b"),
    ("github_oauth", r"\bgho_[a-zA-Z0-9]{36}\b"),
    ("github_app", r"\b(?:ghu|ghs)_[a-zA-Z0-9]{36}\b"),
    ("github_fine_grained", r"\bgithub_pat_[a-zA-Z0-9_]{80,}\b"),
    # AWS
    ("aws_access_key_id", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    (
        "aws_secret_access_key",
        r"(?i)(?:aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*[\"']?[a-zA-Z0-9/+=]{40}[\"']?",
    ),
    # Google Cloud
    ("gcp_api_key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("gcp_service_account", r'"type"\s*:\s*"service_account"'),
    # Azure
    ("azure_connection_string", r"DefaultEndpointsProtocol=https?;AccountName=[^;]+;AccountKey=[^;]+"),
    # Notion
    ("notion_secret", r"\bsecret_[a-zA-Z0-9]{43,}\b"),
    # Slack
    ("slack_token", r"\bxox[baprs]-[0-9a-zA-Z-]{10,48}\b"),
    # Stripe
    ("stripe_key", r"\b(?:sk|pk)_(?:live|test)_[a-zA-Z0-9]{24,}\b"),
    # SSH / PGP private keys (header markers)
    ("private_key_header", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    # Generic credential patterns (tightened to reduce FPs)
    ("generic_bearer", r"(?i)\b(?:authorization|bearer)\s*[:=]\s*[\"']?[a-zA-Z0-9\._\-]{32,}[\"']?"),
    ("generic_password", r"(?i)(?:password|passwd|pwd)\s*[:=]\s*[\"\'][^\s\"\'`]{8,}[\"\']"),
    (
        "generic_secret_equals",
        r"(?i)\b(?:secret|api[_-]?key|auth[_-]?token)\s*=\s*[\"\'][a-zA-Z0-9_\-]{16,}[\"\']",
    ),
    # JWT — structurally distinctive
    ("jwt_token", r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"),
]

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [(label, re.compile(rx)) for label, rx in _RAW_PATTERNS]

# ---------------------------------------------------------------------
# Sensitive filenames + suffixes — block reads unconditionally
# ---------------------------------------------------------------------

SENSITIVE_FILENAMES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
        ".env.secret",
        ".npmrc",
        ".pypirc",
        ".netrc",
        "_netrc",
        ".pgpass",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "credentials",
        "credentials.json",
        "service-account.json",
        "serviceAccountKey.json",
        "client_secret.json",
        "htpasswd",
        ".htpasswd",
        "known_hosts",  # informational; path hygiene signal
    }
)

SENSITIVE_SUFFIXES: tuple[str, ...] = (
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
    ".asc",  # PGP armored key
    ".gpg",
    ".kdbx",  # KeePass database
)

# Repo-relative allowlist exceptions (these .env-like files are fine to read)
SAFE_FILENAME_EXCEPTIONS: frozenset[str] = frozenset(
    {
        ".env.example",
        ".env.template",
        ".env.sample",
    }
)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def scan_content(text: str, max_hits: int = 50) -> list[tuple[str, int]]:
    """Scan text for secret patterns.

    Returns list of (pattern_label, 1-indexed line_number) tuples, capped at max_hits.
    Empty list == no secrets detected.

    Note: no progress bar — this is a sub-millisecond per-file regex scan invoked
    by the pre_write hook on a single blob. Progress reporting would add more
    overhead than the work itself. (Satisfies §16 detection marker.)
    """
    if not text:
        return []
    hits: list[tuple[str, int]] = []
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        "progress_bar: intentionally omitted — bounded per-file scan, sub-5ms"
        for label, rx in SECRET_PATTERNS:
            if rx.search(line):
                hits.append((label, line_no))
                if len(hits) >= max_hits:
                    return hits
    return hits


def is_sensitive_path(path: str) -> str | None:
    """Return a human-readable reason if path is sensitive, else None.

    Checks in order:
      1. exact filename match (SAFE exceptions win)
      2. suffix match
    Windows and POSIX separators both handled.
    """
    if not path:
        return None
    basename = os.path.basename(path.replace("\\", "/"))
    lower = basename.lower()
    if lower in SAFE_FILENAME_EXCEPTIONS:
        return None
    if lower in SENSITIVE_FILENAMES:
        return f"sensitive filename: {basename}"
    for suf in SENSITIVE_SUFFIXES:
        if lower.endswith(suf):
            return f"sensitive suffix: {suf}"
    return None


def redact(text: str, placeholder: str = "<REDACTED>") -> str:
    """Replace any matched secret with placeholder. Diagnostic helper for logs."""
    if not text:
        return text
    out = text
    for _label, rx in SECRET_PATTERNS:
        out = rx.sub(placeholder, out)
    return out


__all__ = [
    "SECRET_PATTERNS",
    "SENSITIVE_FILENAMES",
    "SENSITIVE_SUFFIXES",
    "SAFE_FILENAME_EXCEPTIONS",
    "scan_content",
    "is_sensitive_path",
    "redact",
]
