import pytest
import ast
from pathlib import Path

# MANDATORY: No Path Shield needed as we test logic functions directly
@pytest.fixture
def disable_path_shield(): return True

def test_ast_detection_logic(tmp_path):
    """Verify the scanner correctly identifies matching classes."""
    from ops_scripts.phase3_deep_scan import check_file_content
    
    # Case 1: Match (Keep)
    f1 = tmp_path / "MyClass.py"
    f1.write_text("import os\nclass MyClass:\n    pass", encoding='utf-8')
    assert check_file_content(f1) == "KEEP"
    
    # Case 2: Mismatch (Rename)
    f2 = tmp_path / "MyScript.py"
    f2.write_text("def run_script():\n    pass", encoding='utf-8')
    assert check_file_content(f2) == "RENAME"
    
    # Case 3: Nested/Decorated (Keep)
    # The AST walker should find classes even if decorated or nested
    f3 = tmp_path / "ComplexEntity.py"
    f3.write_text("@dataclass\nclass ComplexEntity:\n    pass", encoding='utf-8')
    assert check_file_content(f3) == "KEEP"

def test_snake_case_conversion():
    from ops_scripts.phase3_deep_scan import to_snake_case
    assert to_snake_case("dag_executor_basic.py") == "dag_executor_basic.py"
    assert to_snake_case("l4_types.py") == "l4_types.py"
