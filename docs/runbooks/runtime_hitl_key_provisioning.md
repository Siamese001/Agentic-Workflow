# Runtime HITL — Key Provisioning Runbook

**Audience:** platform operator / SRE
**Scope:** ed25519 key management for the runtime HITL audit chain (W7 P7.1)
**Peer docs:** `docs/architecture/runtime_hitl_soc2_mapping.md` §4 (Key Management)

---

## Overview

The HITL audit chain is **tamper-evident without signing**. Signing adds
**authenticity**: proof that the row was written by the production service,
not an attacker with SQLite write access.

- **Private key** lives only in the production environment (never in Git, never in CI).
- **Public key** is published to CI as a secret so nightly verification can validate signatures.
- **Rotation** is quarterly. Old public keys are retained forever for historical verification.

---

## 1. Generate a new keypair

Run this ONCE per rotation cycle, on a hardened workstation:

```bash
python - <<'PY'
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from pathlib import Path
import datetime

key = ed25519.Ed25519PrivateKey.generate()
priv_raw = key.private_bytes_raw()              # 32 bytes
pub_raw = key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)
stamp = datetime.date.today().isoformat()
Path(f"hitl_priv_{stamp}.hex").write_text(priv_raw.hex(), encoding="utf-8")
Path(f"hitl_pub_{stamp}.hex").write_text(pub_raw.hex(), encoding="utf-8")
print(f"Generated hitl_priv_{stamp}.hex (SECRET) and hitl_pub_{stamp}.hex (public).")
PY
```

- `hitl_priv_<date>.hex` → provision to prod secret manager, then **delete local copy**
- `hitl_pub_<date>.hex` → commit metadata only (fingerprint), publish to CI as secret

---

## 2. Provision the private key to production

### AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name runtime/hitl/ed25519_private_key \
  --secret-string "$(cat hitl_priv_YYYY-MM-DD.hex)"
```

Application reads it via:

```python
import os
from agentic_core.L3_orchestration.exit_control.ledger_integrity import Ed25519SigningKey

signing_key = Ed25519SigningKey(bytes.fromhex(os.environ["RUNTIME_HITL_PRIVATE_KEY_HEX"]))
```

### Environment variable (dev / staging)

Set `RUNTIME_HITL_PRIVATE_KEY_HEX` in the service environment. **NEVER** commit
a `.env` file containing it.

### HSM (future)

The `SigningKey` Protocol is HSM-compatible. Any class implementing `sign(bytes) → bytes`
and exposing `public_key_bytes` works. HSM integration is a future enhancement — see
`runtime_hitl_soc2_mapping.md` §6 Out-of-Scope.

---

## 3. Publish the public key to CI

Add two GitHub repository secrets (Settings → Secrets → Actions):

| Secret name | Value |
|-------------|-------|
| `HITL_LEDGER_PUBLIC_KEY_HEX` | Contents of `hitl_pub_<date>.hex` (hex string, no newline) |
| `HITL_LEDGER_SNAPSHOT_URL` | Pre-signed URL to the latest production audit-chain snapshot |

The workflow `.github/workflows/hitl-integrity-gate.yml` picks these up:

- On schedule (daily 07:00 UTC) or `workflow_dispatch`, the `production` job downloads the snapshot, loads the public key, and runs `--require-signatures`.
- If the public key secret is absent, verification falls back to **unsigned mode** — linkage is still checked, authenticity is not.

---

## 4. Snapshot export from production

The workflow pulls an audit-chain SQLite file from a pre-signed URL. Choose one:

### Option A — scheduled S3 upload from prod

```bash
aws s3 cp /var/lib/agentic/hitl_audit.db \
  s3://agentic-runtime-audit/$(date +%Y%m%d)/hitl_audit.db \
  --sse aws:kms --sse-kms-key-id <kms-key-id>

# Generate pre-signed URL, update HITL_LEDGER_SNAPSHOT_URL secret
aws s3 presign s3://agentic-runtime-audit/$(date +%Y%m%d)/hitl_audit.db --expires-in 604800
```

### Option B — direct-pull from prod (VPN or private endpoint)

CI runs inside a self-hosted runner with network access to prod. No snapshot upload needed.
This requires additional infrastructure out of this runbook's scope.

---

## 5. Rotation procedure

Quarterly (Jan/Apr/Jul/Oct, 1st of month):

1. **Generate** new keypair (step 1)
2. **Provision** new private key alongside the old one (dual-key period, 7 days)
3. **Publish** new public key. Keep the old public key available for historical verification — storage format: `docs/runbooks/hitl_public_keys/<date>.hex` committed to repo
4. **Switch** production service to new key at day 7 (deploy)
5. **Decommission** old private key at day 14 (remove from secrets manager)
6. **Verify** `python ops_scripts/ci/check_runtime_hitl_ledger_integrity.py --audit-db <snapshot> --public-key-file docs/runbooks/hitl_public_keys/<new-date>.hex` passes
7. **Record** rotation in `docs/runbooks/hitl_public_keys/ROTATION_LOG.md`

---

## 6. Incident response — suspected key compromise

If the private key is believed exposed:

1. **Rotate immediately** — do not wait for the quarterly cycle
2. **Retain** the compromised public key in `hitl_public_keys/` — historical rows signed before the compromise window remain valid evidence
3. **Mark** the compromise window in `ROTATION_LOG.md` with a `COMPROMISED_FROM <timestamp> TO <timestamp>` row
4. **Review** ledger entries signed during the compromise window — these require manual corroboration (OTEL spans, adapter logs, approver identity via SSO)
5. **File** a SOC 2 incident record per internal policy

---

## 7. Verification the key works end-to-end

Local smoke test after provisioning:

```bash
python - <<'PY'
from agentic_core.L3_orchestration.exit_control.ledger_integrity import (
    AuditChain, AuditEventType, Ed25519SigningKey, Ed25519VerifyingKey,
)
import os, tempfile, pathlib

priv = bytes.fromhex(os.environ["RUNTIME_HITL_PRIVATE_KEY_HEX"])
signing = Ed25519SigningKey(priv)
with tempfile.TemporaryDirectory() as td:
    path = pathlib.Path(td) / "smoke.db"
    chain = AuditChain(path, signing_key=signing)
    chain.append(ledger_id="smoke", run_id="r",
                 event_type=AuditEventType.CREATED, payload={})
    report = chain.verify(verifying_key=Ed25519VerifyingKey(signing.public_key_bytes))
    assert report.ok, report.violations
    print("Key verified end-to-end.")
PY
```

If this prints `Key verified end-to-end.`, the production key is correctly provisioned.

---

## 8. Minimum operator checklist (ship-day)

- [ ] Generate keypair (step 1)
- [ ] Provision `RUNTIME_HITL_PRIVATE_KEY_HEX` to production secret store
- [ ] Deploy service with the signing key enabled
- [ ] Commit current public key to `docs/runbooks/hitl_public_keys/<date>.hex`
- [ ] Publish `HITL_LEDGER_PUBLIC_KEY_HEX` and `HITL_LEDGER_SNAPSHOT_URL` to GitHub secrets
- [ ] Trigger `workflow_dispatch` on `hitl-integrity-gate.yml` and confirm the production job succeeds
- [ ] Add rotation reminder to the team calendar (next quarter)
