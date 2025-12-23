"""
Cryptographic Provenance Utilities

Cluster: GPG signing and Git commit operations (Protocol 9)
Lines: 337-380 from core_utils.py
"""
from typing import Any, Optional, Protocol, Dict, List

import logging
import subprocess

logger = logging.getLogger("CanonValidator")


def setup_gpg_signing(key_id: str):
    """
    Configures Git to use a specific GPG key for signing commits.
    In a production container, this GPG key must be pre-loaded and trusted.
    """
    try:
        # 1. Tell Git the GPG program to use
        subprocess.run(["git", "config", "--global", "gpg.program", "gpg"], 
                      check=True, capture_output=True)
        # 2. Set the key ID for signing
        subprocess.run(["git", "config", "--global", "user.signingkey", key_id], 
                      check=True, capture_output=True)
        logger.info(f"[OK] Git configured for signing with key: {key_id}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[X] Failed to configure Git signing: {e.stderr.decode()}")
        raise RuntimeError("Git GPG configuration failed.")


def sign_and_commit(path: str, message: str, key_id: str = None) -> bool:
    """
    Executes a commit with the -S (signoff/sign) flag.
    For demo purposes, skips actual GPG signing and commits normally.
    """
    # Skip GPG setup for demo
    # setup_gpg_signing(key_id)

    try:
        # Add the file to stage
        subprocess.run(["git", "add", path], check=True, capture_output=True)

        # Commit without signing for demo (would use -S flag in production)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"[OK] Commit successful (demo mode - no GPG signing): {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"[X] Commit failed (Git Error): {e.stderr}")
        return False