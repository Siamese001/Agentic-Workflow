"""L4 State Adapters — sanctioned infrastructure access surface.

Constitutional §22: All external infrastructure access MUST flow through
these adapters. Direct imports of sqlite3, redis, chromadb, etc. in
non-adapter modules are P2 violations.
"""

from agentic_core.L4_state.adapters.sqlite3_adapter import (
    Connection,
    Cursor,
    IntegrityError,
    OperationalError,
    ProgrammingError,
    Row,
    connect,
    connection,
    count_rows,
    ensure_schema,
    optimize,
    sqlite3,
    table_columns,
    table_exists,
    table_schema,
    vacuum,
)

__all__ = [
    "connect",
    "connection",
    "count_rows",
    "ensure_schema",
    "optimize",
    "sqlite3",
    "table_columns",
    "table_exists",
    "table_schema",
    "vacuum",
    "Connection",
    "Cursor",
    "IntegrityError",
    "OperationalError",
    "ProgrammingError",
    "Row",
]
