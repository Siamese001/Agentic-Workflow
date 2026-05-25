# Release Signer Runbook

> **Plan**: `apps-fort-knox-parity-c5d9a3` W10 (OPEN-4 closure).
> **Scope**: Ed25519 dev-keypair rotation for the W5/W9 Fort Knox signer.
> **Audience**: release engineers + ops on-call.

This runbook covers the **dev-keypair** path (`tools/cert/apps_e2e/sign_apps_release_bundle.py`) which is what produces the SIGNED_PROOF claim. The keyless cosign path (W9, FINAL_SIGNED_CERTIFICATION) does NOT need rotation \u2014 it uses ephemeral certificates from Sigstore Fulcio with no long-lived keypair.

---

## 1. When to rotate

Rotate the release signer keypair when ANY of the following hold:

| Trigger | Severity | Window |
|---|---|---|
| Suspected private-key exposure (laptop loss, accidental commit, etc.) | P0 | Immediate |
| Ex-employee with access to `artifacts/keys/release_signer/release_signer.key.pem` | P0 | Within 24h of departure |
| Annual rotation cadence | P3 | Every 365 days from `signing_timestamp_utc` of last rotation |
| Cryptographic algorithm deprecation (Ed25519 \u2192 Ed448 etc.) | P2 | Within the deprecation window |
| Quarterly hygiene audit flags age > 365 days | P3 | Next maintenance window |

**Default**: schedule annual rotation. If you cannot remember when the keypair was last rotated, treat that as a P3 trigger and rotate within 30 days.

## 2. Pre-rotation checklist

Before running rotation:

- [ ] Confirm a clean working tree on `main`. Rotation produces a new public key that downstream verifiers must accept.
- [ ] Confirm the latest W6 bundle is at `trust_level=SIGNED_OFF_WITH_WAIVERS` or better (`python ops_scripts/ci/check_apps_fortknox_signed_proof.py` exits 0).
- [ ] Confirm there are no in-flight signature consumers expecting the old fingerprint (search the repo for the existing `signer_identity` value).
- [ ] Notify any external verifiers (currently none for the apps_e2e arm; agentic_core arm shares the same keypair so coordinate with that runbook).
- [ ] Snapshot current state so rollback is one git command:
      ```pwsh
      git tag pre-keypair-rotation-$(Get-Date -Format yyyyMMdd-HHmmss)
      ```

## 3. Rotation procedure

### Step 1 \u2014 Generate the new keypair

```pwsh
python tools/cert/apps_e2e/sign_apps_release_bundle.py --rotate-keys
```

This:

- Generates a fresh Ed25519 keypair
- Writes `artifacts/keys/release_signer/release_signer.key.pem` (private \u2014 must NOT be committed; verify `.gitignore`)
- Writes `config/release_signer/release_signer.pub.pem` (public \u2014 IS committed)
- Updates `config/release_signer/release_signer.pub.fingerprint` (committed; `signer_identity` consumers read this)
- Re-signs the current `apps_e2e_signoff_report.json`

### Step 2 \u2014 Verify the new fingerprint locally

```pwsh
python tools/cert/apps_e2e/verify_apps_release_signature.py
python tools/certification/generate_apps_100pct_runtime_proof.py
python ops_scripts/ci/check_apps_fortknox_signed_proof.py
```

All three must exit 0. Confirm the new `signer_identity` matches the new public-key fingerprint:

```pwsh
Get-Content artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.json | python -c "import json,sys; d=json.load(sys.stdin); print(d['signer_identity'])"
Get-Content config/release_signer/release_signer.pub.fingerprint
```

The fingerprint suffix in `signer_identity` must equal the contents of the `.fingerprint` file.

### Step 3 \u2014 Commit the public-side changes

```pwsh
git add config/release_signer/release_signer.pub.pem
git add config/release_signer/release_signer.pub.fingerprint
git add artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.json
git add artifacts/certification/apps_e2e/APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json
git commit -m "ops: rotate release-signer keypair (Ed25519, fingerprint=$(Get-Content config/release_signer/release_signer.pub.fingerprint))"
```

**Do NOT commit** `artifacts/keys/release_signer/release_signer.key.pem`. Pre-commit gate `T7s.1` (clean-bundle) will reject the commit if the private key materialized in the index.

### Step 4 \u2014 Announce the new fingerprint

- Update the running `apps-fort-knox-parity-c5d9a3` plan with a §-bullet noting the rotation date and new fingerprint suffix
- If external verifiers exist (e.g. downstream consumers pinning the old fingerprint): notify them BEFORE merging the rotation commit
- Tag the rotation commit:
      ```pwsh
      git tag release-signer-rotation-$(Get-Date -Format yyyyMMdd)
      git push origin --tags
      ```

