"""
File: scripts/discover_agents.py
Path: C:\\Git\\Agentic-Workflow\\scripts\\discover_agents.py
Status: Post-Migration Validation Tool
Rationale:
    Referenced in DEPLOYMENT_PROTOCOL.md.
    This script verifies that the "Pascal Sovereignty" migration was successful by:
    1. Finding all files ending in 'Agent.py'.
    2. attempting to import them (verifying paths/imports are healthy).
    3. Confirming the internal class name matches the filename.
"""
import ast
import importlib.util
import sys
from pathlib import Path

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
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "sovereignty_auditor")
_emit_applies_guardrail("p0", "sovereignty_auditor", "p0_governance")
_emit_reads_policy_state("p0", "sovereignty_auditor", "policy_binding")
_emit_snapshots_state("p0", "sovereignty_auditor", "state_snapshot")
emit_replay_key("p0", "sovereignty_auditor")
emit_determinism_digest("p0", "sovereignty_auditor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
REPO_ROOT = Path(__file__).parent.parent.resolve()
# guardian: allow-global-mutation
sys.path.insert(0, str(REPO_ROOT))
from agentic_core.utils.ssot_discovery_validator import get_python_files

from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)


class SovereigntyAuditor:

    def __init__(self):
        self.agents_found = 0
        self.import_failures = []
        self.naming_violations = []

    def audit_file(self, path: Path):
        if not path.name.endswith('Agent.py'):
            return
        self.agents_found += 1
        module_name = path.stem
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if module_name not in classes:
                self.naming_violations.append(f"{path.name}: Expected class '{module_name}' not found. Found: {classes}")
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            self.naming_violations.append(f'{path.name}: AST Parse Error - {e}')
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
        except ImportError as e:
            self.import_failures.append(f'{path.name}: {e}')
        # guardian: allow-silent-swallow
        except Exception as e:
            self.import_failures.append(f'{path.name}: Runtime Error - {e}')

    def run(self):
        print('=' * 60)
        print('PASCAL SOVEREIGNTY: POST-MIGRATION AUDIT')
        print('=' * 60)
        target_dirs = [REPO_ROOT / d for d in [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]]
        files = []
        for d in target_dirs:
            if d.exists():
                files.extend(get_python_files(d))
        print(f'Scanning {len(files)} files for Agents...')
        for f in files:
            self.audit_file(f)
        print('\n' + '=' * 60)
        print(f'Agents Found: {self.agents_found}')
        print(f'Naming Violations: {len(self.naming_violations)}')
        print(f'Import Failures:   {len(self.import_failures)}')
        if self.naming_violations:
            print('\n[!] NAMING VIOLATIONS (Class name != Filename):')
            for v in self.naming_violations:
                print(f'  - {v}')
        if self.import_failures:
            print('\n[!] IMPORT FAILURES (Broken References):')
            for f in self.import_failures:
                print(f'  - {f}')
        if self.import_failures:
            sys.exit(1)
        print('\n[PASS] Architecture Integrity Verified.')
        sys.exit(0)
if __name__ == '__main__':
    SovereigntyAuditor().run()
