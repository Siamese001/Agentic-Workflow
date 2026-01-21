from __future__ import annotations

"""
Cryptographic Provenance Utilities

Cluster: GPG signing and Git commit operations (Protocol 9)
Lines: 337-380 from core_utils.py
"""
import logging
import subprocess
from typing import Any

from agentic_core.utils.security import safe_execute

Logger: Any = logging.getLogger('CanonValidator')

def setup_gpg_signing(key_id: str) -> Any:
    """
    Configures Git to use a specific GPG key for signing commits.
    In a production container, this GPG key must be pre-loaded and trusted.
    """
    try:
        safe_execute(['git', 'config', '--global', 'gpg.program', 'gpg'], check=True, capture_output=True)
        safe_execute(['git', 'config', '--global', 'user.signingkey', key_id], check=True, capture_output=True)
        Logger.info(f'[OK] Git configured for signing with key: {key_id}')
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if hasattr(e.stderr, 'decode') else str(e.stderr)
        Logger.error(f'[X] Failed to configure Git signing: {error_msg}')
        raise RuntimeError('Git GPG configuration failed.')

def sign_and_commit(path: str, message: str, key_id: str=None) -> bool:
    """
    Executes a commit with the -S (signoff/sign) flag.
    For demo purposes, skips actual GPG signing and commits normally.
    """
    try:
        safe_execute(['git', 'add', path], check=True, capture_output=True)
        result: Any = safe_execute(['git', 'commit', '-m', message], check=True, capture_output=True, text=True)
        Logger.info(f'[OK] Commit successful (demo mode - no GPG signing): {result.stdout.strip()}')
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if hasattr(e, 'stderr') else str(e)
        Logger.error(f'[X] Commit failed (Git Error): {error_msg}')
        return False