### Step 5 \u2014 Securely destroy the old private key

After 30 days of new-key signatures running cleanly in CI:

- Confirm no rollback was needed (no consumer pinned the old fingerprint)
- Confirm the new fingerprint appears in every recent W5 envelope
- Securely shred the old `release_signer.key.pem.bak` (if backed up locally):
      ```pwsh
      # Cipher /w erases free space, NOT a specific file. Use a real shredder.
      # Windows: SDelete (sysinternals)
      sdelete -p 7 path\to\old_release_signer.key.pem.bak
      ```

## 4. Rollback (if rotation breaks something)

If the rotation commit causes downstream verification failures:

```pwsh
# Revert the rotation commit
git revert <rotation-commit-sha>

# Restore the private key from your secret manager (see your org's
# secret-manager runbook \u2014 NOT documented here intentionally).

# Re-verify the old keypair still produces a valid signature
python tools/cert/apps_e2e/sign_apps_release_bundle.py
python tools/cert/apps_e2e/verify_apps_release_signature.py
```

If the OLD private key is also lost (worst case):

- The apps_e2e Fort Knox track temporarily drops to `INTEGRITY_PROOF` (W3 compiler still works; only the W5 signature is gone)
- Generate a fresh keypair via `--rotate-keys`
- Re-sign and accept the trust-level downgrade until the new keypair has been in use long enough for external verifiers to update

## 5. Communicating the new fingerprint to verifiers

Verifiers that must accept the new public key:

| Verifier | Where it reads the fingerprint | Update mechanism |
|---|---|---|
| `tools/cert/apps_e2e/verify_apps_release_signature.py` | `config/release_signer/release_signer.pub.pem` | Automatic on `git pull` |
| `tools/certification/generate_apps_100pct_runtime_proof.py` | reads from `apps_e2e_signoff_report.signature.json` directly | Automatic on `git pull` |
| `ops_scripts/ci/check_apps_fortknox_signed_proof.py` | re-runs the generator | Automatic on `git pull` |
| External verifiers (if any) | their own pinned fingerprint config | **Manual** \u2014 notify per Step 4 |

There are currently no known external verifiers for the apps_e2e arm. Re-audit before claiming "no external verifiers" if rotating in a different month than this runbook was last updated.

## 6. Cosign keyless (W9) does NOT need rotation

The W9 keyless path (`sign_apps_release_bundle_keyless.py`) uses Sigstore Fulcio's ephemeral certificate flow. The signing identity is the GitHub Actions OIDC subject, not a long-lived keypair. There is no key to rotate on this side; rotation of the OIDC subject happens automatically when:

- The workflow file path changes (`.github/workflows/apps-fortknox-keyless-sign.yml`)
- The repository moves
- The Git tag pattern changes

If any of those happen, the `signer_identity_subject` in the keyless envelope will change, and downstream verifiers must update their `--certificate-identity-regexp` pin. That is its own change, not a rotation.

## 7. Audit trail

Every rotation MUST leave a paper trail in:

1. The rotation git commit (Step 3) \u2014 includes the new fingerprint in the commit message
2. The Git tag `release-signer-rotation-YYYYMMDD` (Step 4)
3. The plan file's open-scope or appendix section (Step 4)
4. The Notion plan row's Summary field (manual; reference the rotation tag)

CI gate `T7s.1` (clean-bundle) verifies the signature against the committed public key on every push, so any uncommunicated rotation will fail CI within minutes.

---

## Appendix \u2014 Keypair file locations

| Path | Status | Committed? |
|---|---|---|
| `artifacts/keys/release_signer/release_signer.key.pem` | Private key | **NO** |
| `config/release_signer/release_signer.pub.pem` | Public key | YES |
| `config/release_signer/release_signer.pub.fingerprint` | Convenience (sha256 of public key) | YES |
| `artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.json` | Latest signature envelope | YES |

If you find a private key file at a path NOT in this table, treat it as a leaked-credential incident (P0 trigger above).

## References

- Plan SSOT: `.windsurf/plans/apps-fort-knox-parity-c5d9a3.md` W5 + W10
- Constitutional rule: `.windsurf/rules/constitutional.md` \u00a732 (Fort Knox certification integrity, two arms)
- Signer source: `tools/cert/apps_e2e/sign_apps_release_bundle.py`
- Verifier source: `tools/cert/apps_e2e/verify_apps_release_signature.py`
- CI gate: `ops_scripts/ci/check_apps_fortknox_signed_proof.py` (T7s.4)
- Sibling agentic_core runbook: pending (the agentic_core arm uses the same keypair; this runbook is the canonical reference until the agentic_core arm gets its own).
