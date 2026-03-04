# Re-export shim: agentic_core.enforcement → agentic_core.L5_safety.enforcement
from agentic_core.L5_safety.enforcement.sealed_interface_check_enforcer import (  # noqa: F401
    check_file,
    main,
    run_check,
)
