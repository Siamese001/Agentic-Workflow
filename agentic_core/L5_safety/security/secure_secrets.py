"""
Secure secrets management for Agentic Workflow.
Encrypts and stores secrets outside the repository.
"""

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

SECRETS_DIR = Path(r"C:\Users\amita\.agentic_secrets")
KEY_FILE = SECRETS_DIR / ".key"
SECRETS_FILE = SECRETS_DIR / "secrets.enc"


def _ensure_key() -> bytes:
    """Ensure encryption key exists, return key bytes."""
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key


def load_secrets() -> dict[str, str]:
    """Load and decrypt secrets from encrypted store.

    Returns:
        Empty dict if files missing, otherwise decrypted secrets.
    """
    if not KEY_FILE.exists() or not SECRETS_FILE.exists():
        return {}

    try:
        key = _ensure_key()
        fernet = Fernet(key)
        encrypted_data = SECRETS_FILE.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode('utf-8'))
    except Exception:
        # Return empty dict on any error to prevent crashes
        return {}


def inject_into_env() -> None:
    """Inject loaded secrets into environment variables.

    Sets defaults without overwriting existing environment variables.
    No printing to avoid secret leakage.
    """
    secrets = load_secrets()
    for key, value in secrets.items():
        os.environ.setdefault(key, value)
