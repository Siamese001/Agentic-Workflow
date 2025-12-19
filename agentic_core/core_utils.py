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

# Re-export all utilities from atomic modules for backward compatibility
from agentic_core.utils.syntax_validator import validate_python_syntax
from agentic_core.utils.mcp_mocks import (
    get_current_time, convert_time, issues_get_detail,
    browser_navigate, browser_type, browser_click,
    string_get, string_set, start_transaction, watch_key,
    transaction_set_with_ttl, commit_transaction, incr, get_and_set,
    brave_search, execute_cost_controlled_search,
    get_from_langcache, set_to_langcache,
    search_nodes, add_observations,
    search_records, write_file, read_text_file,
    semantic_score_draft, generate_draft_llm,
    get_variable_defs, get_file_versions,
)
from agentic_core.utils.error_handling import (
    MCPError, CircuitBreakerOpenError, retry_with_backoff
)
from agentic_core.utils.validation_utils import (
    validate_email, validate_url, sanitize_filename
)
from agentic_core.utils.crypto_utils import (
    setup_gpg_signing, sign_and_commit
)
from agentic_core.utils.process_utils import (
    register_process, log_action
)

# Preserve original logger for backward compatibility
import logging
logger = logging.getLogger("CanonValidator")

__all__ = [
    # Syntax Validation
    'validate_python_syntax',
    
    # MCP Mocks
    'get_current_time', 'convert_time', 'issues_get_detail',
    'browser_navigate', 'browser_type', 'browser_click',
    'string_get', 'string_set', 'start_transaction', 'watch_key',
    'transaction_set_with_ttl', 'commit_transaction', 'incr', 'get_and_set',
    'brave_search', 'execute_cost_controlled_search',
    'get_from_langcache', 'set_to_langcache',
    'search_nodes', 'add_observations',
    'search_records', 'write_file', 'read_text_file',
    'semantic_score_draft', 'generate_draft_llm',
    'get_variable_defs', 'get_file_versions',
    
    # Error Handling
    'MCPError', 'CircuitBreakerOpenError', 'retry_with_backoff',
    
    # Validation
    'validate_email', 'validate_url', 'sanitize_filename',
    
    # Cryptographic
    'setup_gpg_signing', 'sign_and_commit',
    
    # Process Management
    'register_process', 'log_action',
    
    # Logger
    'logger',
]
