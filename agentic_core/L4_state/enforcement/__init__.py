"""C4 Universal Write Governance (UWG) - Single ink path for all mutations.

Implements 10C GAP-10C-007:
- U1: UWG ONLY - Singleton clerk with serialized write queue
- U2: VERIFY THE BOSS - Signature/compliance hash/capability validation
- U3: CHECK CATALOG RULES - RBAC, blast radius, before-after diff
- U4: CLAIM WRITE LOCK - Exclusive write access, ghost write prevention
- U5: COMMIT + CHAIN APPEND - Durable ledger, hash-chain audit log
- U6: REFRESH READ SURFACES - Alias swap, cache clear
"""

from .uwg_clerk import UWGClerk, WriteRequest, WriteReceipt
from .uwg_verifier import UWGVerifier, VerificationResult
from .uwg_catalog_checker import UWGCatalogChecker, CatalogRuleResult
from .uwg_locker import UWGLocker, WriteLock
from .uwg_committer import UWGCommitter, CommitRecord
from .uwg_refresher import UWGRefresher, RefreshResult

__all__ = [
    "UWGClerk",
    "WriteRequest",
    "WriteReceipt",
    "UWGVerifier",
    "VerificationResult",
    "UWGCatalogChecker",
    "CatalogRuleResult",
    "UWGLocker",
    "WriteLock",
    "UWGCommitter",
    "CommitRecord",
    "UWGRefresher",
    "RefreshResult",
]
