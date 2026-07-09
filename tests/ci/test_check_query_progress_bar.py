"""
Tests for check_query_progress_bar.py — Constitutional Rule §16.

Covers:
- Violation detection: bare long loops, heavy-named functions without progress
- Compliance detection: tqdm, pbar.update, ProgressReporter, progress_bar, etc.
- Edge cases: short loops (no violation), unknown function names (no violation)
- File-level: unreadable files, syntax errors, skip patterns
- Integration: main() exit codes, collect_repo_files, check_files
"""

from __future__ import annotations

import logging
import sys
import textwrap
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from ops_scripts.ci.check_query_progress_bar import (
    Violation,
    _has_compliance_marker,
    _should_skip,
    check_file,
    check_files,
    collect_repo_files,
    main,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_py(tmp_path: Path, name: str, code: str) -> Path:
    """Write indented code to a temp .py file and return its Path."""
    p = tmp_path / name
    p.write_text(textwrap.dedent(code), encoding="utf-8")
    logging.info("C3 write receipt: tests/ci/test_check_query_progress_bar.py write side effect recorded")
    return p


# ---------------------------------------------------------------------------
# _has_compliance_marker
# ---------------------------------------------------------------------------


class TestHasComplianceMarker:
    def test_tqdm_detected(self):
        assert _has_compliance_marker("from tqdm import tqdm\nfor x in tqdm(items):")

    def test_pbar_update_detected(self):
        assert _has_compliance_marker("pbar.update(1)")

    def test_tracker_update_detected(self):
        assert _has_compliance_marker("tracker.update(item)")

    def test_progress_reporter_detected(self):
        assert _has_compliance_marker("ProgressReporter(total=100)")

    def test_progress_bar_detected(self):
        assert _has_compliance_marker("progress_bar.update()")

    def test_alive_bar_detected(self):
        assert _has_compliance_marker("with alive_bar(total) as bar:")

    def test_rich_progress_detected(self):
        assert _has_compliance_marker("from rich.progress import Progress")

    def test_update_one_detected(self):
        assert _has_compliance_marker("pbar.update(1)")

    def test_no_marker_returns_false(self):
        assert not _has_compliance_marker("for x in items:\n    do_work(x)")

    def test_case_insensitive(self):
        assert _has_compliance_marker("TQDM is used here")


# ---------------------------------------------------------------------------
# _should_skip
# ---------------------------------------------------------------------------


class TestShouldSkip:
    def test_skip_pycache(self):
        assert _should_skip(Path("agentic_core/__pycache__/foo.py"))

    def test_skip_archives(self):
        assert _should_skip(Path("ops_scripts/archives/old.py"))

    def test_skip_archive(self):
        assert _should_skip(Path("tools/archive/legacy.py"))

    def test_no_skip_normal(self):
        assert not _should_skip(Path("agentic_core/L0_routing/foo.py"))

    def test_no_skip_ops_scripts(self):
        assert not _should_skip(Path("ops_scripts/ci/check_structure_policy.py"))


# ---------------------------------------------------------------------------
# check_file — violation cases
# ---------------------------------------------------------------------------


class TestCheckFileViolations:
    def test_long_loop_no_progress(self, tmp_path):
        code = """\
            def process_data(items):
                results = []
                for item in items:
                    a = item * 2
                    b = a + 1
                    c = b - 3
                    d = c * 4
                    e = d / 5
                    f = e + 6
                    g = f - 7
                    h = g * 8
                    i = h - 1
                    j = i + 9
                    results.append(j)
                return results
        """
        p = _write_py(tmp_path, "long_loop.py", code)
        violations = check_file(p)
        loop_violations = [v for v in violations if "For-loop" in v.message]
        assert len(loop_violations) >= 1
        assert "§16" in loop_violations[0].message

    def test_heavy_function_no_progress(self, tmp_path):
        code = """\
            def scan_repository(root):
                results = []
                step1 = init(root)
                step2 = prepare(step1)
                step3 = configure(step2)
                for f in root.rglob("*.py"):
                    content = f.read_text()
                    more = process(f)
                    extra = transform(more)
                    final = validate(extra)
                    results.append(final)
                step4 = finalize(results)
                step5 = report(step4)
                return step5
        """
        p = _write_py(tmp_path, "scan_repo.py", code)
        violations = check_file(p)
        assert any("scan_repository" in v.message for v in violations)

    def test_analyze_function_no_progress(self, tmp_path):
        code = """\
            def analyze_graph(graph):
                visited = set()
                init_state = setup(graph)
                context = build_context(init_state)
                for node in graph.nodes:
                    for edge in node.edges:
                        visited.add(edge)
                        compute(edge)
                        transform(edge)
                        validate(edge)
                        store(edge)
                        report(edge)
                        log(edge)
                return visited
        """
        p = _write_py(tmp_path, "analyze.py", code)
        violations = check_file(p)
        assert any("analyze_graph" in v.message for v in violations)

    def test_build_function_excluded_from_heavy_prefix(self, tmp_path):
        """build_* is excluded from heavy prefixes — function-level check must not fire."""
        code = """\
            def build_index(files):
                index = {}
                config = load_config()
                schema = resolve_schema(config)
                for f in files:
                    k = f.stem
                    v = f.read_text()
                    parsed = parse(v)
                    validated = validate(parsed)
                    transformed = transform(validated)
                    stored = store(transformed)
                    logged = log(stored)
                    result = finalize(logged)
                    index[k] = result
                return index
        """
        p = _write_py(tmp_path, "build_index.py", code)
        violations = check_file(p)
        func_violations = [v for v in violations if "build_index" in v.message]
        assert func_violations == [], f"build_* should not be flagged: {func_violations}"


# ---------------------------------------------------------------------------
# check_file — compliant cases (no violations)
# ---------------------------------------------------------------------------


class TestCheckFileCompliant:
    def test_tqdm_loop_compliant(self, tmp_path):
        code = """\
            from tqdm import tqdm

            def process_data(items):
                results = []
                for item in tqdm(items, desc="Processing"):
                    a = item * 2
                    b = a + 1
                    c = b - 3
                    d = c * 4
                    e = d / 5
                    f = e + 6
                    g = f - 7
                    results.append(g)
                return results
        """
        p = _write_py(tmp_path, "tqdm_loop.py", code)
        assert check_file(p) == []

    def test_pbar_update_compliant(self, tmp_path):
        code = """\
            def scan_files(paths, pbar):
                results = []
                for path in paths:
                    data = path.read_text()
                    parsed = parse(data)
                    validated = validate(parsed)
                    transformed = transform(validated)
                    stored = store(transformed)
                    logged = log(stored)
                    result = finalize(logged)
                    results.append(result)
                    extra = compute(path)
                    results.append(extra)
                    pbar.update(1)
                return results
        """
        p = _write_py(tmp_path, "pbar_update.py", code)
        assert check_file(p) == []

    def test_progress_reporter_compliant(self, tmp_path):
        code = """\
            from tools.progress_display import ProgressReporter

            def query_nodes(graph):
                reporter = ProgressReporter(total=len(graph.nodes), label="Query")
                results = []
                for node in graph.nodes:
                    data = node.fetch()
                    parsed = parse(data)
                    validated = validate(parsed)
                    transformed = transform(validated)
                    stored = store(transformed)
                    logged = log(stored)
                    result = finalize(logged)
                    results.append(result)
                    reporter.update()
                reporter.done()
                return results
        """
        p = _write_py(tmp_path, "progress_reporter.py", code)
        assert check_file(p) == []

    def test_validate_function_excluded_from_heavy_prefix(self, tmp_path):
        """validate_* functions are excluded — thin policy wrappers, not time-intensive."""
        code = """\
            def validate_cache_operation(op, key, data_size=None):
                result = check_policy(op)
                for item in result.items:
                    check(item)
                    verify(item)
                    assert_ok(item)
                    log(item)
                    store(item)
                    emit(item)
                    record(item)
                    finalize(item)
                    archive(item)
                    report(item)
                return result
        """
        p = _write_py(tmp_path, "validate_no_flag.py", code)
        violations = check_file(p)
        func_violations = [v for v in violations if "validate_cache_operation" in v.message]
        assert func_violations == [], f"validate_* should not be flagged: {func_violations}"

    def test_heavy_func_no_loop_no_false_positive(self, tmp_path):
        """scan_* function with no for-loop must not be flagged (no iteration = not time-intensive)."""
        code = """\
            def scan_config(root):
                a = load(root)
                b = parse(a)
                c = validate(b)
                d = transform(c)
                e = store(d)
                f = log(e)
                g = finalize(f)
                h = check(g)
                i = report(h)
                j = archive(i)
                k = emit(j)
                l = record(k)
                return l
        """
        p = _write_py(tmp_path, "scan_no_loop.py", code)
        violations = check_file(p)
        func_violations = [v for v in violations if "scan_config" in v.message]
        assert func_violations == []

    def test_short_loop_no_violation(self, tmp_path):
        code = """\
            def process_items(items):
                for item in items:
                    do_work(item)
                    log(item)
        """
        p = _write_py(tmp_path, "short_loop.py", code)
        assert check_file(p) == []

    def test_unknown_function_name_no_violation(self, tmp_path):
        code = """\
            def compute_total(items):
                total = 0
                for item in items:
                    total += item.value
                    subtotal = item.sub
                    tax = item.tax
                    discount = item.discount
                    net = subtotal - discount
                    gross = net + tax
                    total += gross
                    adj = adjust(total)
                    total = adj
                return total
        """
        p = _write_py(tmp_path, "compute.py", code)
        # 'compute_total' doesn't start with a heavy prefix → function check skipped
        # but the inner loop IS long enough — so we check only function check is not triggered
        violations = check_file(p)
        assert not any("compute_total" in v.message for v in violations)

    def test_syntax_error_file_ignored(self, tmp_path):
        p = tmp_path / "bad_syntax.py"
        p.write_text("def broken(\n    pass\n", encoding="utf-8")
        assert check_file(p) == []

    def test_progress_bar_var_compliant(self, tmp_path):
        code = """\
            def process_batch(items):
                progress_bar = make_bar(len(items))
                for item in items:
                    work(item)
                    transform(item)
                    validate(item)
                    store(item)
                    log(item)
                    check(item)
                    finalize(item)
                    report(item)
                    progress_bar.update()
                return True
        """
        p = _write_py(tmp_path, "progress_bar_var.py", code)
        assert check_file(p) == []


# ---------------------------------------------------------------------------
# check_files — multi-file
# ---------------------------------------------------------------------------


class TestCheckFiles:
    def test_mixed_files(self, tmp_path):
        clean = _write_py(
            tmp_path,
            "clean.py",
            """\
            def process(items):
                for item in items:
                    do(item)
        """,
        )
        dirty = _write_py(
            tmp_path,
            "dirty.py",
            """\
            def scan_all(paths):
                results = []
                for p in paths:
                    a = read(p)
                    b = parse(a)
                    c = validate(b)
                    d = transform(c)
                    e = store(d)
                    f = log(e)
                    g = finalize(f)
                    h = check(g)
                    results.append(h)
                    extra = compute(p)
                    results.append(extra)
                return results
        """,
        )
        violations = check_files([clean, dirty])
        assert len(violations) >= 1
        assert all(dirty.name in str(v) or str(dirty) in str(v) for v in violations)

    def test_non_python_files_skipped(self, tmp_path):
        md = tmp_path / "README.md"
        md.write_text("# No progress bar needed here", encoding="utf-8")
        violations = check_files([md])
        assert violations == []

    def test_skip_pattern_respected(self, tmp_path):
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        p = cache_dir / "cached.py"
        p.write_text("for x in items:\n    work(x)\n" * 15, encoding="utf-8")
        violations = check_files([p])
        assert violations == []


# ---------------------------------------------------------------------------
# main() exit codes
# ---------------------------------------------------------------------------


class TestMain:
    def test_main_no_files_returns_skip(self, tmp_path):
        exit_code = main(["--verbose", str(tmp_path / "nonexistent.py")])
        # nonexistent files are simply not found / skipped
        assert exit_code in (0, 1)

    def test_main_clean_file_exits_zero(self, tmp_path):
        p = _write_py(
            tmp_path,
            "clean.py",
            """\
            def helper(x):
                return x + 1
        """,
        )
        exit_code = main([str(p)])
        assert exit_code == 0

    def test_main_violation_exits_one(self, tmp_path):
        p = _write_py(
            tmp_path,
            "violator.py",
            """\
            def scan_modules(root):
                results = []
                for mod in root.iterdir():
                    a = mod.read_text()
                    b = parse(a)
                    c = validate(b)
                    d = transform(c)
                    e = store(d)
                    f = log(e)
                    g = finalize(f)
                    h = check(g)
                    results.append(h)
                    extra = compute(mod)
                    results.append(extra)
                return results
        """,
        )
        exit_code = main([str(p)])
        assert exit_code == 1

    def test_main_verbose_flag_accepted(self, tmp_path):
        p = _write_py(tmp_path, "simple.py", "x = 1\n")
        exit_code = main(["--verbose", str(p)])
        assert exit_code == 0


# ---------------------------------------------------------------------------
# Violation __str__
# ---------------------------------------------------------------------------


class TestViolationStr:
    def test_str_contains_lineno(self):
        v = Violation(Path(_ROOT / "tools" / "foo.py"), 42, "some message")
        s = str(v)
        assert "42" in s
        assert "some message" in s

    def test_str_outside_root(self, tmp_path):
        p = tmp_path / "outside.py"
        v = Violation(p, 1, "msg")
        s = str(v)
        assert "1" in s
        assert "msg" in s


# ---------------------------------------------------------------------------
# collect_repo_files — smoke test
# ---------------------------------------------------------------------------


class TestCollectRepoFiles:
    def test_returns_list_of_py_paths(self):
        files = collect_repo_files()
        assert isinstance(files, list)
        assert all(f.suffix == ".py" for f in files)

    def test_no_pycache_in_results(self):
        files = collect_repo_files()
        assert not any("__pycache__" in str(f) for f in files)

    def test_no_archives_in_results(self):
        files = collect_repo_files()
        # Check path *components* not substring (filename may legitimately contain 'archives')
        archive_path_hits = [f for f in files if any(part in ("archives", "archive") for part in f.parts)]
        assert archive_path_hits == [], f"Files in archive dirs: {archive_path_hits[:3]}"
