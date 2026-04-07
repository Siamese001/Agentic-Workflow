"""V15 Phase 5 Gate Runner — Tokenized Authority (§2.7)

CI-ready evidence-only gate. Verifies authority artifact infrastructure:
- SignedModify type exists with required fields
- ensure_v15_signed function exists in guardian_contract
- PolicyExceptionArtifact exists for policy challenge protocol
- Authority artifacts are frozen (immutable)

Emits evidence JSON to docs/reports/plans/. Non-blocking (exit 0).

Usage:
    python ops_scripts/ci/run_v15_p5_gate.py
    python ops_scripts/ci/run_v15_p5_gate.py --repo-root /path/to/repo
"""
import json
import sys

_FIXED_TS = "2026-01-01T00:00:00Z"
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
EVIDENCE_DIR = PROJECT_ROOT / 'docs' / REPORTS_DIR / 'plans'
SIGNED_MODIFY_REQUIRED_FIELDS = ['trace_id', 'human_reviewer_id', 'resolution']
POLICY_EXCEPTION_REQUIRED_FIELDS = ['trace_id', 'nonce', 'exception_scope']

class P5EvidenceCollector:
    """Collect evidence for §2.7 — Tokenized Authority."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.violations: list[dict] = []
        self.checks_passed: list[dict] = []

    def collect(self) -> dict:
        """Run all P5 checks and return evidence dict."""
        self._check_signed_modify_type()
        self._check_ensure_v15_signed()
        self._check_policy_exception_artifact()
        self._check_authority_immutability()
        self._check_evidence_pack_type()
        total = len(self.violations) + len(self.checks_passed)
        return {'phase': 'P5', 'gate': 'tokenized_authority', 'spec_section': '§2.7', 'timestamp': _FIXED_TS, 'total_checks': total, 'passed': len(self.checks_passed), 'violations': len(self.violations), 'violation_details': self.violations, 'passed_details': self.checks_passed, 'blocking': False}

    def _check_signed_modify_type(self):
        """Verify SignedModify type exists with required fields."""
        p5_path = self.repo_root / 'agentic_core/L0_routing/types/crypto_trust_types.py'
        if not p5_path.exists():
            self.violations.append({'check': 'signed_modify_type', 'detail': 'crypto_trust_types.py not found'})
            return
        content = p5_path.read_text(encoding='utf-8')
        has_class = 'class SignedModify' in content
        missing_fields = []
        for field in SIGNED_MODIFY_REQUIRED_FIELDS:
            if f'{field}:' not in content and f'{field} :' not in content:
                missing_fields.append(field)
        if has_class and (not missing_fields):
            self.checks_passed.append({'check': 'signed_modify_type', 'detail': f'SignedModify found with all {len(SIGNED_MODIFY_REQUIRED_FIELDS)} required fields'})
        else:
            self.violations.append({'check': 'signed_modify_type', 'detail': f'class={has_class}, missing_fields={missing_fields}'})

    def _check_ensure_v15_signed(self):
        """Verify ensure_v15_signed function exists in guardian_contract."""
        gc_path = self.repo_root / 'agentic_core/L0_routing/types/guardian_contract_types.py'
        if not gc_path.exists():
            self.violations.append({'check': 'ensure_v15_signed', 'detail': 'guardian_contract.py not found'})
            return
        content = gc_path.read_text(encoding='utf-8')
        if 'ensure_v15_signed' in content:
            self.checks_passed.append({'check': 'ensure_v15_signed', 'detail': 'ensure_v15_signed found in guardian_contract'})
        else:
            self.violations.append({'check': 'ensure_v15_signed', 'detail': 'ensure_v15_signed not found in guardian_contract'})

    def _check_policy_exception_artifact(self):
        """Verify PolicyExceptionArtifact exists with required fields."""
        p3_path = self.repo_root / 'agentic_core/L0_routing/types/governance_types.py'
        if not p3_path.exists():
            self.violations.append({'check': 'policy_exception_artifact', 'detail': 'governance_types.py not found'})
            return
        content = p3_path.read_text(encoding='utf-8')
        has_class = 'class PolicyExceptionArtifact' in content
        missing_fields = []
        for field in POLICY_EXCEPTION_REQUIRED_FIELDS:
            if f'{field}:' not in content and f'{field} :' not in content:
                missing_fields.append(field)
        if has_class and (not missing_fields):
            self.checks_passed.append({'check': 'policy_exception_artifact', 'detail': 'PolicyExceptionArtifact found with required fields'})
        else:
            self.violations.append({'check': 'policy_exception_artifact', 'detail': f'class={has_class}, missing_fields={missing_fields}'})

    def _check_authority_immutability(self):
        """Verify authority artifacts use frozen=True."""
        p5_path = self.repo_root / 'agentic_core/L0_routing/types/crypto_trust_types.py'
        if not p5_path.exists():
            return
        content = p5_path.read_text(encoding='utf-8')
        frozen_count = content.count('@dataclass(frozen=True)')
        total_dc = content.count('@dataclass')
        if total_dc > 0 and frozen_count == total_dc:
            self.checks_passed.append({'check': 'authority_immutability', 'detail': f'All {total_dc} dataclasses in crypto_trust_types are frozen=True'})
        elif total_dc > 0:
            self.violations.append({'check': 'authority_immutability', 'detail': f'{frozen_count}/{total_dc} dataclasses are frozen'})

    def _check_evidence_pack_type(self):
        """Verify EvidencePack exists for human escalation (§3.4)."""
        p3_path = self.repo_root / 'agentic_core/L0_routing/types/governance_types.py'
        if not p3_path.exists():
            return
        content = p3_path.read_text(encoding='utf-8')
        if 'class EvidencePack' in content and 'trace_id:' in content:
            self.checks_passed.append({'check': 'evidence_pack_type', 'detail': 'EvidencePack found with trace_id for human escalation'})
        else:
            self.violations.append({'check': 'evidence_pack_type', 'detail': 'EvidencePack missing or incomplete'})

def main() -> int:
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='V15 Phase 5 Gate — Tokenized Authority')
    parser.add_argument('--repo-root', type=Path, default=None)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    repo_root = args.repo_root or PROJECT_ROOT
    output = args.output or EVIDENCE_DIR / 'v15_p5_evidence.json'
    print('[P5-GATE] Starting Phase 5 gate (§2.7 — Tokenized Authority)...')
    collector = P5EvidenceCollector(repo_root)
    evidence = collector.collect()
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(evidence, f, indent=2, sort_keys=True)
    print(f'[P5-GATE] Evidence written to: {output}')
    print(f"[P5-GATE] Checks passed: {evidence['passed']}, Violations: {evidence['violations']}")
    print('[P5-GATE] PASSED (evidence-only, non-blocking)')
    return 0
if __name__ == '__main__':
    sys.exit(main())
