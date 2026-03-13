"""G-16-14: Lineage chain validator for System Learning versioned ChangePackages.

Validates:
  - Parent version exists (except genesis)
  - No cycles (DAG structure enforced)
  - Lineage chain integrity
"""

from __future__ import annotations


class LineageValidationError(Exception):
    """Base exception for lineage validation failures."""


class ParentNotFound(LineageValidationError):
    """Raised when parent version does not exist."""


class CycleDetected(LineageValidationError):
    """Raised when a cycle is detected in the lineage chain."""


class LineageValidator:
    """Validates lineage chain integrity for versioned ChangePackages.

    Enforces:
      - Parent version exists (except genesis)
      - No cycles (DAG structure)
      - Lineage chain is well-formed
    """

    def __init__(self, version_store) -> None:
        """Initialize validator with a version store.

        Parameters
        ----------
        version_store
            A version store implementing get_change_package(version_id).
        """
        self._store = version_store

    def validate_lineage(self, version_id: str) -> None:
        """Validate the lineage chain for a version.

        Parameters
        ----------
        version_id : str
            The version_id to validate.

        Raises
        ------
        ParentNotFound
            If a parent version does not exist.
        CycleDetected
            If a cycle is detected in the lineage chain.
        """
        visited: set[str] = set()
        current = version_id
        while current is not None:
            if current in visited:
                raise CycleDetected(f"CYCLE_DETECTED: version {current!r} appears twice in lineage chain")
            visited.add(current)
            try:
                pkg = self._store.get_change_package(current)
            except Exception as e:
                raise ParentNotFound(f"PARENT_NOT_FOUND: version {current!r} does not exist") from e
            current = pkg.parent_version_id
            if current is not None:
                try:
                    self._store.get_change_package(current)
                except Exception as e:
                    raise ParentNotFound(
                        f"PARENT_NOT_FOUND: parent version {current!r} does not exist"
                    ) from e

    def validate_chain(self, version_id: str) -> list[str]:
        """Validate and return the full lineage chain.

        Parameters
        ----------
        version_id : str
            The version_id to start from.

        Returns
        -------
        list[str]
            Ordered list of version_ids from genesis to current (inclusive).

        Raises
        ------
        ParentNotFound
            If a parent version does not exist.
        CycleDetected
            If a cycle is detected.
        """
        self.validate_lineage(version_id)
        chain: list[str] = []
        current = version_id
        while current is not None:
            chain.append(current)
            pkg = self._store.get_change_package(current)
            current = pkg.parent_version_id
        return list(reversed(chain))
