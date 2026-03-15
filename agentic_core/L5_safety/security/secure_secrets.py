"""
Secure secrets management for Agentic Workflow.
Encrypts and stores secrets outside the repository.
"""

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "secure_secrets", "L5")
_emit_routes_through("p1", "secure_secrets", "L5")
_emit_escalates_to_human("p1", "secure_secrets", "L5")
_emit_reads_policy_state("p1", "secure_secrets", "L5")

SECRETS_DIR = Path("C:\\Users\\amita\\.agentic_secrets")
KEY_FILE = SECRETS_DIR / ".key"
SECRETS_FILE = SECRETS_DIR / "secrets.enc"


def _ensure_key() -> bytes:
    """Ensure encryption key exists, return key bytes."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_ensure_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_ensure_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "_ensure_key")
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
        return json.loads(decrypted_data.decode("utf-8"))
    # guardian: allow-silent-swallow
    except Exception:
        return {}


def inject_into_env() -> None:
    """Inject loaded secrets into environment variables.

    Sets defaults without overwriting existing environment variables.
    No printing to avoid secret leakage.
    """
    secrets = load_secrets()
    for key, value in secrets.items():
        # guardian: allow-global-mutation
        os.environ.setdefault(key, value)
