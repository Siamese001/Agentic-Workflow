"""ADG Identity Normalizer — classify and resolve every imported name.

Produces an explicit IdentityRecord for each name rather than silently
collapsing unresolved imports into null nodes. Every null-file node in the
old dep_graph_db output maps to one of the five IdentityKind categories.

Identity kinds:
  repo_module          — file exists in repo at the resolved path
  package_container    — dotted name resolves to a package directory (no .py)
  external_module      — top-level package not under any SSOT root
  unresolved_import    — claimed to be internal but no file or package found
  inferred_symbol      — class/function name inferred from parent module import

Design constraints:
  - No silent swallowing: every name gets a kind and a reason
  - Deterministic: same set of names always produces same output (sorted keys)
  - No duplication of L5 classification or territory logic
  - Confidence labels: HIGH, MEDIUM, LOW
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SSOT root prefixes (mirrors LAYER_PREFIXES in schema.py without duplication)
# — only the root-level dirs used to determine if an import is "internal"
# ---------------------------------------------------------------------------
_INTERNAL_ROOTS: frozenset[str] = frozenset(
    [
        "agentic_core",
        "apps_lic",
        "apps_rg",
        "apps_shared",
        "system_learning",
        "tools",
        "tests",
        "ops_scripts",
    ]
)


class IdentityKind(str, Enum):
    """Canonical identity category for an imported name."""

    REPO_MODULE = "repo_module"
    PACKAGE_CONTAINER = "package_container"
    EXTERNAL_MODULE = "external_module"
    UNRESOLVED_IMPORT = "unresolved_import"
    INFERRED_SYMBOL = "inferred_symbol"


class IdentityConfidence(str, Enum):
    """Confidence in the identity resolution."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class IdentityRecord:
    """Fully-resolved identity for one imported name.

    Attributes
    ----------
    raw_name:
        The original dot-notation import name (e.g. ``agentic_core.L0_routing.config``).
    kind:
        Canonical identity category.
    confidence:
        HIGH / MEDIUM / LOW based on resolution method.
    resolved_path:
        Repo-relative forward-slash path if kind is REPO_MODULE or PACKAGE_CONTAINER,
        else empty string.
    reason:
        Human-readable explanation of the classification decision.
    adg_name:
        Canonical ADG:: name (e.g. ``ADG::Module::agentic_core/L0_routing/config/__init__.py``).
    """

    raw_name: str
    kind: IdentityKind
    confidence: IdentityConfidence
    resolved_path: str = ""
    reason: str = ""
    adg_name: str = ""


@dataclass
class NormalizationReport:
    """Aggregate statistics from a normalization run."""

    total: int = 0
    by_kind: dict[str, int] = field(default_factory=dict)
    by_confidence: dict[str, int] = field(default_factory=dict)
    unresolved: list[str] = field(default_factory=list)
    inferred_symbols: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "by_kind": dict(sorted(self.by_kind.items())),
            "by_confidence": dict(sorted(self.by_confidence.items())),
            "unresolved_count": len(self.unresolved),
            "unresolved_names": sorted(self.unresolved),
            "inferred_symbol_count": len(self.inferred_symbols),
            "inferred_symbol_names": sorted(self.inferred_symbols),
        }


