from __future__ import annotations
"""
Cryptographic Provenance Utilities

Cluster: GPG signing and Git commit operations (Protocol 9)
Lines: 337-380 from core_utils.py
"""
import logging
import subprocess
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger('CanonValidator')

def setup_gpg_signing(key_id: str) -> Any:
    """
    Configures Git to use a specific GPG key for signing commits.
    In a production container, this GPG key must be pre-loaded and trusted.
    """
    try:
        subprocess.run(['git', 'config', '--global', 'gpg.program', 'gpg'], check=True, capture_output=True)
        subprocess.run(['git', 'config', '--global', 'user.signingkey', key_id], check=True, capture_output=True)
        Logger.info(f'[OK] Git configured for signing with key: {key_id}')
    except subprocess.CalledProcessError as e:
        Logger.error(f'[X] Failed to configure Git signing: {e.stderr.decode()}')
        raise RuntimeError('Git GPG configuration failed.')

def sign_and_commit(path: str, message: str, key_id: str=None) -> bool:
    """
    Executes a commit with the -S (signoff/sign) flag.
    For demo purposes, skips actual GPG signing and commits normally.
    """
    try:
        subprocess.run(['git', 'add', path], check=True, capture_output=True)
        result: Any = subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True, text=True)
        Logger.info(f'[OK] Commit successful (demo mode - no GPG signing): {result.stdout.strip()}')
        return True
    except subprocess.CalledProcessError as e:
        Logger.error(f'[X] Commit failed (Git Error): {e.stderr}')
        return False
