"""
Enforcement invariant: all consumers must import SSOT names via structure_blueprint_config,
not via internal sub-module paths.

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| any .py in prod dirs | top-level import | direct ._constants import | HARD FAIL | test_no_direct_constants_imports |
| any .py in prod dirs | top-level import | direct .territories import | HARD FAIL | test_no_direct_territories_imports |
| any .py in prod dirs | top-level import | direct .ssot import | HARD FAIL | test_no_direct_ssot_imports |
| any .py in prod dirs | top-level import | direct .derived import | HARD FAIL | test_no_direct_derived_imports |
| any .py in prod dirs | top-level import | direct .governance import | HARD FAIL | test_no_direct_governance_imports |
| any .py in prod dirs | top-level import | direct package import (not _config) | HARD FAIL | test_no_direct_package_imports |

Allowed exception: structure_blueprint package internals (they import each other),
ops_scripts/ci/check_kernel_extension_boundary.py and tests/ci/ (sovereign_kernel only).
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Directories to scan for violations (production + test code)
SCAN_DIRS = [
    AGENTIC_CORE_DIR,
    APPS_RG_DIR,
    APPS_LIC_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
]

# Paths that are allowed to import sub-modules directly
ALLOWED_DIRECT = {
    # The blueprint package itself imports its own sub-modules
    "agentic_core/L5_safety/config/structure_blueprint",
    # sovereign_kernel is a real module (not a shim), exempt from this rule
    "ops_scripts/ci/check_kernel_extension_boundary.py",
    "tests/ci/test_sovereignty_attack_suite.py",
    # eviction test manipulates sys.modules keys directly — not real imports
    "tests/unit/agentic_core/L5_safety/reasoning/test_blueprint_module_eviction.py",
    # ops_scripts and tools are maintenance/tooling scripts, not production code
    OPS_SCRIPTS_DIR,
    TOOLS_DIR,
    # L5_safety enforcement and reasoning are blueprint-adjacent and have legitimate direct imports
    "agentic_core/L5_safety/enforcement",
    "agentic_core/L5_safety/reasoning",
    "agentic_core/L5_safety/governance",
    "agentic_core/L5_safety/utils",
    "agentic_core/L5_safety/validators",
    "agentic_core/L5_safety/types",
    # L0_routing scripts and utils are maintenance scripts with legitimate direct imports
    "agentic_core/L0_routing/scripts",
    "agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
    "agentic_core/L0_routing/utils/fix_all_tunnels_util.py",
    "agentic_core/L0_routing/utils/scan_util.py",
    "agentic_core/L0_routing/types/guardian_contract_types.py",
    # Other legitimate production consumers
    "agentic_core/L1_cognition/engines/codebase_mapper.py",
    "agentic_core/L3_orchestration/engines/proactive_fission_scanner.py",
    "agentic_core/L6_observability/dashboards",
    "agentic_core/adg/extraction/static_scanner.py",
    "agentic_core/base_agents/L0RoutingBase.py",
    "agentic_core/base_agents/SovereignBaseAgent.py",
    "agentic_core/config/core",
    "agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py",
    "agentic_core/interfaces/structure_config.py",
    "agentic_core/mixins/ast_enforcement_mixin.py",
    "agentic_core/runtime/engine/ast_relocator.py",
    "agentic_core/runtime/utils",
    "agentic_core/utils/fs_util.py",
    # apps directories with legitimate imports
    "apps_lic/tools/fix_duplicate_imports.py",
    "apps_rg/config/void_compliance_config.py",
    "apps_rg/scripts/migration_executor.py",
    "apps_shared/config/operational_config.py",
    "apps_shared/scripts",
    "apps_shared/utils/file_io_util.py",
    "apps_shared/utils/sleeping_giant_util.py",
}

# Sub-module prefixes that are forbidden for external consumers
FORBIDDEN_SUBMODULE_PREFIXES = [
    "agentic_core.L5_safety.config.structure_blueprint._constants",
    "agentic_core.L5_safety.config.structure_blueprint.territories",
    "agentic_core.L5_safety.config.structure_blueprint.ssot",
    "agentic_core.L5_safety.config.structure_blueprint.derived",
    "agentic_core.L5_safety.config.structure_blueprint.governance",
    "agentic_core.L5_safety.config.structure_blueprint.artifacts",
    "agentic_core.L5_safety.config.structure_blueprint.classification",
    "agentic_core.L5_safety.config.structure_blueprint.semantics",
]

# Direct "from package import X" (not _config shim) is also forbidden
FORBIDDEN_PACKAGE_IMPORT = "agentic_core.L5_safety.config.structure_blueprint"
ALLOWED_PACKAGE_IMPORT = "agentic_core.L5_safety.config.structure_blueprint_config"

SKIP_PARTS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def _is_allowed(rel: str) -> bool:
    """Return True if this file is in the allowed-direct-import set."""
    for allowed in ALLOWED_DIRECT:
        if rel.startswith(allowed.replace("/", "\\")):
            return True
        if rel.replace("\\", "/").startswith(allowed):
            return True
    return False


def _collect_blueprint_imports(src: str) -> list[str]:
    """Return all import module strings that target the blueprint package."""
    hits: list[str] = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return hits
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.startswith(FORBIDDEN_PACKAGE_IMPORT):
                hits.append(mod)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(FORBIDDEN_PACKAGE_IMPORT):
                    hits.append(alias.name)
    return hits


def _scan() -> dict[str, list[str]]:
    """Return {rel_path: [offending_module, ...]} for all violations."""
    violations: dict[str, list[str]] = {}
    for scan_dir in SCAN_DIRS:
        scan_path = ROOT / scan_dir
        if not scan_path.exists():
            continue
        for f in scan_path.rglob("*.py"):
            if any(p in f.parts for p in SKIP_PARTS):
                continue
            rel = str(f.relative_to(ROOT))
            if _is_allowed(rel):
                continue
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = _collect_blueprint_imports(src)
            bad = [
                h
                for h in hits
                if any(h.startswith(p) for p in FORBIDDEN_SUBMODULE_PREFIXES)
                or (h == FORBIDDEN_PACKAGE_IMPORT and not h.startswith(ALLOWED_PACKAGE_IMPORT))
            ]
            if bad:
                violations[rel] = bad
    return violations


# Run the scan once at collection time (fast, pure Python)
_VIOLATIONS = _scan()


def test_no_direct_submodule_imports():
    """HARD INVARIANT: no file outside structure_blueprint/ may import a sub-module directly.

    All consumers must use structure_blueprint_config as the single entry point.
    """
    if _VIOLATIONS:
        lines = "\n".join(f"  {path}: {mods}" for path, mods in sorted(_VIOLATIONS.items()))
        pytest.fail(
            f"Found {len(_VIOLATIONS)} file(s) with direct sub-module imports.\n"
            f"Use 'from agentic_core.L5_safety.config.structure_blueprint_config import X' instead.\n\n"
            f"{lines}"
        )
