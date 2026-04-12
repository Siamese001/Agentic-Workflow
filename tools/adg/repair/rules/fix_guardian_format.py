"""AUTO_FIX rule: Correct guardian comment format.

Reuses and wraps the existing adg_antipattern_fixer.py logic to
auto-correct non-canonical guardian comment formats.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.adg.repair.base_rule import BaseRepairRule
from tools.adg.repair.rule_engine import repair_rule
from tools.adg.repair.types import Deficiency, FixCategory, FixResult


@repair_rule("fix_guardian_format", priority=20)
class FixGuardianFormatRule(BaseRepairRule):
    """Fixes non-canonical guardian comment formats.

    Canonical format:
        # guardian: allow-<type> -- <justification>

    Non-canonical forms auto-corrected:
        - Missing colon after 'guardian'
        - Wrong separator (-- vs :)
        - Wrong case (Guardian vs guardian)
        - Underscore type (allow_magic_config vs allow-magic-config)
        - camelCase type (allowMagicConfig vs allow-magic-config)
        - Missing space after --

    Safety: High - only changes comment format, not code semantics
    """

    rule_name = "Fix Guardian Format"
    rule_description = "Corrects non-canonical guardian comment formats"
    rule_priority = 20

    # Issue types this rule can handle
    HANDLED_ISSUES = {
        "guardian_format",
        "non_canonical_guardian",
    }

    # Canonical type registry
    CANONICAL_TYPES: dict[str, str] = {
        # magic-config
        "magic-config": "magic-config",
        "magic_config": "magic-config",
        "magicconfig": "magic-config",
        # silent-swallower
        "silent-swallower": "silent-swallower",
        "silent_swallower": "silent-swallower",
        "silentswallower": "silent-swallower",
        # global-mutation
        "global-mutation": "global-mutation",
        "global_mutation": "global-mutation",
        "globalmutation": "global-mutation",
        # bare-except
        "bare-except": "bare-except",
        "bare_except": "bare-except",
        "bareexcept": "bare-except",
        # broad-exception-catch
        "broad-exception-catch": "broad-exception-catch",
        "broad_exception_catch": "broad-exception-catch",
        "broadexceptioncatch": "broad-exception-catch",
        # log-and-swallow
        "log-and-swallow": "log-and-swallow",
        "log_and_swallow": "log-and-swallow",
        "logandswallow": "log-and-swallow",
        # return-none-swallow
        "return-none-swallow": "return-none-swallow",
        "return_none_swallow": "return-none-swallow",
        "returnnoneswallow": "return-none-swallow",
        # os-path
        "os-path": "os-path",
        "os_path": "os-path",
        # string-path-concat
        "string-path-concat": "string-path-concat",
        "string_path_concat": "string-path-concat",
        # silent-degradation
        "silent-degradation": "silent-degradation",
        "silent_degradation": "silent-degradation",
        "silentdegradation": "silent-degradation",
        # availability-guard-skip
        "availability-guard-skip": "availability-guard-skip",
        "availability_guard_skip": "availability-guard-skip",
        "availabilityguardskip": "availability-guard-skip",
        # silent-success-on-noop
        "silent-success-on-noop": "silent-success-on-noop",
        "silent_success_on_noop": "silent-success-on-noop",
        "silentsuccessonnoop": "silent-success-on-noop",
        # phantom-module-import
        "phantom-module-import": "phantom-module-import",
        "phantom_module_import": "phantom-module-import",
        "phantommoduleimport": "phantom-module-import",
        # except-import-pass
        "except-import-pass": "except-import-pass",
        "except_import_pass": "except-import-pass",
        "exceptimportpass": "except-import-pass",
        # log-and-return-mock
        "log-and-return-mock": "log-and-return-mock",
        "log_and_return_mock": "log-and-return-mock",
        "logandreturnmock": "log-and-return-mock",
        # skip-string-return
        "skip-string-return": "skip-string-return",
        "skip_string_return": "skip-string-return",
        "skipstringreturn": "skip-string-return",
    }

    # Detection regex for non-canonical guardian lines
    GUARDIAN_DETECT_RE = re.compile(
        r"""
        ^(\s*\#\s*)          # indent + hash prefix (group 1)
        [Gg]uardian          # keyword (case-insensitive first letter)
        \s*:?\s*             # optional colon
        (allow[-_a-zA-Z0-9]*)  # allow-<type> chunk (group 2)
        \s*(?:--|:)\s*       # separator: -- or :
        (.*)                 # justification (group 3)
        $
        """,
        re.VERBOSE,
    )

    # Pattern that matches ALREADY CANONICAL lines (no change needed)
    CANONICAL_RE = re.compile(
        r"^\s*#\s*guardian:\s+allow-[a-z][a-z0-9-]+\s+--\s+\S.*$",
    )

    def match(self, deficiency: Deficiency) -> bool:
        """Check if this rule applies."""
        return deficiency.category == FixCategory.AUTO_FIX and deficiency.issue_type in self.HANDLED_ISSUES

    def can_fix(self, deficiency: Deficiency) -> tuple[bool, str]:
        """Determine if fix can be applied."""
        file_path = deficiency.file_path

        if file_path == "ADG_METADATA":
            return False, "Cannot fix ADG metadata"

        if not file_path.endswith(".py"):
            return False, "Not a Python file"

        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"

        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return False, f"Cannot read file: {e}"

        # Check for non-canonical guardian lines
        has_fixable = False
        for line in content.split("\n"):
            if self._is_non_canonical(line):
                has_fixable = True
                break

        if not has_fixable:
            return False, "No non-canonical guardian comments found"

        return True, "Can fix guardian formats"

    def apply_fix(self, deficiency: Deficiency) -> FixResult:
        """Apply the fix by correcting guardian comment formats."""
        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            original_content = path.read_text(encoding="utf-8")
            lines = original_content.split("\n")

            new_lines = []
            changes_made = 0

            for line in lines:
                if self._is_canonical(line):
                    # Already canonical, keep as-is
                    new_lines.append(line)
                elif self._is_non_canonical(line):
                    # Fix the line
                    fixed_line = self._fix_line(line)
                    new_lines.append(fixed_line)
                    if fixed_line != line:
                        changes_made += 1
                else:
                    # Not a guardian line, keep as-is
                    new_lines.append(line)

            if changes_made == 0:
                return FixResult(
                    deficiency_id=deficiency.id,
                    success=False,
                    error_message="No changes needed or could be made",
                )

            new_content = "\n".join(new_lines)
            path.write_text(new_content, encoding="utf-8")

            return FixResult(
                deficiency_id=deficiency.id,
                success=True,
                original_content=original_content,
                new_content=new_content,
            )

        except Exception as e:
            return FixResult(
                deficiency_id=deficiency.id,
                success=False,
                error_message=str(e),
            )

    def verify_fix(self, deficiency: Deficiency, result: FixResult) -> bool:
        """Verify that guardian formats were corrected."""
        if not result.success:
            return False

        file_path = deficiency.file_path
        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")

            # Check that no non-canonical guardian lines remain
            for line in content.split("\n"):
                if self._is_non_canonical(line):
                    return False

            return True

        except Exception:
            return False

    def _is_canonical(self, line: str) -> bool:
        """Check if line is already in canonical format."""
        return bool(self.CANONICAL_RE.match(line))

    def _is_non_canonical(self, line: str) -> bool:
        """Check if line looks like a non-canonical guardian comment."""
        if self._is_canonical(line):
            return False
        return bool(self.GUARDIAN_DETECT_RE.match(line))

    def _fix_line(self, line: str) -> str:
        """Fix a non-canonical guardian comment line."""
        match = self.GUARDIAN_DETECT_RE.match(line)
        if not match:
            return line

        indent = match.group(1)  # Includes '# '
        raw_type = match.group(2)
        justification = match.group(3).strip()

        # Normalize the type
        canonical_type = self._normalize_type(raw_type)

        # Reconstruct the line in canonical format
        return f"{indent}guardian: {canonical_type} -- {justification}"

    def _normalize_type(self, raw: str) -> str:
        """Normalize a raw allow-<type> token to canonical kebab form."""
        lowered = raw.lower().strip("-_ ")

        # Strip leading 'allow' prefix
        if lowered.startswith("allow-"):
            inner = lowered[len("allow-") :]
        elif lowered.startswith("allow_"):
            inner = lowered[len("allow_") :]
        elif lowered.startswith("allow"):
            inner_raw = raw[len("allow") :].lstrip("-_ ")
            inner = self._camel_to_kebab(inner_raw) if inner_raw else ""
        else:
            inner = self._camel_to_kebab(lowered)

        # Normalize inner to kebab
        inner = inner.replace("_", "-")
        inner = re.sub(r"-+", "-", inner).strip("-")

        # Lookup canonical form
        if inner in self.CANONICAL_TYPES:
            return f"allow-{self.CANONICAL_TYPES[inner]}"

        # Return best-effort
        return f"allow-{inner}" if inner else "allow-unknown"

    def _camel_to_kebab(self, name: str) -> str:
        """Convert camelCase or PascalCase to lowercase-kebab-case."""
        s = re.sub(r"([A-Z])", r"-\1", name).lower()
        s = s.replace("_", "-")
        s = re.sub(r"-+", "-", s)
        return s.strip("-")
