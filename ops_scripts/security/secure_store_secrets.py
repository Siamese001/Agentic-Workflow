"""
One-way importer: migrate .env secrets to encrypted store.
Reads .env from repo root, encrypts to machine-local store.
"""
import json
from pathlib import Path

from cryptography.fernet import Fernet

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "secure_store_secrets", "uwg_governed_write")
_emit_writes_through("p1", "secure_store_secrets", "uwg_governed_write_2")
_emit_pulls_context("p1", "secure_store_secrets", "context_retrieval")
_emit_pulls_context("p1", "secure_store_secrets", "context_retrieval_2")
emit_determinism_digest("trace_secure_store_secrets", "secure_store_secrets_dispatch")
emit_determinism_digest("trace_secure_store_secrets", "secure_store_secrets_complete")
_emit_validated_by_safety_plane("p1", "secure_store_secrets", "safety_validation")
SECRETS_DIR = Path('C:\\Users\\amita\\.agentic_secrets')
KEY_FILE = SECRETS_DIR / '.key'
SECRETS_FILE = SECRETS_DIR / 'secrets.enc'
ENV_FILE = Path(__file__).parent.parent / '.env'

def _ensure_key() -> bytes:
    """Ensure encryption key exists, return key bytes."""
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key

def parse_env_file(env_path: Path) -> dict[str, str]:
    """Parse .env file, ignoring comments and blanks."""
    secrets = {}
    if not env_path.exists():
        return secrets
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                secrets[key.strip()] = value.strip()
    return secrets

def store_secrets(secrets: dict[str, str]) -> None:
    """Encrypt and store secrets."""
    if not secrets:
        print('Stored 0 secrets securely.')
        return
    key = _ensure_key()
    fernet = Fernet(key)
    secrets_json = json.dumps(secrets, separators=(',', ':'))
    encrypted_data = fernet.encrypt(secrets_json.encode('utf-8'))
    SECRETS_FILE.write_bytes(encrypted_data)
    print(f'Stored {len(secrets)} secrets securely.')

def main():
    """Import .env secrets to encrypted store."""
    SECRETS_DIR.mkdir(exist_ok=True)
    secrets = parse_env_file(ENV_FILE)
    store_secrets(secrets)
if __name__ == '__main__':
    main()
