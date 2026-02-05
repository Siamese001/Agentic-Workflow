"""
CST-based Canon Healing Tests

Tests that the CodeHealerAgent correctly performs canon healing operations
using CST-based transformers while preserving comments and formatting.
"""

import ast
import tempfile
from datetime import datetime
from pathlib import Path

import libcst as cst
import pytest

from agentic_core.L5_safety.validators.cst_transformers import (
    DocstringTarget,
    SurgicalBareExceptFixer,
    SurgicalDocstringInserter,
    SurgicalFutureImportInserter,
)
from agentic_core.L5_safety.validators.surgical_context import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from agentic_core.L5_safety.validators.surgical_cst_healer_mixin import (
    SurgicalCSTHealerMixin,
)


class TestCanonHealingCST:
    """Test CST-based canon healing operations."""

    def test_future_import_insertion(self):
        """Test that __future__ import is correctly inserted."""
        source_code = """# Module comment
import os

def test():
    return os.getcwd()
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            coordinate = ASTCoordinate(
                line=1,
                column=0,
                node_id="missing_future_import",
                node_type="Module",
            )
            violation = ViolationConstraint(
                constraint_type="missing_future_import",
                severity="warning",
                message="Missing __future__ annotations import",
                fix_type="insert",
            )
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="future_import_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert "from __future__ import annotations" in healed_content
            assert "# Module comment" in healed_content
            assert "import os" in healed_content
            assert "def test():" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

        finally:
            temp_path.unlink()

    def test_bare_except_fix(self):
        """Test that bare except clauses are correctly fixed."""
        source_code = """# Important comment
def risky():
    try:
        x = 1 / 0
    except:
        pass
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            coordinate = ASTCoordinate(
                line=5,
                column=0,
                node_id="bare_except_5",
                node_type="ExceptHandler",
            )
            violation = ViolationConstraint(
                constraint_type="bare_except",
                severity="warning",
                message="Bare except clause at line 5",
                fix_type="replace",
            )
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="bare_except_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert "except Exception:" in healed_content
            assert "except:" not in healed_content
            assert "# Important comment" in healed_content
            assert "def risky():" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

        finally:
            temp_path.unlink()

    def test_docstring_insertion_class(self):
        """Test that docstrings are correctly inserted into classes."""
        source_code = """# Module comment
class MyClass:
    # This comment must stay
    def method(self):
        pass
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            coordinate = ASTCoordinate(
                line=2,
                column=0,
                node_id="class_MyClass",
                node_type="ClassDef",
            )
            violation = ViolationConstraint(
                constraint_type="missing_docstring",
                severity="warning",
                message="Class MyClass missing docstring",
                fix_type="insert",
            )
            violation.target_coordinate = coordinate

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="docstring_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert '"""' in healed_content  # Docstring added
            assert "# Module comment" in healed_content
            assert "# This comment must stay" in healed_content
            assert "class MyClass:" in healed_content
            assert "def method(self):" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

        finally:
            temp_path.unlink()

    def test_combined_canon_fixes(self):
        """Test multiple canon fixes at once."""
        source_code = """# Header comment
import os

class MyClass:
    def risky(self):
        try:
            x = 1 / 0
        except:
            pass
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            violations = []
            coordinates = []

            # Future import violation
            coord1 = ASTCoordinate(line=1, column=0, node_id="missing_future", node_type="Module")
            viol1 = ViolationConstraint(
                constraint_type="missing_future_import",
                severity="warning",
                message="Missing __future__ import",
                fix_type="insert",
            )
            viol1.target_coordinate = coord1
            violations.append(viol1)
            coordinates.append(coord1)

            # Bare except violation
            coord2 = ASTCoordinate(
                line=8, column=0, node_id="bare_except_8", node_type="ExceptHandler"
            )
            viol2 = ViolationConstraint(
                constraint_type="bare_except",
                severity="warning",
                message="Bare except at line 8",
                fix_type="replace",
            )
            viol2.target_coordinate = coord2
            violations.append(viol2)
            coordinates.append(coord2)

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=violations,
                target_coordinates=coordinates,
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="combined_canon_test",
            )

            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Assertions
            assert "from __future__ import annotations" in healed_content
            assert "except Exception:" in healed_content
            assert "except:" not in healed_content
            assert "# Header comment" in healed_content
            assert "import os" in healed_content
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 2

        finally:
            temp_path.unlink()

    def test_preserves_existing_future_import(self):
        """Test that existing __future__ imports are not duplicated."""
        source_code = """from __future__ import annotations
