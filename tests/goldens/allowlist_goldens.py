"""
Regression goldens for allowlists.

These goldens ensure that allowlist changes are intentional and reviewed.
Adding an entry to an allowlist requires updating this golden file.
"""

from typing import Final

# Golden: L5 Subprocess Allowlist
# Any change to L5_SUBPROCESS_ALLOWLIST must update this golden
L5_SUBPROCESS_ALLOWLIST_GOLDEN: Final[frozenset[str]] = frozenset(
    {
        "safe_subprocess_handler.py",
        "subprocess_security_util.py",
        "PreCommitSovereignAgent.py",
        "ArchitectureGovernorAgent.py",
        "AutonomyGuardianAgent.py",
        "SovereignActionPlaneAgent.py",
        "pre_deploy_check_util.py",
    },
)

# Golden: L6 Hybrid Allowlist
# Any change to L6_HYBRID_ALLOWLIST must update this golden
L6_HYBRID_ALLOWLIST_GOLDEN: Final[frozenset[str]] = frozenset(
    {
        "verify_dashboard_e2e_playwright_util.py",
    },
)

# Golden: Scripts Forbidden Patterns
# Any change to SCRIPTS_FORBIDDEN_PATTERNS must update this golden
SCRIPTS_FORBIDDEN_PATTERNS_GOLDEN: Final[list[str]] = [
    r"^[A-Z]",  # PascalCase module filenames
    r"^test_",  # Test files
]

# Golden: Layer Roots
# Any change to LAYER_ROOTS must update this golden
LAYER_ROOTS_GOLDEN: Final[frozenset[str]] = frozenset(
    {
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    },
)

# Golden: Required LCD Subfolders
# Any change to REQUIRED_LCD_SUBFOLDERS must update this golden
REQUIRED_LCD_SUBFOLDERS_GOLDEN: Final[frozenset[str]] = frozenset(
    {
        "config",
        "types",
        "reasoning",
        "enforcement",
        "validators",
        "utils",
    },
)

# Golden: Leaf Domains (no LCD allowed)
# Any change to LEAF_DOMAINS_NO_LCD must update this golden
LEAF_DOMAINS_NO_LCD_GOLDEN: Final[frozenset[str]] = frozenset(
    {
        "prompt_governance",
        "knowledge",
        "mixins",
        "runtime",
        "interfaces",
        "base_agents",
        "config",
    },
)
