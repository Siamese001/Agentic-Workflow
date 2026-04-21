"""Core AST Visitors for ADG Extraction.

Visitors in this module extract:
    - Call edges for sensitive symbols (embeddings, writes, network)
    - Antipattern detection (silent exception swallow, broad catches, etc.)
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor
from tqdm import tqdm

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("call")
class _CallVisitor(BaseStructuralVisitor):
    """Extract call edges for sensitive symbols (embeddings, writes, network)."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        # Import symbols at runtime to avoid circular imports
        from agentic_core.adg.contracts.schema_util import (
            EMBEDDING_SYMBOLS,
            NETWORK_SYMBOLS,
            PROVIDER_SDK_SYMBOLS,
            WRITE_SIDE_EFFECT_EXCLUSIONS,
            WRITE_SIDE_EFFECT_SYMBOLS,
        )

        self._embedding_symbols = EMBEDDING_SYMBOLS
        self._write_symbols = WRITE_SIDE_EFFECT_SYMBOLS
        self._write_exclusions = WRITE_SIDE_EFFECT_EXCLUSIONS
        self._network_symbols = NETWORK_SYMBOLS
        self._provider_symbols = PROVIDER_SDK_SYMBOLS

    def visit_Call(self, node: ast.Call) -> None:
        """Extract edges from function calls to sensitive symbols."""
        sym = self._extract_symbol(node.func)
        if sym:
            # Suppress instrumentation helpers from generating base edges
            tail = sym.rsplit(".", 1)[-1] if "." in sym else sym
            if tail.startswith("_emit_") or tail.startswith("emit_"):
                self.generic_visit(node)
                return

            edge_kind, relation = self._classify_call(sym)
            if edge_kind:
                from agentic_core.adg.contracts.schema_util import canonical_name
                from agentic_core.adg.extraction.static_scanner import Edge as _Edge

                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type=relation,
                        to_name=to_name,
                        edge_kind=edge_kind,
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    ),
                )
        self.generic_visit(node)

    def _extract_symbol(self, func_node: ast.expr) -> str:
        """Extract symbol name from function expression."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    def _classify_call(self, sym: str) -> tuple[str, str]:
        """Classify call edge kind and relation type."""
        if sym in self._embedding_symbols or any(sym.endswith(e) for e in self._embedding_symbols):
            return "embedding", "instantiates"
        if sym in self._write_symbols or any(sym.endswith(w.split(".")[-1]) for w in self._write_symbols):
            # G3: exclude false-positive write symbols
            if sym in self._write_exclusions:
                return "", ""
            return "write", "writes_to"
        if sym in self._network_symbols or any(
            sym.startswith(n.split(".")[0]) for n in self._network_symbols
        ):
            return "network", "invokes_provider"

        base = sym.split(".")[0]
        if base in {s.split(".")[0] for s in self._provider_symbols}:
            return "network", "invokes_provider"

        return "", ""

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("antipattern")
class _AntipatternVisitor(BaseStructuralVisitor):
    """GA: Detect behavioral anti-patterns via AST analysis.

    Emits `antipattern` edges for:
        - silent exception swallow
        - broad exception catches
        - log-and-swallow patterns
        - return-None-after-exception
        - blocking I/O calls inside async functions
        - module-level UPPER_CASE mutation inside functions (lazy-init guard excluded)
        - retry loops without backoff (range-based loops only, not collection iteration)
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        from agentic_core.adg.contracts.schema_util import BROAD_EXCEPTION_TYPES

        self._broad_exceptions = BROAD_EXCEPTION_TYPES
        self._antipatterns: list[tuple[int, str, str]] = []  # (line_no, category, symbol)
        # Allowlist of known blocking I/O calls for async detection
        self._blocking_io_calls = frozenset(
            {
                "time.sleep",
                "requests.get",
                "requests.post",
                "requests.put",
                "requests.delete",
                "requests.request",
                "urllib.request.urlopen",
                "urllib.urlopen",
                "socket.recv",
                "socket.send",
                "socket.connect",
                "socket.accept",
                "subprocess.run",
                "subprocess.call",
                "subprocess.check_output",
                "os.system",
                "asyncio.get_event_loop().run_until_complete",
            }
        )
        # Hardcoded path patterns to detect (AST stores string values without escapes)
        self._hardcoded_path_patterns = frozenset(
            {
                "C:\\Git\\",  # Windows backslash path
                "C:/Git/",  # Windows forward slash path
                "/home/amita/",  # Unix user home
                "/Users/amita/",  # macOS user home
                "D:\\",  # Secondary drive
            }
        )

    def visit_Constant(self, node: ast.Constant) -> None:
        """Detect hardcoded absolute paths in string constants."""
        if isinstance(node.value, str):
            for pattern in self._hardcoded_path_patterns:
                if pattern in node.value:
                    self._antipatterns.append(
                        (
                            node.lineno,
                            "hardcoded_path",
                            pattern,
                        )
                    )
                    break
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Detect antipatterns in exception handlers."""
        handler_type = self._get_exception_type(node.type)

        # Bare `except:` (node.type is None) is strictly MORE dangerous than
        # `except Exception:` because it also catches SystemExit,
        # KeyboardInterrupt, and GeneratorExit — non-exceptions that are
        # part of normal interpreter shutdown / iteration protocol.
        # Emitted as its own edge_kind (not subsumed by broad_exception_catch).
        if node.type is None:
            self._antipatterns.append(
                (
                    node.lineno,
                    "bare_except",
                    "BaseException",
                )
            )
        # Broad Exception/BaseException catch
        elif handler_type in self._broad_exceptions:
            self._antipatterns.append(
                (
                    node.lineno,
                    "broad_exception_catch",
                    handler_type or "Exception",
                )
            )

        # Doc #12 — throw_for_normal_flow
        # Conservative: narrow control-flow exception (KeyError/IndexError/
        # AttributeError/LookupError/StopIteration) caught + body takes a
        # non-error 'continue normal processing' path (not log/raise/return None).
        # Intentionally P3 LOW: this is subjective and has FPs by design.
        if self._is_throw_for_normal_flow(node, handler_type):
            self._antipatterns.append(
                (
                    node.lineno,
                    "throw_for_normal_flow",
                    handler_type or "Exception",
                )
            )

        # Doc #4 — default_fallback_masking
        # Handler body is a single assignment `X = <Constant literal>` where
        # the constant is NOT None (None is already return_none_swallow).
        # Catches the "except Exception: price = 0" pattern.
        #
        # Precision: exempt ImportError / ModuleNotFoundError / SyntaxError /
        # ParseError handlers - these are standard optional-dependency,
        # feature-detection, and parse-recovery patterns, not failure masking.
        _optional_dep_types = {
            "ImportError",
            "ModuleNotFoundError",
            "SyntaxError",
            "ParseError",
            "DecodeError",
            "JSONDecodeError",
            "EOFError",
        }
        if (
            self._is_default_fallback_masking(node.body)
            and handler_type not in _optional_dep_types
        ):
            self._antipatterns.append(
                (
                    node.lineno,
                    "default_fallback_masking",
                    handler_type or "Exception",
                )
            )

        # Analyze handler body for antipatterns
        if node.body:
            # Check for empty/pass-only handlers (silent swallow)
            if self._is_silent_swallow(node.body):
                self._antipatterns.append(
                    (
                        node.lineno,
                        "silent_exception_swallow",
                        handler_type or "Exception",
                    )
                )

            # Check for log-and-swallow
            if self._is_log_and_swallow(node.body):
                self._antipatterns.append(
                    (
                        node.lineno,
                        "log_and_swallow",
                        handler_type or "Exception",
                    )
                )

            # Check for return None after exception
            if self._is_return_none_after_exception(node.body):
                self._antipatterns.append(
                    (
                        node.lineno,
                        "return_none_swallow",
                        handler_type or "Exception",
                    )
                )

            # Check for unreachable code after raise (Pattern C — dead code bug)
            if self._has_unreachable_after_raise(node.body):
                self._antipatterns.append(
                    (
                        node.lineno,
                        "unreachable_after_raise",
                        handler_type or "Exception",
                    )
                )

            # Check for exception type erasure (doc #8 — raise new type without 'from')
            erased_type = self._get_erased_exception_type(node, handler_type)
            if erased_type is not None:
                self._antipatterns.append(
                    (
                        node.lineno,
                        "exception_type_erasure",
                        f"{handler_type or 'Exception'}->{erased_type}",
                    )
                )

            # Check for double-logging (doc #11 — log + re-raise).
            # The inner half: handler invokes a logger AND re-raises. The outer caller
            # almost always catches and logs the same error, producing duplicate alerts.
            # Intentionally a high-precision proxy — flags only within-handler evidence.
            if self._is_double_logging(node.body):
                self._antipatterns.append(
                    (
                        node.lineno,
                        "double_logging",
                        handler_type or "Exception",
                    )
                )

        self.generic_visit(node)

    def _get_exception_type(self, type_node: ast.expr | None) -> str | None:
        """Extract exception type name from AST node."""
        if type_node is None:
            return "Exception"  # bare except:
        if isinstance(type_node, ast.Name):
            return type_node.id
        if isinstance(type_node, ast.Tuple):
            # Get first element for tuple exceptions
            if type_node.elts:
                first = type_node.elts[0]
                if isinstance(first, ast.Name):
                    return first.id
        return None

    def _is_silent_swallow(self, body: list[ast.stmt]) -> bool:
        """Check if handler silently swallows exception (pass only)."""
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            return True
        # Check for comment-only handlers (effectively silent)
        return all(isinstance(s, ast.Pass) for s in body)

    def _is_log_and_swallow(self, body: list[ast.stmt]) -> bool:
        """Check for log-and-swallow pattern."""
        # Look for logging call followed by implicit fallthrough
        for i, stmt in enumerate(body):
            if isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Call):
                    call = stmt.value
                    if isinstance(call.func, ast.Attribute):
                        if call.func.attr in {"debug", "info", "warning", "error", "exception"}:
                            # Check if this is the last statement or followed by pass
                            remaining = body[i + 1 :]
                            if not remaining or all(isinstance(s, ast.Pass) for s in remaining):
                                return True
        return False

    def _is_return_none_after_exception(self, body: list[ast.stmt]) -> bool:
        """Check for return None pattern after exception handling."""
        if not body:
            return False
        last = body[-1]
        if isinstance(last, ast.Return):
            # return with no value or explicit None
            if last.value is None:
                return True
            if isinstance(last.value, ast.Constant) and last.value.value is None:
                return True
        return False

    def _is_default_fallback_masking(self, body: list[ast.stmt]) -> bool:
        """Detect doc anti-pattern #4 — 'except X: price = 0'.

        Handler body is a single assignment ``target = <non-None constant literal>``.
        Return-None swallows are deliberately excluded (covered by
        ``return_none_swallow``). Flags fabricated-value patterns where a
        real failure is masquerading as a valid value (price=0, count=0,
        status="ok", etc.).
        """
        if len(body) != 1:
            return False
        stmt = body[0]
        if not isinstance(stmt, ast.Assign):
            return False
        if not isinstance(stmt.value, ast.Constant):
            return False
        # Exclude None (already return_none_swallow territory; here it's assignment)
        if stmt.value.value is None:
            return False
        # Require at least one simple Name target (don't flag tuple/attribute assigns)
        for target in stmt.targets:
            if isinstance(target, (ast.Name, ast.Attribute)):
                return True
        return False

    def _is_throw_for_normal_flow(self, node: ast.ExceptHandler, handler_type: str | None) -> bool:
        """Detect doc anti-pattern #12 — exception as control flow.

        Conservative: only flags when BOTH:
          1. The caught type is a narrow control-flow exception
             (KeyError / IndexError / AttributeError / LookupError / StopIteration)
          2. The handler body does NOT re-raise, does NOT return None, and does
             NOT consist solely of a log call — i.e. it performs active
             ``normal-path'' work.
        P3 LOW severity because this is subjective by design.
        """
        control_flow_types = {
            "KeyError",
            "IndexError",
            "AttributeError",
            "LookupError",
            "StopIteration",
        }
        # Single narrow type
        if handler_type not in control_flow_types:
            # Tuple: check if all members are control-flow types
            if isinstance(node.type, ast.Tuple):
                names: list[str] = []
                for elt in node.type.elts:
                    if isinstance(elt, ast.Name):
                        names.append(elt.id)
                if not names or not all(n in control_flow_types for n in names):
                    return False
            else:
                return False

        if not node.body:
            return False

        # Exclude if handler re-raises (that's proper)
        for stmt in node.body:
            if isinstance(stmt, ast.Raise):
                return False
        # Exclude return-None (that's return_none_swallow)
        if self._is_return_none_after_exception(node.body):
            return False
        # Exclude log-only (that's log_and_swallow; also exclude pass-only)
        if self._is_silent_swallow(node.body):
            return False
        if self._is_log_and_swallow(node.body):
            return False

        # At this point the body does 'something else' — active normal flow.
        # This is the doc anti-pattern #12 signature.
        return True

    def _is_double_logging(self, body: list[ast.stmt]) -> bool:
        """Detect doc anti-pattern #11 inner-side: handler logs AND re-raises.

        Pattern:
            except X as e:
                logger.error("failed: %s", e)   # <-- log
                raise                           # <-- re-raise

        The outer caller will almost always catch-and-log the same exception,
        producing duplicate alerts / alert fatigue (doc Pattern 11). The GOOD
        variant is 'log OR re-raise, not both' — if re-raising, let the top
        boundary log; don't emit duplicates at intermediate layers.
        """
        if not body:
            return False
        has_log = False
        has_reraise = False
        for stmt in body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Attribute) and call.func.attr in {
                    "debug",
                    "info",
                    "warning",
                    "error",
                    "exception",
                    "critical",
                }:
                    has_log = True
            elif isinstance(stmt, ast.Raise):
                has_reraise = True
        return has_log and has_reraise

    def _has_unreachable_after_raise(self, body: list[ast.stmt]) -> bool:
        """Detect 'raise' followed by executable statements in an except body.

        Pattern C (cross-cutting) — dead code after a raise/re-raise. The
        code after raise is NEVER executed and is almost always a leftover
        log or state-mutation statement that the author forgot to delete.
        """
        if not body:
            return False
        for i, stmt in enumerate(body):
            if not isinstance(stmt, ast.Raise):
                continue
            # Any remaining non-pass, non-docstring statement = dead code
            for follow in body[i + 1 :]:
                if isinstance(follow, ast.Pass):
                    continue
                if (
                    isinstance(follow, ast.Expr)
                    and isinstance(follow.value, ast.Constant)
                    and isinstance(follow.value.value, str)
                ):
                    # Docstring / standalone string literal — ignore
                    continue
                return True
        return False

    def _get_erased_exception_type(self, node: ast.ExceptHandler, handler_type: str | None) -> str | None:
        """Detect doc anti-pattern #8 — type erasure via bare 'raise NewExc(...)'.

        Returns the erased type name if the except body raises a DIFFERENT
        exception type WITHOUT chaining the original via 'from <caught>' or
        'from e'. Returns None if no erasure detected.

        A raise without 'cause' inside an except handler is PEP 3134 compliant
        only when raising the SAME type (bare ``raise`` or ``raise OriginalType(...)``).
        Raising a DIFFERENT type without ``from`` silently drops the original
        exception context from debuggers and tracebacks.
        """
        if not node.body or handler_type is None:
            return None
        # Walk the immediate except body (not nested try/except) for raises
        for stmt in node.body:
            if not isinstance(stmt, ast.Raise):
                continue
            # Bare 're-raise' — no erasure
            if stmt.exc is None:
                continue
            # raise X(...) or raise X
            raised_type: str | None = None
            if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                raised_type = stmt.exc.func.id
            elif isinstance(stmt.exc, ast.Name):
                raised_type = stmt.exc.id
            if raised_type is None:
                continue
            # Same-type re-raise (e.g., 'raise RuntimeError(...)' inside except RuntimeError) is fine
            if raised_type == handler_type:
                continue
            # 'raise X from <anything>' documents the chain — not erasure
            if stmt.cause is not None:
                continue
            # Different type, no cause → erasure
            return raised_type
        return None

    def visit_Try(self, node: ast.Try) -> None:
        """Detect finally-block antipatterns (doc #9/#10) and partial side effects (doc #7)."""
        if node.finalbody:
            # Doc #9 — 'cleanup_raises_over_original'
            # Any Raise inside finalbody can mask the exception from the try block.
            for stmt in node.finalbody:
                if isinstance(stmt, ast.Raise):
                    self._antipatterns.append(
                        (
                            stmt.lineno,
                            "cleanup_raises_over_original",
                            "finally:raise",
                        )
                    )
                    break
            # Doc #10 — 'return_in_finally'
            # Any Return in finalbody silently overrides the try/except result.
            for stmt in node.finalbody:
                if isinstance(stmt, ast.Return):
                    self._antipatterns.append(
                        (
                            stmt.lineno,
                            "return_in_finally",
                            "finally:return",
                        )
                    )
                    break

        # Doc #7 — 'partial_side_effects'
        # When the try body performs MULTIPLE side effects (writes, network, subprocess,
        # filesystem, database ops) AND any handler SWALLOWS the exception, the
        # system-of-record can be left inconsistent: some writes landed, the failing one
        # did not, and the caller sees success. Uses the existing graph-layer
        # side-effect taxonomy.
        #
        # Precision: require >=2 side effects (1 side effect has no "partial" risk —
        # it either fully succeeded or fully failed, and the swallow is already
        # tracked by log_and_swallow / silent_exception_swallow / return_none_swallow).
        # This removes the duplicate-flag pattern where every swallowing handler with
        # a single write was triple-counted.
        side_effect_count = self._count_side_effects_in_body(node.body)
        if side_effect_count >= 2 and node.handlers:
            for handler in node.handlers:
                if self._handler_is_swallowing(handler):
                    self._antipatterns.append(
                        (
                            handler.lineno,
                            "partial_side_effects",
                            f"try_body_side_effects={side_effect_count}",
                        )
                    )
        self.generic_visit(node)

    def _count_side_effects_in_body(self, body: list[ast.stmt]) -> int:
        """Count side-effect calls inside a try body using graph-layer taxonomy.

        Reuses the canonical WRITE_SIDE_EFFECT_SYMBOLS and NETWORK_SYMBOLS used by
        the graph-layer _CallVisitor so detection stays consistent with the
        ``emits_side_effect`` / ``writes_to`` edges already in the ADG.
        """
        from agentic_core.adg.contracts.schema_util import (
            NETWORK_SYMBOLS,
            WRITE_SIDE_EFFECT_SYMBOLS,
        )

        side_effect_syms = set(WRITE_SIDE_EFFECT_SYMBOLS) | set(NETWORK_SYMBOLS)
        # Cheap string-prefix match for base symbols (subprocess.*, os.*, requests.*, etc.)
        side_effect_prefixes = {"subprocess.", "os.", "requests.", "urllib.", "socket.", "shutil."}

        count = 0
        for stmt in body:
            for child in ast.walk(stmt):
                if not isinstance(child, ast.Call):
                    continue
                sym = self._extract_symbol(child.func)
                if not sym:
                    continue
                if sym in side_effect_syms:
                    count += 1
                    continue
                if any(sym.startswith(p) for p in side_effect_prefixes):
                    count += 1
        return count

    def _handler_is_swallowing(self, handler: ast.ExceptHandler) -> bool:
        """True if the handler swallows — no raise, or a raise that's unreachable."""
        if not handler.body:
            return True
        # Walk top-level stmts; if we see a Raise, not swallowing (unless dead-code pattern).
        for stmt in handler.body:
            if isinstance(stmt, ast.Raise):
                return False
        # No raise at top level = swallowing (silent, log+continue, or return None)
        return True

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Detect blocking I/O calls in async bodies + mutable default args."""
        self._check_mutable_default_args(node)
        for child in tqdm(ast.walk(node), desc="Processing", unit="item"):
            if isinstance(child, ast.Call):
                sym = self._extract_symbol(child.func)
                if sym and sym in self._blocking_io_calls:
                    self._antipatterns.append(
                        (
                            child.lineno,
                            "blocking_call_in_async",
                            sym,
                        )
                    )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Detect global state mutation + mutable default args + agent-safety patterns."""
        self._check_global_state_mutation(node)
        self._check_mutable_default_args(node)
        # Tier 1 agent-safety detectors (plan agentic-antipattern-tier1-9f2c8a)
        self._check_unbounded_agent_loop(node)
        self._check_llm_output_unvalidated(node)
        self._check_hallucinated_tool_name(node)
        self.generic_visit(node)

    # -----------------------------------------------------------------
    # Tier 1 agentic anti-pattern detectors
    # -----------------------------------------------------------------

    def _is_in_agent_method(self, func_name: str) -> bool:
        """True if a function name looks like an agent lifecycle method.

        Conservative: only flags methods named ``heal``, ``run``, ``step``,
        ``execute``, ``loop``, ``dispatch``, ``react``. This keeps FPs low
        for generic utility loops.
        """
        return func_name in {
            "heal",
            "run",
            "step",
            "execute",
            "loop",
            "dispatch",
            "react",
            "run_loop",
            "agent_loop",
            "reason_act",
            "tool_loop",
        }

    def _check_unbounded_agent_loop(self, node: ast.FunctionDef) -> None:
        """Doc A1 — unbounded agent reasoning loop.

        Flags ``while True:`` (or ``while 1:``) inside an agent lifecycle
        method whose body contains NO ``break`` at top level AND NO bounded
        loop counter comparison. This is the classic ReAct loop that cannot
        terminate on persistent tool failure.

        Conservative: requires method name to match agent lifecycle set.
        """
        if not self._is_in_agent_method(node.name):
            return
        # Only consider top-level while-True loops in the function body
        for stmt in node.body:
            if not isinstance(stmt, ast.While):
                continue
            # Must be 'while True:' or 'while 1:'
            test = stmt.test
            is_unconditional = (isinstance(test, ast.Constant) and test.value in (True, 1)) or (
                isinstance(test, ast.Name) and test.id == "True"
            )
            if not is_unconditional:
                continue
            # Check for a top-level break in the loop body
            has_break = any(isinstance(s, ast.Break) for s in stmt.body)
            # Check for a top-level return in the loop body (also escapes)
            has_return = any(isinstance(s, ast.Return) for s in stmt.body)
            if has_break or has_return:
                continue
            # Check for raise at top level (also escapes)
            has_raise = any(isinstance(s, ast.Raise) for s in stmt.body)
            if has_raise:
                continue
            self._antipatterns.append(
                (
                    stmt.lineno,
                    "unbounded_agent_loop",
                    node.name,
                )
            )

    def _check_llm_output_unvalidated(self, node: ast.FunctionDef) -> None:
        """Doc A2 — LLM output consumed without schema validation.

        Conservative pattern: flag when ``json.loads(...)`` is called on an
        argument whose expression traces to an LLM response surface
        (``.content``, ``.choices[...].message.content``, ``.text`` on a
        known-LLM-response variable) AND the result is NOT passed to
        ``pydantic`` / ``.parse_obj`` / ``.model_validate`` / ``validate_*``
        anywhere in the same function body.
        """
        llm_response_attrs = {"content", "text", "message"}
        json_loads_nodes: list[ast.Call] = []
        validation_calls: set[str] = set()
        has_server_side_json_schema = False
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            sym = self._extract_symbol(child.func)
            if sym == "json.loads":
                # Check if argument traces to an LLM response surface
                if child.args and self._expr_traces_to_llm_response(child.args[0], llm_response_attrs):
                    json_loads_nodes.append(child)
            # Track validation calls
            if sym:
                tail = sym.rsplit(".", 1)[-1]
                if tail in {"parse_obj", "model_validate", "parse_raw", "model_validate_json"}:
                    validation_calls.add(sym)
                elif tail.startswith("validate_") or tail == "validate":
                    validation_calls.add(sym)
            # Track OpenAI-style server-side JSON schema enforcement:
            #   response_format={"type": "json_object"} or
            #   response_format={"type": "json_schema", ...}
            # These are pre-validated by the API itself.
            for kw in child.keywords or []:
                if kw.arg == "response_format" and isinstance(kw.value, ast.Dict):
                    for k, v in zip(kw.value.keys, kw.value.values):
                        if (
                            isinstance(k, ast.Constant)
                            and k.value == "type"
                            and isinstance(v, ast.Constant)
                            and isinstance(v.value, str)
                            and v.value in ("json_object", "json_schema")
                        ):
                            has_server_side_json_schema = True
        # If json.loads is followed by ANY validation call in the same function,
        # OR if the upstream LLM call uses server-side JSON schema enforcement,
        # we treat validation as present (conservative — collapses false positives).
        if json_loads_nodes and not (validation_calls or has_server_side_json_schema):
            for call in json_loads_nodes:
                self._antipatterns.append(
                    (
                        call.lineno,
                        "llm_output_unvalidated",
                        "json.loads(llm_response)",
                    )
                )

    def _expr_traces_to_llm_response(self, expr: ast.expr, response_attrs: set[str]) -> bool:
        """Shallow trace: does this expression look like an LLM response surface?

        Matches ``X.content``, ``X.text``, ``X.choices[i].message.content``,
        ``X.choices[0].text``. No cross-statement dataflow — purely structural.
        """
        cur: ast.expr = expr
        depth = 0
        while depth < 8:
            depth += 1
            if isinstance(cur, ast.Attribute):
                if cur.attr in response_attrs:
                    return True
                cur = cur.value
                continue
            if isinstance(cur, ast.Subscript):
                cur = cur.value
                continue
            if isinstance(cur, ast.Call):
                # e.g., response.json() — don't chase further
                return False
            return False
        return False

    def _check_hallucinated_tool_name(self, node: ast.FunctionDef) -> None:
        """Doc A15 — hallucinated tool/API name not caught pre-execution.

        Conservative pattern: flag when ``tools[X]`` or ``toolkit[X]`` or
        ``getattr(<something>, X)`` is used with a DYNAMIC (variable) key AND
        there is no ``X in tools`` / ``X in registry`` / ``hasattr`` check in
        the same function body.

        Precision exclusions:
          - __getattr__ delegation methods (Python protocol — receiver
            raises AttributeError if not present)
          - iteration over dir(X)/vars(X) (all members guaranteed real)
          - iteration over a self._CONSTANT_ attribute (class-level literal)
          - tqdm/enumerate/sorted/iter wrapping of a literal tuple/list/set
        """
        # Skip Python's __getattr__ delegation — framework-enforced safety
        if node.name == "__getattr__":
            return
        dynamic_lookups: list[tuple[int, str]] = []  # (line, container_name)
        has_membership_check = False
        has_hasattr_check = False
        has_attr_except = False
        has_key_except = False

        # Container names we consider tool-registry-like
        registry_names = {
            "tools",
            "toolkit",
            "tool_registry",
            "registry",
            "capability_registry",
            "capabilities",
            "tool_map",
            "actions",
            "skills",
        }

        # Collect names bound by iteration sources that guarantee the bound
        # name is a real attribute/key. Safe sources:
        #   - literal tuple/list/set of constants
        #   - tqdm/enumerate/sorted/iter/list wrapping a literal collection
        #   - dir(X) / vars(X) / X.__dict__ / X.__dict__.keys()
        #   - self._UPPER_CASE class attribute (declared constant collection)
        def _is_literal_collection(n: ast.expr) -> bool:
            return isinstance(n, (ast.Tuple, ast.List, ast.Set)) and all(
                isinstance(e, ast.Constant) for e in n.elts
            )

        def _is_safe_iter_source(n: ast.expr) -> bool:
            if _is_literal_collection(n):
                return True
            # tqdm(...) / enumerate(...) / sorted(...) / list(...) / iter(...) / tuple(...)
            if isinstance(n, ast.Call):
                fname = None
                if isinstance(n.func, ast.Name):
                    fname = n.func.id
                elif isinstance(n.func, ast.Attribute):
                    fname = n.func.attr
                if fname in {"tqdm", "enumerate", "sorted", "list", "iter", "tuple", "reversed"}:
                    if n.args and _is_safe_iter_source(n.args[0]):
                        return True
                # dir(X), vars(X)
                if isinstance(n.func, ast.Name) and n.func.id in ("dir", "vars"):
                    return True
            # self._UPPER_CASE (class-level constant collection by convention)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "self":
                if n.attr.startswith("_") and n.attr.replace("_", "").isupper():
                    return True
                # also accept plain ALL_CAPS class attr via self.UPPER
                if n.attr.isupper():
                    return True
            # X.__dict__ or X.__annotations__
            if isinstance(n, ast.Attribute) and n.attr in ("__dict__", "__annotations__"):
                return True
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr in ("keys", "values", "items")
            ):
                # X.__dict__.keys() / X.__annotations__.keys()
                if isinstance(n.func.value, ast.Attribute) and n.func.value.attr in (
                    "__dict__",
                    "__annotations__",
                ):
                    return True
            return False

        iter_bound_safe: set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                for gen in child.generators:
                    if _is_safe_iter_source(gen.iter) and isinstance(gen.target, ast.Name):
                        iter_bound_safe.add(gen.target.id)
            if isinstance(child, ast.For):
                if _is_safe_iter_source(child.iter) and isinstance(child.target, ast.Name):
                    iter_bound_safe.add(child.target.id)

        for child in ast.walk(node):
            # Track membership checks. Accepts:
            #   X in <Name>       -> X in tools
            #   X in {...}/[...]  -> X in {"a","b"} (literal set/list/tuple/dict)
            if isinstance(child, ast.Compare):
                for op, comparator in zip(child.ops, child.comparators):
                    if isinstance(op, ast.In):
                        if isinstance(comparator, ast.Name) and comparator.id in registry_names:
                            has_membership_check = True
                        elif isinstance(comparator, (ast.Set, ast.List, ast.Tuple, ast.Dict)):
                            has_membership_check = True
            # Track try/except blocks wrapping attribute/key access
            if isinstance(child, ast.Try):
                for handler in child.handlers:
                    htype = handler.type
                    if isinstance(htype, ast.Name):
                        if htype.id == "AttributeError":
                            has_attr_except = True
                        if htype.id in ("KeyError", "LookupError"):
                            has_key_except = True
                    elif isinstance(htype, ast.Tuple):
                        for elt in htype.elts:
                            if isinstance(elt, ast.Name):
                                if elt.id == "AttributeError":
                                    has_attr_except = True
                                if elt.id in ("KeyError", "LookupError"):
                                    has_key_except = True
            # Track hasattr / getattr with default
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == "hasattr":
                    has_hasattr_check = True
                # getattr(obj, name, default) is safe — 3rd positional arg or 'default' kwarg
                if child.func.id == "getattr":
                    has_default = len(child.args) >= 3 or any(
                        kw.arg == "default" for kw in (child.keywords or [])
                    )
                    if not has_default and len(child.args) >= 2:
                        # Key must be a variable (ast.Name), not a string constant
                        key_arg = child.args[1]
                        if isinstance(key_arg, ast.Name) and key_arg.id not in iter_bound_safe:
                            dynamic_lookups.append((child.lineno, "getattr"))
            # Subscript access: tools[X] where X is a variable AND ctx is Load
            # (Store ctx = assignment target like `tools[tool] = True` is not a lookup)
            if isinstance(child, ast.Subscript) and isinstance(child.ctx, ast.Load):
                container_expr = child.value
                if isinstance(container_expr, ast.Name) and container_expr.id in registry_names:
                    slice_node = child.slice
                    if isinstance(slice_node, ast.Name) and slice_node.id not in iter_bound_safe:
                        dynamic_lookups.append((child.lineno, container_expr.id))
        if dynamic_lookups and not (
            has_membership_check or has_hasattr_check or has_attr_except or has_key_except
        ):
            for line_no, container_name in dynamic_lookups:
                self._antipatterns.append(
                    (
                        line_no,
                        "hallucinated_tool_name",
                        container_name,
                    )
                )

    def _check_global_state_mutation(self, node: ast.FunctionDef) -> None:
        """Check for assignment to module-level UPPER_CASE names, excluding lazy-init guards."""
        for stmt in tqdm(ast.walk(node), desc="Processing", unit="item"):
            if isinstance(stmt, (ast.Assign, ast.AugAssign)):
                for target in tqdm(ast.walk(stmt), desc="Processing", unit="item"):
                    if isinstance(target, ast.Name) and target.id.isupper():
                        # Skip if inside a lazy-init guard: if _X is None: X = ...
                        # TODO: implement parent tracking for guard detection
                        self._antipatterns.append(
                            (
                                stmt.lineno,
                                "global_state_mutation",
                                target.id,
                            )
                        )

    def _extract_symbol(self, func_node: ast.expr) -> str:
        """Extract symbol name from function expression."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    def visit_While(self, node: ast.While) -> None:
        """Detect retry loops without backoff (while loops)."""
        if self._loop_contains_retry_without_backoff(node):
            self._antipatterns.append(
                (
                    node.lineno,
                    "retry_without_backoff",
                    "while_retry",
                )
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Detect hardcoded credentials (conservative; FP-averse).

        Flags ``foo_password = "literal"`` style assignments where the target
        name matches known secret-indicator patterns AND the value is a
        non-trivial string constant. Excludes obvious placeholders, empty
        strings, env var reads, f-strings, and test files.
        """
        import re

        # Exclude test files entirely to avoid FPs on fixtures
        if self._source_file and (
            "/tests/" in self._source_file.replace("\\", "/")
            or self._source_file.startswith("tests/")
            or "conftest" in self._source_file
            or "_test.py" in self._source_file
            or "/test_" in self._source_file.replace("\\", "/")
        ):
            self.generic_visit(node)
            return

        # Value must be a plain string literal (not f-string, not os.environ, not call)
        if not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            self.generic_visit(node)
            return
        value = node.value.value

        # Placeholder / obvious-not-real filter
        if len(value) < 8:
            self.generic_visit(node)
            return
        low = value.lower().strip()
        placeholder_markers = (
            "xxx",
            "todo",
            "fixme",
            "example",
            "placeholder",
            "dummy",
            "fake",
            "your-",
            "your_",
            "<",
            ">",
            "...",
            "changeme",
            "change-me",
            "change_me",
            "replace",
            "n/a",
            "none",
            "null",
            "test",
        )
        if any(m in low for m in placeholder_markers):
            self.generic_visit(node)
            return

        # Target name must look secret-like
        secret_name_pattern = re.compile(
            r"(?:^|_)(?:password|passwd|secret|api[_-]?key|private[_-]?key|"
            r"access[_-]?key|auth[_-]?token|bearer[_-]?token|refresh[_-]?token|"
            r"credential|client[_-]?secret|signing[_-]?key)s?(?:$|_)",
            re.IGNORECASE,
        )
        # Identifier/label suffixes — these name a KIND of secret, not a secret itself
        label_suffixes = ("_id", "_name", "_type", "_kind", "_label", "_key_id")
        flagged = False
        matched_name: str | None = None
        for target in node.targets:
            name: str | None = None
            if isinstance(target, ast.Name):
                name = target.id
            elif isinstance(target, ast.Attribute):
                name = target.attr
            if not (name and secret_name_pattern.search(name)):
                continue
            # Skip enum-label pattern: PASSWORD = "password" (value matches name)
            name_normalized = name.lower().replace("_", "").replace("-", "")
            value_normalized = value.lower().replace("_", "").replace("-", "")
            if name_normalized == value_normalized:
                continue
            # Skip label/identifier suffixes
            if any(name.lower().endswith(sfx) for sfx in label_suffixes):
                continue
            flagged = True
            matched_name = name
            break
        if flagged:
            self._antipatterns.append(
                (
                    node.lineno,
                    "hardcoded_secret",
                    matched_name or "<unknown>",
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Detect star imports (``from X import *``).

        Star imports pollute the namespace, hide dependency edges, and break
        static analysis tooling. Widely recognized anti-pattern (PEP 8, pylint
        W0401). Emits one edge per star-import statement.
        """
        for alias in node.names:
            if alias.name == "*":
                module = node.module or "<relative>"
                self._antipatterns.append(
                    (
                        node.lineno,
                        "star_import_use",
                        f"from {module} import *",
                    )
                )
                break
        self.generic_visit(node)

    def _check_mutable_default_args(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Detect mutable default arguments (list/dict/set/bytearray).

        Mutable defaults are evaluated once at function definition time and
        shared across all calls — a well-known source of bugs (PEP 8, pylint
        W0102). Emits one edge per offending default.
        """
        # args.defaults align with the LAST N positional/positional-only args
        defaults = list(node.args.defaults) + list(node.args.kw_defaults)
        for default in defaults:
            if default is None:
                continue
            is_mutable = False
            # Literal list/dict/set
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                is_mutable = True
            # Call to list()/dict()/set()/bytearray()
            elif isinstance(default, ast.Call) and isinstance(default.func, ast.Name):
                if default.func.id in {"list", "dict", "set", "bytearray"}:
                    is_mutable = True
            if is_mutable:
                self._antipatterns.append(
                    (
                        default.lineno,
                        "mutable_default_arg",
                        node.name,
                    )
                )

    def visit_For(self, node: ast.For) -> None:
        """Detect retry loops without backoff (for loops)."""
        if self._loop_contains_retry_without_backoff(node):
            self._antipatterns.append(
                (
                    node.lineno,
                    "retry_without_backoff",
                    "for_retry",
                )
            )
        self.generic_visit(node)

    def _loop_contains_retry_without_backoff(self, node: ast.AST) -> bool:
        """Detect retry loops that lack backoff.

        Requires ALL of:
          - loop iterates over range() OR is a while loop
          - body contains try/except
          - body does NOT contain sleep/backoff
          - at least one except body contains 'continue' (actual retry semantics)
            OR no except body exits the loop (break/return/raise)

        Precision exclusions:
          - except body begins with `break` → drain pattern, not retry
          - except body begins with `return` → one-shot, not retry
          - except handlers catch only queue.Empty / StopIteration → drain
          - while guard references terminated/stopped/done/finished/active
            state flag → event loop, not retry
        """
        # Check if loop iterates over range() or similar integer sequence
        is_retry_loop = False
        if isinstance(node, ast.For):
            if isinstance(node.iter, ast.Call):
                sym = self._extract_symbol(node.iter.func)
                is_retry_loop = sym == "range"
        elif isinstance(node, ast.While):
            # Event-loop guards (not retry): `while not self.is_terminated:`,
            # `while state.active:`, `while not done`, etc.
            guard_names = self._collect_name_refs(node.test)
            event_loop_markers = {
                "is_terminated",
                "is_running",
                "terminated",
                "stopped",
                "done",
                "finished",
                "active",
                "alive",
                "closed",
                "shutdown",
                "cancelled",
                "is_cancelled",
                "should_continue",
                "should_stop",
                "_running",
                "_active",
                "_alive",
            }
            if guard_names & event_loop_markers:
                return False
            is_retry_loop = True

        if not is_retry_loop:
            return False

        # Check if body contains sleep/backoff
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                sym = self._extract_symbol(child.func)
                if sym and any(s in sym for s in ("sleep", "time.sleep", "await asyncio.sleep")):
                    return False
            # await asyncio.wait_for(...) acts as a per-iteration timeout (backoff equivalent)
            if isinstance(child, ast.Await) and isinstance(child.value, ast.Call):
                sym = self._extract_symbol(child.value.func)
                if sym and "wait_for" in sym:
                    return False

        # Require at least one try/except where the pattern is actually a RETRY
        # (except: continue) rather than a DRAIN (except: break/return/raise).
        has_retry_semantics = False
        for child in ast.walk(node):
            if not isinstance(child, ast.Try):
                continue
            for handler in child.handlers:
                if not handler.body:
                    continue
                # Drain patterns: except X: break / return / raise
                first_stmt = handler.body[0]
                if isinstance(first_stmt, (ast.Break, ast.Return, ast.Raise)):
                    continue
                # Drain-specific exception types (queue.Empty, StopIteration)
                htype_name = self._get_handler_type_name(handler)
                if htype_name in {"Empty", "queue.Empty", "StopIteration", "StopAsyncIteration"}:
                    continue
                # Explicit retry: except: ...; continue
                if any(isinstance(s, ast.Continue) for s in handler.body):
                    has_retry_semantics = True
                    break
                # Implicit retry: handler neither breaks/returns/raises nor
                # has explicit continue, but loop body DOES continue by falling
                # through. Conservative: treat as retry only if handler body
                # has no terminal statements at top level.
                has_terminal = any(
                    isinstance(s, (ast.Break, ast.Return, ast.Raise)) for s in handler.body
                )
                if not has_terminal:
                    has_retry_semantics = True
                    break
            if has_retry_semantics:
                break

        return has_retry_semantics

    def _collect_name_refs(self, node: ast.AST) -> set[str]:
        """Collect all ast.Name.id and ast.Attribute.attr names referenced in node."""
        names: set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                names.add(child.id)
            elif isinstance(child, ast.Attribute):
                names.add(child.attr)
        return names

    def _get_handler_type_name(self, handler: ast.ExceptHandler) -> str | None:
        """Return the handler's exception type name (best-effort, first type only)."""
        htype = handler.type
        if isinstance(htype, ast.Name):
            return htype.id
        if isinstance(htype, ast.Attribute):
            # queue.Empty -> "queue.Empty"
            parts: list[str] = []
            cur: ast.expr = htype
            while isinstance(cur, ast.Attribute):
                parts.insert(0, cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.insert(0, cur.id)
            return ".".join(parts)
        return None

    def extract_edges(self) -> list[Edge]:
        """Convert antipattern detections to edges."""
        from agentic_core.adg.contracts.schema_util import canonical_name
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        for line_no, category, symbol in tqdm(self._antipatterns, desc="Processing", unit="item"):
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("antipattern_category", category),
                    edge_kind=category,
                    source_file=self._source_file,
                    line_no=line_no,
                    symbol=symbol,
                ),
            )
        return self.edges
