"""Unit tests for shared complexity analyzer.

Tests for agentic_core.L4_state.utils.complexity_analyzer
"""

import ast


from agentic_core.L4_state.utils.complexity_analyzer import (
    analyze_file_complexity,
    calculate_mccabe_complexity,
    check_function_complexity,
)


class TestCalculateMcCabeComplexity:
    """Tests for McCabe complexity calculation."""

    def test_simple_function_complexity_1(self):
        """Simple function with no branches should have complexity 1."""
        code = "def simple(): return 1"
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 1

    def test_if_statement_adds_complexity(self):
        """Each if statement adds 1 to complexity."""
        code = """
def with_if(x):
    if x > 0:
        return 1
    return 0
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 2

    def test_for_loop_adds_complexity(self):
        """Each for loop adds 1 to complexity."""
        code = """
def with_for(items):
    for item in items:
        print(item)
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 2

    def test_while_loop_adds_complexity(self):
        """Each while loop adds 1 to complexity."""
        code = """
def with_while(x):
    while x > 0:
        x -= 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 2

    def test_nested_loops_add_complexity(self):
        """Nested loops each add to complexity."""
        code = """
def nested(items):
    for i in items:
        for j in items:
            if i == j:
                continue
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 4  # 1 + for + for + if

    def test_boolean_operators_add_complexity(self):
        """Boolean operators add n-1 to complexity."""
        code = """
def bool_ops(a, b, c):
    if a and b and c:
        return True
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 4  # 1 + if + (and + and)

    def test_except_handler_adds_complexity(self):
        """Each except handler adds 1 to complexity."""
        code = """
def with_try(x):
    try:
        return int(x)
    except ValueError:
        return 0
    except TypeError:
        return -1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 3  # 1 + except + except

    def test_elif_chain_adds_complexity(self):
        """Each elif adds to complexity."""
        code = """
def with_elif(x):
    if x > 100:
        return "big"
    elif x > 10:
        return "medium"
    elif x > 0:
        return "small"
    else:
        return "zero"
"""
        tree = ast.parse(code)
        func = tree.body[0]
        # 1 + if + elif + elif = 4
        assert calculate_mccabe_complexity(func) == 4

    def test_or_operator_adds_complexity(self):
        """Or operator adds n-1 to complexity."""
        code = """
def with_or(a, b, c):
    if a or b or c:
        return True
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 4  # 1 + if + (or + or)

    def test_async_function_same_as_sync(self):
        """Async functions should calculate complexity the same way."""
        code = """
async def async_func(x):
    if x > 0:
        for i in range(x):
            pass
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 3  # 1 + if + for


class TestCheckFunctionComplexity:
    """Tests for complexity threshold checking."""

    def test_check_function_complexity_pass(self):
        """Function under threshold should pass."""
        code = "def simple(): return 1"
        tree = ast.parse(code)
        func = tree.body[0]
        passed, complexity = check_function_complexity(func, max_complexity=10)
        assert passed is True
        assert complexity == 1

    def test_check_function_complexity_fail(self):
        """Function over threshold should fail."""
        code = """
def complex_func(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return "big"
"""
        tree = ast.parse(code)
        func = tree.body[0]
        passed, complexity = check_function_complexity(func, max_complexity=2)
        assert passed is False
        assert complexity == 4

    def test_check_function_complexity_at_threshold(self):
        """Function at exactly the threshold should pass."""
        code = """
def at_threshold(x):
    if x > 0:
        return 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        passed, complexity = check_function_complexity(func, max_complexity=2)
        assert passed is True
        assert complexity == 2

    def test_default_threshold_is_10(self):
        """Default max_complexity should be 10."""
        code = "def simple(): return 1"
        tree = ast.parse(code)
        func = tree.body[0]
        passed, _ = check_function_complexity(func)
        assert passed is True


class TestAnalyzeFileComplexity:
    """Tests for file-level complexity analysis."""

    def test_analyze_file_with_violations(self, tmp_path):
        """Should detect complexity violations in file."""
        test_file = tmp_path / "complex.py"
        test_file.write_text("""
def simple():
    return 1

def complex_func(x):
    if x > 0:
        if x > 10:
            if x > 100:
                for i in range(x):
                    while i > 0:
                        i -= 1
""")
        violations = analyze_file_complexity(str(test_file), max_complexity=3)

        # simple() has complexity 1, should not be in violations
        # complex_func() has complexity 6, should be in violations
        assert len(violations) == 1
        assert violations[0]["function_name"] == "complex_func"
        assert violations[0]["complexity"] == 6

    def test_analyze_file_no_violations(self, tmp_path):
        """Should return empty list when no violations."""
        test_file = tmp_path / "simple.py"
        test_file.write_text("""
def func1():
    return 1

def func2(x):
    if x:
        return 2
    return 0
""")
        violations = analyze_file_complexity(str(test_file), max_complexity=10)
        assert len(violations) == 0

    def test_analyze_nonexistent_file(self):
        """Should handle nonexistent file gracefully."""
        violations = analyze_file_complexity("/nonexistent/path.py")
        assert violations == []

    def test_analyze_file_with_syntax_error(self, tmp_path):
        """Should handle syntax errors gracefully."""
        test_file = tmp_path / "bad_syntax.py"
        test_file.write_text("def broken(")
        violations = analyze_file_complexity(str(test_file))
        assert violations == []
