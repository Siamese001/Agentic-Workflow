"""
Core Utils - Thin Wrapper
Delegates to consolidated tools in AgenticCore/tools/

This is a backward compatibility shim. All new code should import directly from:
    from AgenticCore.tools import *

"""

# Analysis Operations
from AgenticCore.tools.analysis_ops import (
    analyze_ast,
    count_lines_of_code,
    detect_security_issues,
    run_black_format,
    run_ruff_check,
    validate_python_syntax,
)

# Filesystem Operations
from AgenticCore.tools.filesystem import read_file as read_text_file
from AgenticCore.tools.filesystem import (
    write_file,
)

# Network Operations
from AgenticCore.tools.network_ops import (
    brave_search,
    browser_click,
    browser_navigate,
    browser_type,
    commit_transaction,
    convert_time,
    execute_cost_controlled_search,
    get_and_set,
    get_current_time,
    get_from_langcache,
    incr,
    issues_get_detail,
    search_nodes,
    search_records,
    set_to_langcache,
    start_transaction,
    string_get,
    string_set,
    transaction_set_with_ttl,
    watch_key,
)

__all__ = [
    # Analysis
    "analyze_ast",
    "count_lines_of_code",
    "detect_security_issues",
    "run_black_format",
    "run_ruff_check",
    "validate_python_syntax",
    # Network
    "brave_search",
    "browser_click",
    "browser_navigate",
    "browser_type",
    "commit_transaction",
    "convert_time",
    "execute_cost_controlled_search",
    "get_and_set",
    "get_current_time",
    "get_from_langcache",
    "incr",
    "issues_get_detail",
    "search_nodes",
    "search_records",
    "set_to_langcache",
    "start_transaction",
    "string_get",
    "string_set",
    "transaction_set_with_ttl",
    "watch_key",
    # Filesystem
    "read_text_file",
    "write_file",
]