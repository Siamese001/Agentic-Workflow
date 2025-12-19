"""
Core Utils - Thin Wrapper
Delegates to consolidated tools in agentic_core/tools/

This is a backward compatibility shim. All new code should import directly from:
    from agentic_core.tools import *
"""

# Analysis Operations
from agentic_core.tools.analysis_ops import (
    validate_python_syntax,
    run_ruff_check,
    run_black_format,
    analyze_ast,
    count_lines_of_code,
    detect_security_issues,
)

# Network Operations
from agentic_core.tools.network_ops import (
    get_current_time,
    convert_time,
    issues_get_detail,
    browser_navigate,
    browser_type,
    browser_click,
    string_get,
    string_set,
    start_transaction,
    watch_key,
    transaction_set_with_ttl,
    commit_transaction,
    incr,
    brave_search,
    execute_cost_controlled_search,
    get_from_langcache,
    set_to_langcache,
    get_and_set,
    search_nodes,
    search_records,
)

# Filesystem Operations
from agentic_core.tools.filesystem import (
    read_file as read_text_file,
    write_file,
)

__all__ = [
    # Analysis
    "validate_python_syntax",
    "run_ruff_check",
    "run_black_format",
    "analyze_ast",
    "count_lines_of_code",
    "detect_security_issues",
    # Network
    "get_current_time",
    "convert_time",
    "issues_get_detail",
    "browser_navigate",
    "browser_type",
    "browser_click",
    "string_get",
    "string_set",
    "start_transaction",
    "watch_key",
    "transaction_set_with_ttl",
    "commit_transaction",
    "incr",
    "brave_search",
    "execute_cost_controlled_search",
    "get_from_langcache",
    "set_to_langcache",
    "get_and_set",
    "search_nodes",
    "search_records",
    # Filesystem
    "read_text_file",
    "write_file",
]