# Comment after future import
import os
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            tree = ast.parse(source_code)

            # No violations - just testing that nothing breaks
            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[],
                target_coordinates=[],
                detector_agent="CodeHealerAgent",
                detection_method="heal_canon",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="no_violations",
            )

            healer = SurgicalCSTHealerMixin()
            healer.heal_surgical_cst(context)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Should be unchanged
            assert healed_content == source_code
            assert healed_content.count("from __future__") == 1

        finally:
            temp_path.unlink()


class TestDocstringInserterUnit:
    """Unit tests for SurgicalDocstringInserter transformer."""

    def test_class_docstring_insertion(self):
        """Test direct use of docstring inserter on class."""
        source = """class TestClass:
    def method(self):
        pass
"""
        cst_tree = cst.parse_module(source)

        target = DocstringTarget(
            line_number=1,
            name="TestClass",
            node_type="class",
            docstring='"""Test class docstring."""',
        )

        inserter = SurgicalDocstringInserter([target])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert '"""Test class docstring."""' in result
        assert inserter.modifications_made == 1

    def test_function_docstring_insertion(self):
        """Test direct use of docstring inserter on function."""
        source = """def test_func():
    return 42
"""
        cst_tree = cst.parse_module(source)

        target = DocstringTarget(
            line_number=1,
            name="test_func",
            node_type="function",
            docstring='"""Test function docstring."""',
        )

        inserter = SurgicalDocstringInserter([target])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert '"""Test function docstring."""' in result
        assert inserter.modifications_made == 1

    def test_skips_existing_docstring(self):
        """Test that existing docstrings are not duplicated."""
        source = '''class TestClass:
    """Existing docstring."""
    def method(self):
        pass
'''
        cst_tree = cst.parse_module(source)

        target = DocstringTarget(
            line_number=1,
            name="TestClass",
            node_type="class",
        )

        inserter = SurgicalDocstringInserter([target])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        # Should be unchanged
        assert result == source
        assert inserter.modifications_made == 0


class TestBareExceptFixerUnit:
    """Unit tests for SurgicalBareExceptFixer transformer."""

    def test_fixes_bare_except(self):
        """Test direct use of bare except fixer."""
        source = """try:
    x = 1
except:
    pass
"""
        cst_tree = cst.parse_module(source)

        fixer = SurgicalBareExceptFixer(fix_all=True)
        modified_tree = cst_tree.visit(fixer)
        result = modified_tree.code

        assert "except Exception:" in result
        assert "except:" not in result.replace("except Exception:", "")
        assert fixer.modifications_made == 1

    def test_skips_typed_except(self):
        """Test that typed except clauses are not modified."""
        source = """try:
    x = 1
except ValueError:
    pass
"""
        cst_tree = cst.parse_module(source)

        fixer = SurgicalBareExceptFixer(fix_all=True)
        modified_tree = cst_tree.visit(fixer)
        result = modified_tree.code

        # Should be unchanged
        assert result == source
        assert fixer.modifications_made == 0


class TestFutureImportInserterUnit:
    """Unit tests for SurgicalFutureImportInserter transformer."""

    def test_inserts_future_import(self):
        """Test direct use of future import inserter."""
        source = """import os

def test():
    pass
"""
        cst_tree = cst.parse_module(source)

        inserter = SurgicalFutureImportInserter(["annotations"])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert "from __future__ import annotations" in result
        assert inserter.modifications_made == 1
        # Future import should come before other imports
        lines = result.split("\n")
        future_idx = next(i for i, line in enumerate(lines) if "__future__" in line)
        os_idx = next(i for i, line in enumerate(lines) if "import os" in line)
        assert future_idx < os_idx

    def test_skips_existing_future_import(self):
        """Test that existing future imports are not duplicated."""
        source = """from __future__ import annotations

import os
"""
        cst_tree = cst.parse_module(source)

        inserter = SurgicalFutureImportInserter(["annotations"])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        # Should be unchanged
        assert result == source
        assert inserter.modifications_made == 0

    def test_respects_module_docstring(self):
        """Test that future import is inserted after module docstring."""
        source = '''"""Module docstring."""

import os
'''
        cst_tree = cst.parse_module(source)

        inserter = SurgicalFutureImportInserter(["annotations"])
        modified_tree = cst_tree.visit(inserter)
        result = modified_tree.code

        assert "from __future__ import annotations" in result
        # Future import should come after docstring
        lines = result.split("\n")
        docstring_idx = next(i for i, line in enumerate(lines) if '"""Module' in line)
        future_idx = next(i for i, line in enumerate(lines) if "__future__" in line)
        assert future_idx > docstring_idx


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
