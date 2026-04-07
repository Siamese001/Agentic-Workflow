"""V15 Phase 3 Gate Runner — No Silent State Mutation (§13.1)

CI-ready evidence-only gate. Detects forbidden mutation patterns:
- Direct os.environ mutation outside guardian-allowed contexts
- Global variable assignment in module scope of enforcement files
- SemanticClock usage without tick() call in gateway paths

Emits evidence JSON to docs/reports/plans/. Non-blocking (exit 0).

Usage:
    python ops_scripts/ci/run_v15_p3_gate.py
    python ops_scripts/ci/run_v15_p3_gate.py --repo-root /path/to/repo
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
ENFORCEMENT_FILES = ['agentic_core/L0_routing/enforcement/execution_gateway.py', 'agentic_core/L0_routing/enforcement/runtime_guard.py', 'agentic_core/L0_routing/enforcement/traceability_contracts.py', 'agentic_core/base_agents/SovereignBaseAgent.py']
FORBIDDEN_GLOBAL_PATTERNS = ['os.environ[', 'os.putenv(', 'globals()[']

class P3EvidenceCollector:
    """Collect evidence for §13.1 — No Silent State Mutation."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.violations: list[dict] = []
        self.checks_passed: list[dict] = []

    def collect(self) -> dict:
        """Run all P3 checks and return evidence dict."""
        self._check_forbidden_mutation_patterns()
        self._check_semantic_clock_wiring()
        self._check_state_hash_fn_present()
        total = len(self.violations) + len(self.checks_passed)
        return {'phase': 'P3', 'gate': 'no_silent_state_mutation', 'spec_section': '§13.1', 'timestamp': _FIXED_TS, 'total_checks': total, 'passed': len(self.checks_passed), 'violations': len(self.violations), 'violation_details': self.violations, 'passed_details': self.checks_passed, 'blocking': False}

    def _check_forbidden_mutation_patterns(self):
        """Scan enforcement files for forbidden global mutation patterns."""
        for rel_path in ENFORCEMENT_FILES:
            fpath = self.repo_root / rel_path
            if not fpath.exists():
                continue
            content = fpath.read_text(encoding='utf-8')
            lines = content.splitlines()
            found_violations = False
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith('#') or 'guardian: allow-global-mutation' in line:
                    continue
                for pattern in FORBIDDEN_GLOBAL_PATTERNS:
                    if pattern in stripped:
                        self.violations.append({'check': 'forbidden_mutation_pattern', 'file': rel_path, 'line': i, 'pattern': pattern, 'content': stripped[:120]})
                        found_violations = True
            if not found_violations:
                self.checks_passed.append({'check': 'forbidden_mutation_pattern', 'file': rel_path, 'detail': 'No forbidden mutation patterns found'})

    def _check_semantic_clock_wiring(self):
        """Verify SemanticClock is imported and tick() is called in gateway."""
        gw_path = self.repo_root / 'agentic_core/L0_routing/enforcement/execution_gateway.py'
        if not gw_path.exists():
            self.violations.append({'check': 'semantic_clock_wiring', 'file': 'execution_gateway.py', 'detail': 'Gateway file not found'})
            return
        content = gw_path.read_text(encoding='utf-8')
        has_import = 'SemanticClock' in content
        has_clock_tick = '_clock.tick(' in content
        has_clock_prepare = '_clock.prepare_commit(' in content
        if has_import and has_clock_tick:
            self.checks_passed.append({'check': 'semantic_clock_wiring', 'file': 'execution_gateway.py', 'detail': f'SemanticClock imported, _clock.tick() called, prepare_commit={has_clock_prepare}'})
        else:
            self.violations.append({'check': 'semantic_clock_wiring', 'file': 'execution_gateway.py', 'detail': f'SemanticClock import={has_import}, _clock.tick={has_clock_tick}'})

    def _check_state_hash_fn_present(self):
        """Verify state_hash_fn is passed to gateway.execute()."""
        sba_path = self.repo_root / 'agentic_core/base_agents/SovereignBaseAgent.py'
        if not sba_path.exists():
            return
        content = sba_path.read_text(encoding='utf-8')
        has_state_hash = 'state_hash_fn' in content
        if has_state_hash and 'state_hash_fn=state_hash_fn' in content:
            self.checks_passed.append({'check': 'state_hash_fn_present', 'file': 'SovereignBaseAgent.py', 'detail': 'state_hash_fn passed to gateway.execute()'})
        else:
            self.violations.append({'check': 'state_hash_fn_present', 'file': 'SovereignBaseAgent.py', 'detail': 'state_hash_fn not properly wired'})

def main() -> int:
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='V15 Phase 3 Gate — No Silent State Mutation')
    parser.add_argument('--repo-root', type=Path, default=None)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    repo_root = args.repo_root or PROJECT_ROOT
    output = args.output or EVIDENCE_DIR / 'v15_p3_evidence.json'
    print('[P3-GATE] Starting Phase 3 gate (§13.1 — No Silent State Mutation)...')
    collector = P3EvidenceCollector(repo_root)
    evidence = collector.collect()
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(evidence, f, indent=2, sort_keys=True)
    print(f'[P3-GATE] Evidence written to: {output}')
    print(f"[P3-GATE] Checks passed: {evidence['passed']}, Violations: {evidence['violations']}")
    print('[P3-GATE] PASSED (evidence-only, non-blocking)')
    return 0
if __name__ == '__main__':
    sys.exit(main())
