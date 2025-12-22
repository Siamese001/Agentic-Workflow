"""
⚛️ THIN PROXY - Core Utils (Post-Atomic Fission)

This file is now a thin proxy that re-exports utilities from the atomic submodules
in agentic_core/utils/ for backward compatibility.

Original file: 444 lines (too complex for single healing cycle)
After Fission: 6 atomic modules (<300 lines each)

Atomic Modules:
- syntax_validator.py (40 lines) - Python syntax validation
- mcp_mocks.py (280 lines) - MCP server mock implementations
- error_handling.py (90 lines) - Exception classes and retry logic
- validation_utils.py (25 lines) - Email, URL, filename validation
- crypto_utils.py (55 lines) - GPG signing and Git operations
- process_utils.py (35 lines) - Process registration and logging

Total: 525 lines across 6 files (avg 87 lines per file)
Original: 444 lines in 1 monolithic file
Preservation: 118% (added docstrings and type hints)
"""

# Standard library imports
import logging

from agentic_core.utils.crypto_utils import (
    setup_gpg_signing,
    sign_and_commit,
)
from agentic_core.utils.error_handling import (
    CircuitBreakerOpenError,
    MCPError,
    retry_with_backoff,
)
from agentic_core.utils.mcp_mocks import (
    add_observations,
    brave_search,
    browser_click,
    browser_navigate,
    browser_type,
    commit_transaction,
    convert_time,
    execute_cost_controlled_search,
    generate_draft_llm,
    get_and_set,
    get_current_time,
    get_file_versions,
    get_from_langcache,
    get_variable_defs,
    incr,
    issues_get_detail,
    read_text_file,
    search_nodes,
    search_records,
    semantic_score_draft,
    set_to_langcache,
    start_transaction,
    string_get,
    string_set,
    transaction_set_with_ttl,
    watch_key,
    write_file,
)
from agentic_core.utils.process_utils import (
    log_action,
    register_process,
)

# Re-export all utilities from atomic modules for backward compatibility
from agentic_core.utils.syntax_validator import validate_python_syntax
from agentic_core.utils.validation_utils import (
    sanitize_filename,
    validate_email,
    validate_url,
)

# Preserve original logger for backward compatibility
logger = logging.getLogger("CanonValidator")

__all__ = [
    # Syntax Validation
    'validate_python_syntax',

    # MCP Mocks (Alphabetical for easier lookup)
    'add_observations',
    'brave_search',
    'browser_click',
    'browser_navigate',
    'browser_type',
    'commit_transaction',
    'convert_time',
    'execute_cost_controlled_search',
    'generate_draft_llm',
    'get_and_set',
    'get_current_time',
    'get_file_versions',
    'get_from_langcache',
    'get_variable_defs',
    'incr',
    'issues_get_detail',
    'read_text_file',
    'search_nodes',
    'search_records',
    'semantic_score_draft',
    'set_to_langcache',
    'start_transaction',
    'string_get',
    'string_set',
    'transaction_set_with_ttl',
    'watch_key',
    'write_file',

    # Error Handling (Alphabetical)
    'CircuitBreakerOpenError',
    'MCPError',
    'retry_with_backoff',

    # Validation (Alphabetical)
    'sanitize_filename',
    'validate_email',
    'validate_url',

    # Cryptographic (Alphabetical)
    'setup_gpg_signing',
    'sign_and_commit',

    # Process Management (Alphabetical)
    'log_action',
    'register_process',

    # Logger
    'logger',
]