class IdentityNormalizer:
    """Resolve dot-notation import names to IdentityRecords.

    Usage
    -----
    normalizer = IdentityNormalizer(repo_root=Path("."))
    record = normalizer.normalize("agentic_core.L0_routing.config")
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._cache: dict[str, IdentityRecord] = {}
        self._known_files: frozenset[str] | None = None

    def _get_known_files(self) -> frozenset[str]:
        """Build a forward-slash repo-relative path set for all .py files."""
        if self._known_files is None:
            paths = set()
            for p in self._repo_root.rglob("*.py"):
                try:
                    rel = p.relative_to(self._repo_root).as_posix()
                    paths.add(rel)
                except ValueError:
                    pass
            self._known_files = frozenset(paths)
        return self._known_files

    @staticmethod
    def _dot_to_path(dot_name: str) -> str:
        """Convert dot-notation to forward-slash relative path (no .py suffix)."""
        return dot_name.replace(".", "/")

    def normalize(self, raw_name: str) -> IdentityRecord:
        """Resolve one dot-notation import name to an IdentityRecord.

        Resolution order:
          1. Cache hit
          2. External module check (top-level not in _INTERNAL_ROOTS)
          3. Direct .py file match
          4. Package __init__.py match
          5. Package directory match (no __init__.py)
          6. Inferred symbol (parent resolves but final segment is a class/fn name)
          7. Unresolved import
        """
        if raw_name in self._cache:
            return self._cache[raw_name]

        record = self._resolve(raw_name)
        self._cache[raw_name] = record
        return record

    def _resolve(self, raw_name: str) -> IdentityRecord:
        from agentic_core.adg.schema import canonical_name

        parts = raw_name.split(".")
        top_level = parts[0] if parts else ""

        # Step 2: External module
        if top_level not in _INTERNAL_ROOTS:
            adg = canonical_name("Symbol", raw_name)
            return IdentityRecord(
                raw_name=raw_name,
                kind=IdentityKind.EXTERNAL_MODULE,
                confidence=IdentityConfidence.HIGH,
                resolved_path="",
                reason=f"Top-level '{top_level}' not in internal roots",
                adg_name=adg,
            )

        slash_path = self._dot_to_path(raw_name)
        known = self._get_known_files()

        # Step 3: Direct .py file match
        candidate_py = slash_path + ".py"
        if candidate_py in known:
            adg = canonical_name("Module", candidate_py)
            return IdentityRecord(
                raw_name=raw_name,
                kind=IdentityKind.REPO_MODULE,
                confidence=IdentityConfidence.HIGH,
                resolved_path=candidate_py,
                reason="Direct .py file match",
                adg_name=adg,
            )

        # Step 4: Package __init__.py match
        # guardian: allow-path-string
        candidate_init = slash_path + "/__init__.py"
        if candidate_init in known:
            adg = canonical_name("Module", candidate_init)
            return IdentityRecord(
                raw_name=raw_name,
                kind=IdentityKind.PACKAGE_CONTAINER,
                confidence=IdentityConfidence.HIGH,
                resolved_path=candidate_init,
                reason="Package __init__.py found",
                adg_name=adg,
            )

        # Step 5: Package directory match (directory exists, no __init__.py)
        pkg_dir = self._repo_root / Path(slash_path)
        if pkg_dir.is_dir():
            adg = canonical_name("Module", slash_path)
            return IdentityRecord(
                raw_name=raw_name,
                kind=IdentityKind.PACKAGE_CONTAINER,
                confidence=IdentityConfidence.MEDIUM,
                resolved_path=slash_path,
                reason="Directory exists but no __init__.py",
                adg_name=adg,
            )

        # Step 6: Inferred symbol — parent resolves, last segment is class/fn
        if len(parts) >= 2:
            parent_name = ".".join(parts[:-1])
            parent_record = self.normalize(parent_name)
            if parent_record.kind in (
                IdentityKind.REPO_MODULE,
                IdentityKind.PACKAGE_CONTAINER,
            ):
                symbol_name = parts[-1]
                adg = canonical_name("Symbol", raw_name)
                return IdentityRecord(
                    raw_name=raw_name,
                    kind=IdentityKind.INFERRED_SYMBOL,
                    confidence=IdentityConfidence.MEDIUM,
                    resolved_path=parent_record.resolved_path,
                    reason=f"Parent '{parent_name}' resolves; '{symbol_name}' inferred as symbol",
                    adg_name=adg,
                )

        # Step 7: Unresolved import
        adg = canonical_name("Symbol", raw_name)
        return IdentityRecord(
            raw_name=raw_name,
            kind=IdentityKind.UNRESOLVED_IMPORT,
            confidence=IdentityConfidence.LOW,
            resolved_path="",
            reason=f"No file, package, or resolvable parent found for '{raw_name}'",
            adg_name=adg,
        )

    def normalize_many(self, raw_names: list[str]) -> dict[str, IdentityRecord]:
        """Normalize a list of names, returning a deterministically-ordered dict."""
        return {name: self.normalize(name) for name in sorted(set(raw_names))}

    def report(self, records: dict[str, IdentityRecord]) -> NormalizationReport:
        """Produce aggregate statistics over a set of resolved records."""
        rpt = NormalizationReport(total=len(records))
        for rec in records.values():
            kind_key = rec.kind.value
            rpt.by_kind[kind_key] = rpt.by_kind.get(kind_key, 0) + 1
            conf_key = rec.confidence.value
            rpt.by_confidence[conf_key] = rpt.by_confidence.get(conf_key, 0) + 1
            if rec.kind == IdentityKind.UNRESOLVED_IMPORT:
                rpt.unresolved.append(rec.raw_name)
            elif rec.kind == IdentityKind.INFERRED_SYMBOL:
                rpt.inferred_symbols.append(rec.raw_name)
        rpt.unresolved.sort()
        rpt.inferred_symbols.sort()
        return rpt

    def normalize_from_scan_result(
        self, result: object
    ) -> tuple[dict[str, IdentityRecord], NormalizationReport]:
        """Normalize all imported names found in a ScanResult.

        Only normalizes ADG::Symbol:: targets — these represent external,
        unresolved, or inferred names that require identity classification.
        ADG::Module:: names are already resolved repo paths and are skipped.

        Returns (records_dict, report).
        """
        raw_names: set[str] = set()

        symbol_prefix = "ADG::Symbol::"

        for edge in getattr(result, "edges", []):
            to_name: str = edge.to_name

            if to_name.startswith(symbol_prefix):
                dot_name = to_name[len(symbol_prefix) :]
                raw_names.add(dot_name)

        records = self.normalize_many(list(raw_names))
        rpt = self.report(records)
        return records, rpt


def normalize_identity(
    raw_name: str,
    repo_root: Path | None = None,
) -> IdentityRecord:
    """Module-level convenience function for single-name normalization."""
    normalizer = IdentityNormalizer(repo_root=repo_root)
    return normalizer.normalize(raw_name)


def build_identity_index(
    dot_names: list[str],
    repo_root: Path | None = None,
) -> tuple[dict[str, IdentityRecord], NormalizationReport]:
    """Build and report on a full identity index for a list of dot-notation names."""
    normalizer = IdentityNormalizer(repo_root=repo_root)
    records = normalizer.normalize_many(dot_names)
    report = normalizer.report(records)
    return records, report


__all__ = [
    "IdentityKind",
    "IdentityConfidence",
    "IdentityRecord",
    "NormalizationReport",
    "IdentityNormalizer",
    "normalize_identity",
    "build_identity_index",
]
