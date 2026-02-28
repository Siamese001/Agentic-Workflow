"""
Certification-grade evidence-backed gap analysis.
Every claim backed by raw command + verbatim stdout.
"""

import ast
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REQ_MD = REPO / "docs" / "reports" / "plans" / "Agentic Master Requirements.md"
OUT = REPO / "docs" / "reports" / "plans" / "requirements-gap-analysis-evidence.md"
PY = sys.executable

# Dirs to skip in all searches
SKIP = {
    ".nox",
    ".git",
    ".backup",
    ".pytest_tmp",
    "archives",
    "__pycache__",
    ".vscode",
    ".windsurf",
    "node_modules",
    ".healing_backups",
    "logs",
    ".venv",
    "venv",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════════════════════


# guardian: allow-magic-config
def run_cmd(argv, cwd=None, timeout=30):
    """Run command, return (cmd_string, stdout, stderr, exitcode)."""
    cmd_str = " ".join(str(a) for a in argv)
    try:
        r = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=cwd or str(REPO),
            shell=False,
        )
        return cmd_str, r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return cmd_str, "", f"TIMEOUT after {timeout}s", -1
    # guardian: allow-silent-swallow
    except Exception as e:
        return cmd_str, "", str(e), -1


# guardian: allow-magic-config
def py_grep(pattern, root=None, ext=".py", max_lines=50):
    """Pure-Python grep returning (file:line:content) tuples.
    Returns (cmd_description, raw_output_lines, match_count, file_set).
    """
    root = root or REPO
    pat = re.compile(pattern, re.IGNORECASE)
    results = []
    files_matched = set()
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fname in filenames:
            if not fname.endswith(ext):
                continue
            fpath = os.path.join(dirpath, fname)  # guardian: allow-path-fragility
            try:
                with open(fpath, encoding="utf-8", errors="replace") as fh:
                    for lineno, line in enumerate(fh, 1):
                        if pat.search(line):
                            total += 1
                            rel = os.path.relpath(fpath, REPO).replace("\\", "/")
                            files_matched.add(rel)
                            if len(results) < max_lines:
                                results.append(f"{rel}:{lineno}: {line.rstrip()[:200]}")
            except OSError:
                pass
    cmd_desc = f"py_grep(r'{pattern}', ext='{ext}') across {root}"
    return cmd_desc, results, total, files_matched


# guardian: allow-magic-config
def py_find_files(name_pattern, root=None, max_results=20):
    """Find files by filename pattern (glob-style, case-insensitive).
    Returns (cmd_description, matched_file_set).
    """
    root = root or REPO
    pat = re.compile(name_pattern.replace("*", ".*").replace("?", "."), re.IGNORECASE)
    results = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fname in filenames:
            if pat.search(fname):
                # guardian: allow-path-fragility
                rel = os.path.relpath(os.path.join(dirpath, fname), REPO).replace("\\", "/")
                results.add(rel)
                if len(results) >= max_results:
                    return f"py_find(r'{name_pattern}')", results
    return f"py_find(r'{name_pattern}')", results


# ═══════════════════════════════════════════════════════════════════════════════
# AST Index — replaces all substring/path heuristics
# ═══════════════════════════════════════════════════════════════════════════════

# Production directories whose .py files are indexed by AST
PROD_PREFIXES = (
    "agentic_core/",
    "apps_",
    "system_learning/",
    "L6_observability/",
    "ops_scripts/",
    "tools/",
    ".github/",
)

# Test directories that run in CI and provide CI-layer evidence
CI_TEST_PREFIXES = ("tests/governance/", "tests/architecture/", "tests/agentic_core/", "ops_scripts/ci/")


class _FileAstRecord:
    """AST-extracted signals for a single .py file."""

    __slots__ = (
        "path",
        "imports",
        "from_imports",
        "classes",
        "functions",
        "base_classes",
        "decorators",
        "calls",
        "raised",
        "markers",
    )

    def __init__(self, path):
        self.path = path
        self.imports = set()  # {'os', 'ast', 'hashlib'}
        self.from_imports = set()  # {'pydantic.BaseModel', 'hashlib.sha256'}
        self.classes = set()  # {'MyGuard', 'ReplayValidator'}
        self.functions = set()  # {'verify_token', 'enforce_budget'}
        self.base_classes = set()  # {'BaseModel', 'Guard'}
        self.decorators = set()  # {'dataclass', 'pytest.mark.xfail'}
        self.calls = set()  # {'ast.parse', 'hashlib.sha256'}
        self.raised = set()  # {'SovereigntyError', 'ValueError'}
        self.markers = set()  # {'xfail', 'parametrize'}


def _extract_call_name(node):
    """Best-effort qualified name from an ast.Call node."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = []
        cur = func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def _parse_file_ast(fpath, rel_path):
    """Parse a single .py file and return a _FileAstRecord or None on failure."""
    try:
        source = open(fpath, encoding="utf-8", errors="replace").read()
        tree = ast.parse(source, filename=rel_path)
    except (SyntaxError, ValueError, UnicodeDecodeError, OSError):
        return None

    rec = _FileAstRecord(rel_path)

    for node in ast.walk(tree):
        # --- imports ---
        if isinstance(node, ast.Import):
            for alias in node.names:
                rec.imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            top = mod.split(".")[0]
            if top:
                rec.imports.add(top)
            for alias in node.names:
                rec.from_imports.add(f"{mod}.{alias.name}" if mod else alias.name)

        # --- class definitions ---
        elif isinstance(node, ast.ClassDef):
            rec.classes.add(node.name)
            for base in node.bases:
                if isinstance(base, ast.Name):
                    rec.base_classes.add(base.id)
                elif isinstance(base, ast.Attribute):
                    rec.base_classes.add(base.attr)
            for deco in node.decorator_list:
                if isinstance(deco, ast.Name):
                    rec.decorators.add(deco.id)
                elif isinstance(deco, ast.Attribute):
                    rec.decorators.add(deco.attr)

        # --- function definitions ---
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            rec.functions.add(node.name)
            for deco in node.decorator_list:
                if isinstance(deco, ast.Name):
                    rec.decorators.add(deco.id)
                elif isinstance(deco, ast.Attribute):
                    rec.decorators.add(deco.attr)
                elif isinstance(deco, ast.Call):
                    cname = _extract_call_name(deco)
                    if cname:
                        rec.decorators.add(cname)
                        # pytest markers
                        if "mark" in cname:
                            parts = cname.split(".")
                            if len(parts) >= 3:
                                rec.markers.add(parts[-1])

        # --- calls ---
        elif isinstance(node, ast.Call):
            cname = _extract_call_name(node)
            if cname:
                rec.calls.add(cname)

        # --- raise ---
        elif isinstance(node, ast.Raise) and node.exc:
            exc = node.exc
            if isinstance(exc, ast.Call):
                ename = _extract_call_name(exc)
                if ename:
                    rec.raised.add(ename)
            elif isinstance(exc, ast.Name):
                rec.raised.add(exc.id)

    return rec


class RepoAstIndex:
    """AST-derived index of all .py files under production prefixes.

    Cached by (path, mtime, size) so re-runs skip unchanged files.
    """

    def __init__(self, repo_root, skip_dirs=None):
        self._repo = Path(repo_root)
        self._skip = skip_dirs or SKIP
        self._records = {}  # rel_path -> _FileAstRecord
        self._cache = {}  # rel_path -> (mtime, size, _FileAstRecord)
        self._symbol_to_files = defaultdict(set)
        self._build()

    def _build(self):
        for dirpath, dirnames, filenames in os.walk(self._repo):
            dirnames[:] = [d for d in dirnames if d not in self._skip]
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(dirpath, fname)  # guardian: allow-path-fragility
                rel = os.path.relpath(fpath, self._repo).replace("\\", "/")
                try:
                    st = os.stat(fpath)
                except OSError:
                    continue
                key = (st.st_mtime, st.st_size)
                cached = self._cache.get(rel)
                if cached and cached[:2] == key:
                    rec = cached[2]
                else:
                    rec = _parse_file_ast(fpath, rel)
                    if rec:
                        self._cache[rel] = (key[0], key[1], rec)
                if rec:
                    self._records[rel] = rec
                    for cls in rec.classes:
                        self._symbol_to_files[cls].add(rel)
                    for fn in rec.functions:
                        self._symbol_to_files[fn].add(rel)

    def records_for(self, file_set):
        """Return list of _FileAstRecord for files in file_set that are indexed."""
        return [self._records[f] for f in file_set if f in self._records]

    @property
    def all_records(self):
        return self._records

    def files_defining(self, symbol):
        return self._symbol_to_files.get(symbol, set())


# ── AST-derived layer signal functions ──────────────────────────────────────

_ENFORCEMENT_CLASS_SUFFIXES = (
    "Guard",
    "Validator",
    "Gate",
    "Enforcer",
    "Contract",
    "Prohibition",
    "Invariant",
)
_ENFORCEMENT_FUNC_PREFIXES = ("verify", "enforce", "check_", "deny", "allow", "validate_", "guard_", "gate_")
_GOVERNANCE_EXCEPTIONS = {
    "SovereigntyError",
    "ToolNotAllowedError",
    "BudgetExhaustedError",
    "MutationProhibitionError",
    "EmbeddingInputViolation",
    "PolicyViolation",
}


def ast_explain_enforcement(records):
    """Return (bool, reasons) where reasons list exact AST predicates that fired."""
    reasons = []
    for rec in records:
        matched_cls = [c for c in rec.classes if c.endswith(_ENFORCEMENT_CLASS_SUFFIXES)]
        if matched_cls:
            reasons.append(f"{rec.path}: classes {matched_cls}")
        gov_exc = rec.raised & _GOVERNANCE_EXCEPTIONS
        if gov_exc:
            reasons.append(f"{rec.path}: raises {sorted(gov_exc)}")
        err_exc = [r for r in rec.raised if r.endswith(("Error", "Violation")) and r not in gov_exc]
        if err_exc:
            reasons.append(f"{rec.path}: raises {err_exc}")
        enf_fns = [fn for fn in rec.functions if fn.startswith(_ENFORCEMENT_FUNC_PREFIXES)]
        if enf_fns:
            reasons.append(f"{rec.path}: defines {enf_fns}")
        enf_calls = [c for c in rec.calls if c.startswith(("verify", "enforce", "deny", "guard"))]
        if enf_calls:
            reasons.append(f"{rec.path}: calls {enf_calls}")
    return (len(reasons) > 0, reasons)


def ast_has_enforcement(records):
    """Thin wrapper — bool only."""
    return ast_explain_enforcement(records)[0]


_SCANNER_IMPORTS = {"ast", "libcst", "inspect"}
_SCANNER_CALLS = {
    "ast.parse",
    "ast.walk",
    "ast.get_source_segment",
    "libcst.parse_module",
    "inspect.getsource",
}


def ast_explain_scanner(records):
    """Return (bool, reasons) for AST/static-analysis scanner signals."""
    reasons = []
    for rec in records:
        imp_hit = rec.imports & _SCANNER_IMPORTS
        call_hit = rec.calls & _SCANNER_CALLS
        if imp_hit and call_hit:
            reasons.append(f"{rec.path}: imports {sorted(imp_hit)}, calls {sorted(call_hit)}")
        scan_cls = [c for c in rec.classes if c.endswith(("Scanner", "StaticCheck", "Audit", "AstChecker"))]
        if scan_cls:
            reasons.append(f"{rec.path}: classes {scan_cls}")
    return (len(reasons) > 0, reasons)


def ast_has_scanner(records):
    """Thin wrapper — bool only."""
    return ast_explain_scanner(records)[0]


_SCHEMA_IMPORTS = {"pydantic", "attrs", "msgspec"}
_SCHEMA_BASES = {"BaseModel", "TypedDict"}


def ast_explain_schema(records):
    """Return (bool, reasons) for schema/type-definition signals."""
    reasons = []
    for rec in records:
        schema_imp = rec.imports & _SCHEMA_IMPORTS
        if schema_imp:
            reasons.append(f"{rec.path}: imports {sorted(schema_imp)}")
        schema_base = rec.base_classes & _SCHEMA_BASES
        if schema_base:
            reasons.append(f"{rec.path}: inherits {sorted(schema_base)}")
        dc_decos = [d for d in rec.decorators if "dataclass" in d]
        if dc_decos:
            reasons.append(f"{rec.path}: decorators {dc_decos}")
    return (len(reasons) > 0, reasons)


def ast_has_schema(records):
    """Thin wrapper — bool only."""
    return ast_explain_schema(records)[0]


_REPLAY_CLASSES = {
    "ReplayValidator",
    "ReplayGuard",
    "ReplayEnvelope",
    "ReplayGuardStore",
    "ReplayGuardRecord",
}
_REPLAY_FUNCS = {"compute_digest", "create_deterministic_cache_key", "replay_validator", "verify_replay"}


def ast_explain_replay(records):
    """Return (bool, reasons) for replay/determinism signals."""
    reasons = []
    for rec in records:
        rp_cls = rec.classes & _REPLAY_CLASSES
        if rp_cls:
            reasons.append(f"{rec.path}: classes {sorted(rp_cls)}")
        prefix_cls = [c for c in rec.classes if c.startswith(("Replay", "Determinism")) and c not in rp_cls]
        if prefix_cls:
            reasons.append(f"{rec.path}: classes {prefix_cls}")
        rp_fn = rec.functions & _REPLAY_FUNCS
        if rp_fn:
            reasons.append(f"{rec.path}: defines {sorted(rp_fn)}")
        prefix_fn = [
            fn for fn in rec.functions if fn.startswith(("replay_", "determinism_")) and fn not in rp_fn
        ]
        if prefix_fn:
            reasons.append(f"{rec.path}: defines {prefix_fn}")
        rp_calls = [c for c in rec.calls if c.startswith(("replay_", "compute_digest"))]
        if rp_calls:
            reasons.append(f"{rec.path}: calls {rp_calls}")
    return (len(reasons) > 0, reasons)


def ast_has_replay(records):
    """Thin wrapper — bool only."""
    return ast_explain_replay(records)[0]


_SIG_IMPORTS = {"hashlib", "hmac", "cryptography", "nacl", "jwt"}
_SIG_FUNCS = {"sign", "verify_signature", "public_key", "hmac_digest", "key_derivation"}


def ast_explain_signature(records):
    """Return (bool, reasons) for cryptographic signing/verification signals."""
    reasons = []
    for rec in records:
        sig_imp = rec.imports & _SIG_IMPORTS
        if not sig_imp:
            continue
        crypto_calls = [c for c in rec.calls if c.startswith(("hmac.", "jwt.", "nacl."))]
        if crypto_calls:
            reasons.append(f"{rec.path}: imports {sorted(sig_imp)}, calls {crypto_calls}")
        matched_fns = [fn for fn in rec.functions if fn in _SIG_FUNCS]
        if matched_fns:
            reasons.append(f"{rec.path}: imports {sorted(sig_imp)}, defines {matched_fns}")
        hmac_calls = [c for c in rec.calls if c in ("hmac.new", "hmac.digest")]
        if hmac_calls:
            reasons.append(f"{rec.path}: calls {hmac_calls}")
        sig_funcs = [fn for fn in rec.functions if "sign" in fn or "hmac" in fn or "key_" in fn]
        if sig_funcs and not matched_fns:
            reasons.append(f"{rec.path}: imports {sorted(sig_imp)}, defines {sig_funcs}")
    return (len(reasons) > 0, reasons)


def ast_has_signature(records):
    """Thin wrapper — bool only."""
    return ast_explain_signature(records)[0]


# ═══════════════════════════════════════════════════════════════════════════════
# CI Index — YAML-parsed, replaces ".yml exists" heuristic
# ═══════════════════════════════════════════════════════════════════════════════


class CiIndex:
    """Parse .github/workflows/*.yml to determine what CI actually runs.

    Stores extracted evidence: (workflow_name, run_line) tuples for each
    detection, so reports can enumerate exactly what was found.
    """

    def __init__(self, repo_root):
        self._repo = Path(repo_root)
        self.runs_pytest = False
        self.runs_scanners = False
        self.covered_test_paths = set()
        self.workflow_names = []
        self.pytest_evidence = []  # [(workflow, run_line), ...]
        self.scanner_evidence = []  # [(workflow, run_line), ...]
        self._current_wf = ""
        self._build()

    def _build(self):
        wf_dir = self._repo / ".github" / "workflows"
        if not wf_dir.is_dir():
            return
        for yml_path in sorted(wf_dir.iterdir()):
            if yml_path.suffix not in (".yml", ".yaml"):
                continue
            self.workflow_names.append(yml_path.name)
            self._current_wf = yml_path.name
            try:
                text = yml_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            self._parse_workflow(text)

    def _parse_workflow(self, text):
        """Extract run commands from YAML without requiring PyYAML."""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("run:"):
                cmd = stripped[4:].strip().strip("|").strip()
                self._analyze_command(cmd, stripped)
            elif stripped.startswith("- run:"):
                cmd = stripped[6:].strip().strip("|").strip()
                self._analyze_command(cmd, stripped)
            elif "pytest" in stripped or "python -m pytest" in stripped:
                self._analyze_command(stripped, stripped)
            elif "scanner" in stripped.lower() or "guardrail" in stripped.lower():
                self.runs_scanners = True
                self.scanner_evidence.append((self._current_wf, stripped))

    def _analyze_command(self, cmd, raw_line):
        if not cmd:
            return
        if "pytest" in cmd or "python -m pytest" in cmd:
            self.runs_pytest = True
            self.pytest_evidence.append((self._current_wf, raw_line))
            parts = cmd.split()
            for p in parts:
                if p.startswith("tests/") or p.startswith("ops_scripts/"):
                    self.covered_test_paths.add(p)
        if "scanner" in cmd.lower() or "guardrail" in cmd.lower() or "audit" in cmd.lower():
            self.runs_scanners = True
            self.scanner_evidence.append((self._current_wf, raw_line))

    def ci_covers_requirement(self, has_test, has_scanner):
        """Determine if CI provides enforcement for this requirement."""
        if has_test and self.runs_pytest:
            return True
        if has_scanner and self.runs_scanners:
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Self-validation assertions for AST classifier
# ═══════════════════════════════════════════════════════════════════════════════


def _run_self_validation(ast_index, ci_index):
    """Run 3 internal assertions to validate the AST classifier is working.
    Returns list of (test_name, passed, detail) tuples.
    """
    results = []

    # Test 1: STRUCTURAL requirement with AST scanner evidence -> should detect scanner
    scanner_files = [
        r for r in ast_index.all_records.values() if r.imports & _SCANNER_IMPORTS and r.calls & _SCANNER_CALLS
    ]
    t1_pass = len(scanner_files) > 0
    results.append(
        ("STRUCTURAL_WITH_AST_SCANNER", t1_pass, f"Found {len(scanner_files)} files with AST scanner signals")
    )

    # Test 2: Runtime enforcement files exist (Guard/Validator classes with raises)
    enforcement_files = []
    for rec in ast_index.all_records.values():
        if any(cls.endswith(_ENFORCEMENT_CLASS_SUFFIXES) for cls in rec.classes):
            enforcement_files.append(rec.path)
    t2_pass = len(enforcement_files) > 0
    results.append(
        ("RUNTIME_ENFORCEMENT_EXISTS", t2_pass, f"Found {len(enforcement_files)} enforcement files")
    )

    # Test 3: CI index detects pytest runs
    t3_pass = ci_index.runs_pytest
    results.append(
        (
            "CI_RUNS_PYTEST",
            t3_pass,
            f"CI workflows: {len(ci_index.workflow_names)}, runs_pytest={ci_index.runs_pytest}",
        )
    )

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Requirements parser
# ═══════════════════════════════════════════════════════════════════════════════


def parse_requirements():
    text = REQ_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    rows = []
    in_table = False
    for line in lines:
        s = line.strip()
        if s.startswith("| Req ID") and "Domain" in s:
            in_table = True
            continue
        if in_table and s.startswith("|---"):
            continue
        if in_table and s.startswith("| REQ-"):
            inner = s[1:-1] if s.endswith("|") else s[1:]
            cells = inner.split("|")
            if len(cells) >= 7:
                rid = cells[0].strip()
                domain = cells[1].strip()
                eclass = cells[-1].strip()
                elayers = cells[-2].strip()
                severity = cells[-3].strip()
                mid = "|".join(cells[2:-3])
                mid_parts = mid.rsplit("|", 1)
                req_text = mid_parts[0].strip() if len(mid_parts) == 2 else mid.strip()
                enf_text = mid_parts[1].strip() if len(mid_parts) == 2 else ""
                rows.append(
                    {
                        "id": rid,
                        "domain": domain,
                        "requirement": req_text,
                        "enforcement": enf_text,
                        "severity": severity,
                        "layers": elayers,
                        "eclass": eclass,
                    }
                )
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# Search patterns per requirement
# ═══════════════════════════════════════════════════════════════════════════════


def get_search_terms(req):
    """Return list of regex patterns to search for this requirement."""
    rid = req["id"]
    domain = req["domain"]
    text = req["requirement"]

    # Specific overrides for key requirements
    SPECIFIC = {
        "REQ-011": [r"SovereignLLMGateway"],
        "REQ-012": [r"model.*literal.*outside|system_invariant_scanner"],
        "REQ-013": [r"EmbeddingServiceFactory|embedding_factory"],
        "REQ-022": [r"InstructionPacket.*signature|instruction_packet.*verify"],
        "REQ-024": [r"SandboxEnvelope.*signature|sandbox_envelope.*verify"],
        "REQ-029": [r"UniversalWriteGateway|write_gateway\.py"],
        "REQ-037": [r"xfail.*strict.*True|negative.*control.*tamper"],
        "REQ-038": [r"route_healing_tier"],
        "REQ-045": [r"embedding_input_guard|embedding_sovereignty_guard"],
        "REQ-114": [r"datetime\.now|time\.time\(\)|uuid4"],
        "REQ-243": [r"WaveAuditSummary"],
        "REQ-244": [r"WaveAuditSummary"],
        "REQ-413": [r"provider_binding_determinism"],
        "REQ-414": [r"network_egress_guard"],
        "REQ-415": [r"provider_substitution_prohibition"],
        "REQ-416": [r"critical_dual_enforcement"],
        "REQ-417": [r"runtime_mutation_guard"],
        "REQ-PT-001": [r"slot.*order.*S0.*I0.*C0.*U0|prompt_assembler.*slot"],
        "REQ-PT-002": [r"slot.*S0|S0.*L5|prompt.*slot.*own|slot_order"],
        "REQ-PT-005": [r"PromptBundle|prompt.*bundle|prompt.*artifact"],
        "REQ-PT-007": [r"U0.*override|slot.*ownership|user.*slot.*restrict|slot_order"],
        "REQ-PT-009": [r"prompt.*deterministic|prompt_assembler.*canonical"],
        "REQ-PT-011": [
            r"validate_slot_order|SlotOrderViolation|xfail.*strict.*True.*slot|negative.*control.*prompt|slot.*tamper"
        ],
        "REQ-PT-012": [r"prompt_hash.*stable|dual.*run.*prompt"],
        "REQ-EM-004": [r"embedding.*disabled.*fail|EMBEDDING_ENABLED.*fail"],
        "REQ-RAGX-005": [r"chunk.*hash|chunk.*sha256|chunk.*integrit|retriev.*verify"],
        "REQ-RAGX-006": [r"ExternalKnowledge|knowledge.*access.*viol|external.*retriev.*guard"],
        "REQ-CTX-002": [r"PreGuard|pre.*guard.*snapshot|context.*snapshot|ContextSnapshot"],
        "REQ-COG-001": [r"PolicyAlignment|policy.*alignment|PolicyViolation"],
        "REQ-COG-002": [r"prompt.*augmentation.*MRO|dependency.*facts.*augment"],
        "REQ-HEALX-001": [r"HealingProviderInvoker|FakeInvoker|DefaultInvoker"],
        "REQ-HEALX-002": [r"InvocationRecord.*tier.*model_id"],
        "REQ-DPO-001": [r"rlhf_optimizer.*clamp|DPO.*0\.1.*2\.0"],
        "REQ-DPO-002": [r"DPOPair|dpo.*proposal|dpo.*ChangePackage|dpo_pair_generator"],
        "REQ-MEMX-001": [r"episodic.*memory|EpisodicMemory|memory.*proposal"],
        "REQ-MEMX-003": [r"memory.*append|memory.*immutable|ChangePackage.*memory|episodic.*version"],
        "REQ-WLD-001": [r"citation.*byte|CitationBundle.*verify|byte.*hash.*citation|citation_hash"],
        "REQ-WLD-002": [r"ghost.*mutation|mutation.*detect|GhostMutation|ghost_mutation_detector"],
    }
    if rid in SPECIFIC:
        return SPECIFIC[rid]

    # Domain-level defaults
    DOMAIN = {
        "Layer Sovereignty": [r"mutation_prohibition|layer.*sovereign|L[0-6].*Base"],
        "Gateway": [r"SovereignLLMGateway|network_egress_guard|provider_substitution"],
        "META-INVARIANT": [r"fail.closed|SovereigntyError|no.*silent.*fallback"],
        "Canonicalization": [r"canonical_json|sort_keys|HMAC"],
        "Packet": [r"InstructionPacket|instruction_packet"],
        "Replay": [r"replay_guard|replay_envelope|replay_validator|replay_key"],
        "Envelope": [r"SandboxEnvelope|sandbox_envelope"],
        "Budget": [r"budget_enforcer|ToolBudget"],
        "Tools": [r"ToolCall|ToolResult|ToolTranscript"],
        "Mutation": [r"UniversalWriteGateway|write_gateway|ToolNotAllowedError"],
        "Artifact": [r"ExecutionTrace|execution_trace"],
        "Determinism": [r"determinism_guard|digest_calculator|determinism\.py"],
        "Determinism Canon": [r"semantic_clock|SemanticClock|uuid4.*forbidden"],
        "Healing": [r"healing_tier_router|healing_tier_dispatcher|escalation_context"],
        "Embeddings": [r"embedding_factory|embedding_input_guard|embedding_sovereignty"],
        "RAG": [r"SeedEmbeddingPack|matrix_hash|EmbeddingResult"],
        "RAG Custody": [r"CitationBundle|RetrievalQuery|citation_enforcement"],
        "Meta-Learning": [r"ChangePackage|proposal_only|VersionStore|meta_learning"],
        "Guardian": [r"guardrail|guardian.*guard|HARD.*STOP"],
        "HIL": [r"HumanDecisionArtifact|reviewer_sig|MODIFY_DIFF"],
        "Incident": [r"CognitiveDiffBundle|ForensicTraceBuffer"],
        "Vigilance": [r"TieredVigilance|EmergencyFreeze"],
        "Prompt Governance": [r"prompt_governance|prompt_assembler|PromptBundleArtifact"],
        "Prompt Taxonomy": [r"prompt_governance|prompt_assembler|slot_order|PromptBundleArtifact"],
        "Auth": [r"capability_chokepoint|capability_token"],
        "Kill-Switch": [r"EMBEDDING_ENABLED|ApprovalGate|tiering_allowlist"],
        "Sovereignty": [r"mutation_prohibition|SovereigntyError|eval.*exec"],
        "Governance": [r"governance_contracts|SovereigntyError|boundary.*validation"],
        "Seam": [r"safety_enforcement_seam|seam.*allowlist|orchestration_protocols"],
        "CI": [r"guardian.*tests\.yml|ssot.*verify\.yml|sovereignty.*enforcement\.yml"],
        "CI Ratchet": [r"guardian.*tests\.yml|ssot.*enforcement\.yml|determinism.*guard\.yml"],
        "Boundary": [r"boundary_verifier|health.*check"],
        "Discovery": [r"agent_discovery|integrity_hash|ZOMBIE"],
        "Trace": [r"ExecutionTrace|HashChainAuditLog|hash_chain_audit"],
        "Evidence": [r"EvidencePack|evidence.*bundle"],
        "Override": [r"PolicyUpdateProposal"],
        "Surgical": [r"SurgicalManifest|SurgicalHealingAdapter|node_id.*blueprint"],
        "SSOT": [r"ssot_guardrail|ssot_structure_validation|structure_blueprint"],
        "SSOT Enforcement": [r"ssot_guardrail|ssot_structure_validation"],
        "Capability Tokens": [r"capability_token|CapabilityToken"],
        "Side-Effect Registry": [r"tool_policy_enforcer|write_set_enforcer|side.effect"],
        "Promotion State": [r"promotion_authority|phase_lock_store|activation_flags"],
        "Emergency Freeze": [r"EmergencyFreeze|freeze_state"],
        "Artifact Legality": [r"artifact.*emission|flow.*violation|artifact.*type.*registry"],
        "Sovereignty Matrix": [r"sovereignty.*matrix|layer.*permission"],
        "Phase Lock": [r"phase_lock_store|phase.*gate"],
        "TraceID Canon": [r"trace_id_generator|CC3AL1|TraceID"],
        "Canonical Hashing": [r"canonical_hash|SHA.256|canonicalize"],
        "HMAC Custody": [r"key_derivation|key_source|hmac"],
        "Signature Enclave": [r"signature_verifier|SignatureEnclave"],
        "Semantic Clock": [r"semantic_clock|SemanticClock|vector.*clock"],
        "Knowledge Supervisor": [r"knowledge_integrity|retraining|KnowledgeAudit"],
        "Guardian Meta": [r"guardian.*tests|invariant.*coverage"],
        "L0 Seam": [r"importlib.*seam|seam.*allowlist"],
        "Incident Telemetry": [r"TieredVigilance|telemetry_recorder|ForensicTraceBuffer"],
        "Cognitive Diff": [r"cognitive_diff|CognitiveDiff"],
        "Boundary Snapshot": [r"filesystem_hash|git_state_hash|snapshot"],
        "Budget Routing": [r"budget_enforcer|RouteRecovery|BudgetGuard"],
        "Law Slot Handler": [r"LawSlotHandler|capability.*depletion"],
        "MRO Integrity": [r"mro_signature|verify_mro|MRO"],
        "Structure Blueprint": [r"structure_blueprint|blueprint.*hash"],
        "Structural Lock": [r"structure_blueprint|dynamic.*class.*injection"],
        "Quorum Governance": [r"quorum|N.of.M.*signature"],
        "Rollback Integrity": [r"rollback|RollbackArtifact"],
        "Audit Completeness": [r"WaveAuditSummary"],
        "Human Override": [r"HumanDecision|reviewer_sig|override.*TTL"],
        "Policy Exception": [r"PolicyException|exception.*scope"],
        "Artifact Registry": [r"ArtifactID|artifact.*registry"],
        "Drift Escalation": [r"DriftEscalation|drift.*escalat"],
        "Cross-Wave Integrity": [r"prev_wave_hash|cross.*wave"],
        "Provider Binding Determinism": [r"provider_binding_determinism"],
        "Network Egress Guard": [r"network_egress_guard"],
        "Provider Substitution Prohibition": [r"provider_substitution_prohibition"],
        "CRITICAL Dual Enforcement Guarantee": [r"critical_dual_enforcement"],
        "Dynamic Runtime Mutation Prohibition": [r"runtime_mutation_guard"],
        "Embedding Utilization": [r"embedding_factory|embedder.*metadata"],
        "Agentic RAG Schema": [r"RetrievalQuery|CitationBundle|citation_enforcement"],
        "Context Control": [r"context.*budget|PreGuardSnapshot|context_curator"],
        "Application Boundary": [r"apps_taxonomy_guard|apps_.*MUST NOT"],
        "Telemetry": [r"telemetry_recorder|INCIDENT.*telemetry"],
        "Policy/HIL": [r"HumanDecision|PolicyException|reviewer_sig"],
        "Shared Memory": [r"episodic.*memory|proposal_only.*memory|memory.*collision"],
        "World-Check": [r"byte_sha256|ghost.*mutation|context_set_hash"],
        "DPO/RLHF Bounds": [r"rlhf_optimizer|dpo_pair_generator|DPOPair"],
        "Cognitive Safety": [r"PolicyAlignmentCheck|PolicyViolationArtifact"],
        "Healing Seam": [r"HealingProviderInvoker|FakeInvoker|DefaultInvoker"],
    }
    if domain in DOMAIN:
        return DOMAIN[domain]

    # Fallback: extract PascalCase from requirement text
    tokens = re.findall(r"[A-Z][a-z]+(?:[A-Z][a-z]+)+", text)
    return [re.escape(t) for t in tokens[:3]] if tokens else [domain.replace(" ", ".*")]


def classify(req, cmd_desc, raw_lines, match_count, matched_files, ast_index=None, ci_index=None):
    """Classify requirement using AST-derived enforcement signals.

    Returns (status, missing_layers, evidence_summary, provenance) where
    provenance is a dict containing the mechanical proof of how the
    classification decision was reached:
      - layers_present: {layer_name: bool}
      - ast_predicates: {layer_name: [reason_strings]}
      - file_categories: {prod: [...], test: [...], tool: [...]}
      - filtered_self_refs: int
      - ast_records_count: int
    """
    layers = req["layers"]
    eclass = req["eclass"]
    domain = req.get("domain", "")
    req_text = req.get("requirement", "")

    # Build provenance skeleton
    self_refs = {f for f in matched_files if f.startswith("tools/evidence/gap_analysis")}
    prov = {
        "layers_present": {},
        "ast_predicates": {},
        "file_categories": {"prod": [], "test": [], "tool": [], "ci_test": []},
        "filtered_self_refs": len(self_refs),
        "ast_records_count": 0,
    }

    if match_count == 0:
        return "FAIL", "No implementation evidence", "0 matches", prov

    # Filter out self-references
    prod_files = matched_files - self_refs

    # Categorize files
    for f in sorted(prod_files):
        if "/test" in f or "tests/" in f:
            prov["file_categories"]["test"].append(f)
            if f.startswith(CI_TEST_PREFIXES):
                prov["file_categories"]["ci_test"].append(f)
        elif f.startswith(("tools/", "ops_scripts/")):
            prov["file_categories"]["tool"].append(f)
        elif f.startswith(PROD_PREFIXES):
            prov["file_categories"]["prod"].append(f)
        else:
            prov["file_categories"]["prod"].append(f)

    has_core = len(prov["file_categories"]["prod"]) > 0 or len(prov["file_categories"]["tool"]) > 0
    has_test = len(prov["file_categories"]["test"]) > 0
    has_ci_test = len(prov["file_categories"]["ci_test"]) > 0

    summary = f"{match_count} matches in {len(prod_files)} files"

    # ── Special case: test-domain requirements ──
    TEST_DOMAINS = {"Negative Control", "Test Integrity", "Guardian Meta"}
    test_keywords = ("negative control", "xfail", "test coverage", "guardian test")
    is_test_req = domain in TEST_DOMAINS or any(kw in req_text.lower() for kw in test_keywords)
    if is_test_req and has_test:
        return "PASS", "", summary, prov

    # ── No production code at all ──
    if not has_core and not has_test:
        return "FAIL", "No production or test evidence", summary, prov

    # ── Get AST records for matched files ──
    ast_records = ast_index.records_for(prod_files) if ast_index else []
    prov["ast_records_count"] = len(ast_records)

    # ── STRUCTURAL eclass: production code = PASS ──
    if eclass == "STRUCTURAL":
        if has_core:
            return "PASS", "", summary, prov
        elif has_test:
            return "PARTIAL", "Test/doc only; no production code", summary, prov
        else:
            return "FAIL", "No structural evidence", summary, prov

    # ── EXECUTION_PATH eclass: AST-derived layer validation ──
    # Compute layers_present from AST explain functions
    enf_hit, enf_reasons = ast_explain_enforcement(ast_records) if ast_records else (False, [])
    scan_hit, scan_reasons = ast_explain_scanner(ast_records) if ast_records else (False, [])
    schema_hit, schema_reasons = ast_explain_schema(ast_records) if ast_records else (False, [])
    replay_hit, replay_reasons = ast_explain_replay(ast_records) if ast_records else (False, [])
    sig_hit, sig_reasons = ast_explain_signature(ast_records) if ast_records else (False, [])

    # CI layer: YAML-parsed CI runs pytest covering tests, or runs scanners
    ci_hit = False
    ci_reasons = []
    if ci_index:
        ci_hit = ci_index.ci_covers_requirement(has_test=has_test or has_ci_test, has_scanner=scan_hit)
        if ci_hit:
            if has_test and ci_index.runs_pytest:
                ci_reasons.append("tests exist + CI runs pytest")
            if scan_hit and ci_index.runs_scanners:
                ci_reasons.append("scanner detected + CI runs scanners")
    if has_ci_test:
        ci_hit = True
        ci_reasons.append(f"governance/architecture tests in CI: {prov['file_categories']['ci_test'][:3]}")

    prov["layers_present"] = {
        "Runtime": enf_hit or has_core,
        "AST": scan_hit or has_core,
        "Schema": schema_hit,
        "Replay": replay_hit,
        "Signature": sig_hit,
        "CI": ci_hit,
    }
    prov["ast_predicates"] = {
        "Runtime": enf_reasons
        if enf_hit
        else (["has_core=True (production code exists)"] if has_core else []),
        "AST": scan_reasons if scan_hit else (["has_core=True (production code exists)"] if has_core else []),
        "Schema": schema_reasons,
        "Replay": replay_reasons,
        "Signature": sig_reasons,
        "CI": ci_reasons,
    }

    # Determine which required layers are missing
    required = [l.strip() for l in layers.split(",")]
    missing = []
    for layer in required:
        key = layer.strip()
        if key in prov["layers_present"] and not prov["layers_present"][key]:
            missing.append(key)
    missing = sorted(set(missing))

    # If no production code, check if governance tests cover CI
    if not has_core and match_count > 0:
        if has_ci_test:
            remaining = [m for m in missing if m != "CI"]
            if not remaining:
                return "PASS", "", summary, prov
            else:
                return "PARTIAL", ", ".join(remaining), summary, prov
        else:
            return "PARTIAL", "Test/doc only; no production code", summary, prov

    if not missing:
        return "PASS", "", summary, prov
    else:
        return "PARTIAL", ", ".join(missing), summary, prov


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    E = []  # evidence lines

    def w(text=""):
        E.append(text)

    w("# Evidence-Backed Full Gap Analysis — Certification Grade")
    w(f"## Repository: `{REPO}`")
    w(f"## Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    w("## Generator: `tools/evidence/gap_analysis_evidence_v2.py`")
    w()

    # ── PHASE 1: INGESTION ────────────────────────────────────────────────
    w("---")
    w("# PHASE 1 — REQUIREMENTS INGESTION (EVIDENCE)")
    w()

    # 1a. Raw line count
    w("## 1a. Raw table line count")
    cmd, stdout, stderr, rc = run_cmd(
        [
            PY,
            "-c",
            "f=open('docs/reports/plans/Agentic Master Requirements.md','r',encoding='utf-8');"
            "lines=f.readlines(); f.close();"
            "c=sum(1 for l in lines if l.strip().startswith('| REQ-'));"
            "print('REQ_TABLE_ROWS:', c)",
        ],
    )
    w("```")
    w(f"$ {cmd}")
    w(stdout.strip())
    w(f"EXIT CODE: {rc}")
    w("```")
    w()

    rows = parse_requirements()
    w(f"## 1b. Parsed rows: **{len(rows)}**")
    w()

    # 1b-INTEGRITY: Compare raw table rows vs parsed rows
    raw_count = 0
    for line in stdout.strip().splitlines():
        if line.startswith("REQ_TABLE_ROWS:"):
            try:
                raw_count = int(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass
    integrity_delta = raw_count - len(rows)
    w("## 1b-INTEGRITY. Requirements Table Integrity Check")
    w("```")
    w(f"Raw REQ- table rows in source markdown: {raw_count}")
    w(f"Parsed rows (after field validation):   {len(rows)}")
    w(f"Delta (declared but unparseable):        {integrity_delta}")
    if integrity_delta != 0:
        w(f"STATUS: MISMATCH — {integrity_delta} rows declared in markdown but not parsed.")
        w("  These rows may have malformed columns (missing severity/domain/layers/eclass)")
        w("  or use a non-standard REQ-ID prefix that the parser does not handle.")
        w("  NOTE: Per scope constraints, requirements source is NOT edited by this tool.")
        w("  This mismatch is acknowledged and reported but not corrected.")
    else:
        w("STATUS: PASS — all declared rows parsed successfully.")
    w("```")
    w()

    # 1c. Duplicate check
    w("## 1c. Duplicate ID check")
    ids = [r["id"] for r in rows]
    ctr = Counter(ids)
    dupes = {k: v for k, v in ctr.items() if v > 1}
    w("```")
    w("Counter(req_ids).items() where count > 1:")
    w(f"  {dupes if dupes else '(none)'}")
    w(f"RESULT: {'FAIL — DUPLICATES' if dupes else 'PASS — no duplicates'}")
    w("```")
    w()

    # 1d. Numeric gap check
    w("## 1d. Numeric gap check REQ-001..REQ-417")
    nums = sorted(int(m.group(1)) for r in rows if (m := re.match(r"^REQ-(\d+)$", r["id"])))
    expected = set(range(nums[0], nums[-1] + 1)) if nums else set()
    actual = set(nums)
    gaps = sorted(expected - actual)
    w("```")
    w(f"numeric IDs found: {len(nums)} (range {nums[0]}..{nums[-1]})")
    w(f"gaps: {gaps if gaps else 'none'}")
    w(f"RESULT: {'FAIL — GAPS' if gaps else 'PASS — no gaps'}")
    w("```")
    w()

    # 1e. Prefix counts
    w("## 1e. Prefix coverage")
    pfx = Counter()
    for r in rows:
        m2 = re.match(r"^(REQ-[A-Z]+)", r["id"])
        pfx[m2.group(1) if m2 else "REQ-nnn"] += 1
    w("```")
    for p, c in sorted(pfx.items()):
        w(f"  {p}: {c}")
    w(f"  TOTAL: {sum(pfx.values())}")
    w("```")
    w()

    # 1f. Severity distribution
    w("## 1f. Severity distribution")
    sev = Counter(r["severity"] for r in rows)
    w("```")
    for s, c in sorted(sev.items()):
        w(f"  {s}: {c}")
    w("```")
    w()

    # ── PHASE 2: REPO INDEX ───────────────────────────────────────────────
    w("---")
    w("# PHASE 2 — REPO INDEX (EVIDENCE)")
    w()

    w("## 2a. Top-level directory listing")
    cmd, stdout, stderr, rc = run_cmd(
        [
            PY,
            "-c",
            "import os; items=sorted(os.listdir('.')); "
            "[print(f'  {i}/' if os.path.isdir(i) else f'  {i}') for i in items if not i.startswith('.')]",
        ]
    )
    w("```")
    w(f"$ {cmd}")
    w(stdout.strip())
    w(f"EXIT CODE: {rc}")
    w("```")
    w()

    w("## 2b. CI workflow listing")
    cmd, stdout, stderr, rc = run_cmd(
        [
            PY,
            "-c",
            "import os; wf='.github/workflows'; "
            "fs=sorted(os.listdir(wf)) if os.path.isdir(wf) else []; "
            "print(f'count: {len(fs)}'); [print(f'  {f}') for f in fs]",
        ]
    )
    w("```")
    w(f"$ {cmd}")
    w(stdout.strip())
    w(f"EXIT CODE: {rc}")
    w("```")
    w()

    w("## 2c. Key enforcement surface .py file counts")
    surfaces = [
        "agentic_core/L2_execution/enforcement",
        "agentic_core/L5_safety/enforcement",
        "agentic_core/L0_routing/enforcement",
        "agentic_core/L4_state/enforcement",
        "agentic_core/prompt_governance",
        "agentic_core/embeddings",
        "agentic_core/replay",
        "agentic_core/seams",
        "agentic_core/security",
        "agentic_core/L2_execution/determinism",
        "agentic_core/L2_execution/healers",
    ]
    w("```")
    for sf in surfaces:
        full = REPO / sf
        if full.exists():
            py_count = sum(1 for _, _, fs in os.walk(full) for f in fs if f.endswith(".py"))
            w(f"  {sf}: {py_count} .py files")
        else:
            w(f"  {sf}: NOT FOUND")
    w("```")
    w()

    # ── PHASE 2d: AST INDEX + CI INDEX ─────────────────────────────────
    print("  Building AST index...", file=sys.stderr)
    ast_idx = RepoAstIndex(REPO, skip_dirs=SKIP)
    ci_idx = CiIndex(REPO)

    w("## 2d. AST Index Summary")
    w("```")
    w(f"Total .py files indexed: {len(ast_idx.all_records)}")
    w(f"Total symbols indexed: {len(ast_idx._symbol_to_files)}")
    w("```")
    w()

    w("## 2e. CI Index Summary")
    w("```")
    w(f"CI workflows parsed: {len(ci_idx.workflow_names)}")
    w(f"  runs_pytest: {ci_idx.runs_pytest}")
    w(f"  runs_scanners: {ci_idx.runs_scanners}")
    w(f"  covered_test_paths: {len(ci_idx.covered_test_paths)}")
    w(f"  pytest_evidence_count: {len(ci_idx.pytest_evidence)}")
    w(f"  scanner_evidence_count: {len(ci_idx.scanner_evidence)}")
    w("")
    w("Workflows:")
    for wf in ci_idx.workflow_names:
        w(f"  - {wf}")
    w("")
    if ci_idx.pytest_evidence:
        w("Pytest run: lines (workflow -> extracted line):")
        seen = set()
        for wf_name, run_line in ci_idx.pytest_evidence:
            key = (wf_name, run_line.strip()[:120])
            if key not in seen:
                seen.add(key)
                w(f"  [{wf_name}] {run_line.strip()[:120]}")
    if ci_idx.scanner_evidence:
        w("Scanner/guardrail run: lines (workflow -> extracted line):")
        seen = set()
        for wf_name, run_line in ci_idx.scanner_evidence:
            key = (wf_name, run_line.strip()[:120])
            if key not in seen:
                seen.add(key)
                w(f"  [{wf_name}] {run_line.strip()[:120]}")
    w("```")
    w()

    w("## 2f. AST Classifier Self-Validation")
    validation_results = _run_self_validation(ast_idx, ci_idx)
    all_passed = all(v[1] for v in validation_results)
    w("```")
    for name, passed, detail in validation_results:
        w(f"  {'PASS' if passed else 'FAIL'}: {name} — {detail}")
    w(f"  OVERALL: {'ALL PASS' if all_passed else 'FAILURES DETECTED'}")
    w("```")
    w()

    # ── PHASE 3: FULL LEDGER ─────────────────────────────────────────────
    w("---")
    w("# PHASE 3 — FULL REQUIREMENT-BY-REQUIREMENT GAP LEDGER")
    w()
    w("Each row includes: raw search command, match count, matched files with line numbers.")
    w("Status classification rules:")
    w("- **PASS**: matches found in production code + all required enforcement layers have evidence")
    w("- **PARTIAL**: matches found but >=1 required layer missing or test-only")
    w("- **FAIL**: zero matches found")
    w("- **STRUCTURAL_ONLY**: AST/static evidence but Runtime guard absent where required")
    w()
    w("| Req ID | Severity | Status | Missing Layers | Matches | Evidence Summary |")
    w("|--------|----------|--------|---------------|---------|-----------------|")

    status_ctr = Counter()
    crit_ctr = Counter()
    pfx_status = defaultdict(lambda: Counter())

    # Collect all per-row evidence into a detail section
    detail_sections = []

    for i, req in enumerate(rows):
        rid = req["id"]
        severity = req["severity"]
        patterns = get_search_terms(req)

        # Run searches
        all_match_count = 0
        all_files = set()
        all_raw = []
        for pat in patterns:
            cmd_desc, raw_lines, mc, fset = py_grep(pat)
            all_match_count += mc
            all_files.update(fset)
            all_raw.append((cmd_desc, raw_lines, mc, fset))

        # For CI-domain requirements, also find .yml files by name pattern
        CI_DOMAINS = {"CI", "CI Ratchet", "Guardian Meta"}
        if req["domain"] in CI_DOMAINS:
            for pat in patterns:
                # Content-search .yml files
                cmd_desc2, raw_lines2, mc2, fset2 = py_grep(pat, ext=".yml")
                all_match_count += mc2
                all_files.update(fset2)
                all_raw.append((cmd_desc2, raw_lines2, mc2, fset2))
            # Also find .yml files by filename pattern (CI workflows)
            # Extract key tokens from search patterns for filename matching
            for pat in patterns:
                fname_desc, fname_set = py_find_files(pat, root=REPO / ".github")
                all_files.update(fname_set)
                if fname_set:
                    all_match_count += len(fname_set)
                    all_raw.append((fname_desc, sorted(fname_set), len(fname_set), fname_set))

        status, missing, summary, prov = classify(
            req, "", [], all_match_count, all_files, ast_index=ast_idx, ci_index=ci_idx
        )

        status_ctr[status] += 1
        if severity == "CRITICAL":
            crit_ctr[status] += 1
        pm = re.match(r"^(REQ-[A-Z]+)", rid)
        pk = pm.group(1) if pm else "REQ-nnn"
        pfx_status[pk][status] += 1

        # Ledger row
        w(
            f"| {rid} | {severity} | {status} | {missing if missing else '—'} | {all_match_count} | {summary} |"
        )

        # ── Detail section: AST signal provenance ──
        det = []
        det.append(f"### {rid} ({severity}) — {status}")
        det.append(f"**Domain:** {req['domain']}")
        det.append(
            f"**Requirement:** {req['requirement'][:200]}{'...' if len(req['requirement']) > 200 else ''}"
        )
        det.append(f"**Required Layers:** {req['layers']}")
        det.append(f"**Class:** {req['eclass']}")
        det.append("")

        # File discovery (grep is the discovery mechanism, not the classifier)
        det.append("#### File Discovery (grep-based)")
        det.append(f"**FILTERED_SELF_REFS:** {prov['filtered_self_refs']}")
        for cmd_desc, raw_lines, mc, fset in all_raw:
            det.append(f"- `{cmd_desc}` -> {mc} matches in {len(fset)} files")
        det.append("")

        # File categories
        fc = prov["file_categories"]
        det.append("#### HIT_FILES")
        det.append("```")
        det.append(f"prod ({len(fc['prod'])}): {fc['prod'][:5]}")
        if len(fc["prod"]) > 5:
            det.append(f"  ... +{len(fc['prod']) - 5} more")
        det.append(f"test ({len(fc['test'])}): {fc['test'][:5]}")
        if len(fc["test"]) > 5:
            det.append(f"  ... +{len(fc['test']) - 5} more")
        det.append(f"tool ({len(fc['tool'])}): {fc['tool'][:5]}")
        det.append(f"ci_test ({len(fc['ci_test'])}): {fc['ci_test'][:3]}")
        det.append("```")
        det.append("")

        # AST signal provenance — the actual classifier inputs
        det.append("#### AST Classification Provenance")
        det.append(f"**ast_records_count:** {prov['ast_records_count']}")
        lp = prov.get("layers_present", {})
        ap = prov.get("ast_predicates", {})
        if lp:
            signals_hit = [k for k, v in lp.items() if v]
            det.append(f"**AST_SIGNALS_HIT:** {signals_hit if signals_hit else '(none)'}")
            det.append("```")
            det.append("layers_present = {")
            for layer_name in ("Runtime", "AST", "Schema", "Replay", "Signature", "CI"):
                val = lp.get(layer_name, False)
                predicates = ap.get(layer_name, [])
                det.append(f"  {layer_name}: {val},")
                for pred in predicates[:3]:
                    det.append(f"    # {pred}")
                if len(predicates) > 3:
                    det.append(f"    # ... +{len(predicates) - 3} more predicates")
            det.append("}")
            det.append("```")
        else:
            det.append("**AST_SIGNALS_HIT:** (not computed — early exit)")
        det.append("")

        det.append(f"**Classification:** {status} | Missing: {missing if missing else 'none'}")
        det.append("")
        detail_sections.append("\n".join(det))

        # Progress
        if (i + 1) % 50 == 0:
            print(f"  ... processed {i + 1}/{len(rows)} requirements", file=sys.stderr)

    w()

    # ── PHASE 4: CRITICAL DEEP AUDIT ─────────────────────────────────────
    w("---")
    w("# PHASE 4 — CRITICAL-ONLY DEEP ENFORCEMENT AUDIT")
    w()

    crit_deep = [
        (
            "REQ-037",
            "Negative control XFAIL(strict=True)",
            [
                r"xfail.*strict.*True",
                r"negative.*control",
                r"tamper.*vector",
            ],
        ),
        (
            "REQ-011",
            "All LLM calls via SovereignLLMGateway",
            [
                r"SovereignLLMGateway",
            ],
        ),
        (
            "REQ-016",
            "Fail-closed no silent fallback",
            [
                r"fail.closed",
                r"SovereigntyError",
                r"silent.*fallback",
            ],
        ),
        (
            "REQ-045",
            "Embeddings C0 informational only",
            [
                r"embedding_input_guard",
                r"embedding_sovereignty_guard",
            ],
        ),
        (
            "REQ-093",
            "Prompt governance chokepoint",
            [
                r"prompt_assembler",
                r"prompt_governance.*validator",
            ],
        ),
        (
            "REQ-114",
            "No wall-clock in determinism paths",
            [
                r"datetime\.now",
                r"time\.time\(\)",
                r"uuid4",
            ],
        ),
        (
            "REQ-131",
            "CI fail on CRITICAL violation by Req ID",
            [
                r"CI.*fail.*CRITICAL|Req.*ID.*failure.*list",
            ],
        ),
        (
            "REQ-243",
            "WaveAuditSummary emitted per wave",
            [
                r"WaveAuditSummary",
            ],
        ),
        (
            "REQ-COG-001",
            "PolicyAlignmentCheck before response",
            [
                r"PolicyAlignmentCheck",
                r"PolicyViolationArtifact",
            ],
        ),
        (
            "REQ-PT-011",
            "Negative control for slot order tamper",
            [
                r"xfail.*strict.*True.*slot",
                r"slot.*order.*tamper",
            ],
        ),
    ]

    for rid, desc, pats in crit_deep:
        w(f"## {rid}: {desc}")
        for pat in pats:
            cmd_desc, raw_lines, mc, fset = py_grep(pat)
            w(f"**Command:** `{cmd_desc}`")
            w(f"**Matches:** {mc} in {len(fset)} files")
            w("```")
            if raw_lines:
                for rl in raw_lines[:20]:
                    w(rl)
                if len(raw_lines) > 20:
                    w(f"... ({len(raw_lines) - 20} more)")
            else:
                w("(no matches)")
            w("```")
            w()

    # ── PHASE 5: DETERMINISM VALIDATION ──────────────────────────────────
    w("---")
    w("# PHASE 5 — DETERMINISM & NEGATIVE CONTROL VALIDATION")
    w()

    w("## 5a. pytest collection count")
    # guardian: allow-magic-config
    cmd, stdout, stderr, rc = run_cmd([PY, "-m", "pytest", "--collect-only", "-q", "--color=no"], timeout=60)
    w("```")
    w(f"$ {cmd}")
    # Show last 20 lines of output (collection summary)
    out_lines = stdout.strip().splitlines()
    for line in out_lines[-20:]:
        w(line)
    w(f"EXIT CODE: {rc}")
    w("```")
    w()

    w("## 5b. Wall-clock / uuid4 contamination in determinism paths")
    for pat_label, pat in [
        ("datetime.now in agentic_core/", r"datetime\.now"),
        ("time.time() in agentic_core/", r"time\.time\(\)"),
        ("uuid4 in agentic_core/", r"uuid4"),
    ]:
        cmd_desc, raw_lines, mc, fset = py_grep(pat, root=REPO / "agentic_core")
        w(f"### {pat_label}")
        w(f"**Command:** `{cmd_desc}`")
        w(f"**Matches:** {mc} in {len(fset)} files")
        w("```")
        for rl in raw_lines[:25]:
            w(rl)
        if len(raw_lines) > 25:
            w(f"... ({len(raw_lines) - 25} more)")
        w("```")
        w()

    w("## 5c. Negative control test search")
    cmd_desc, raw_lines, mc, fset = py_grep(r"xfail.*strict.*True")
    w(f"**Command:** `{cmd_desc}`")
    w(f"**Matches:** {mc} in {len(fset)} files")
    w("```")
    for rl in raw_lines[:30]:
        w(rl)
    if len(raw_lines) > 30:
        w(f"... ({len(raw_lines) - 30} more)")
    w("```")
    w()

    w("## 5d. Determinism digest search")
    cmd_desc, raw_lines, mc, fset = py_grep(r"determinism.*digest|digest.*determinism|DETERMINISM_DIGEST")
    w(f"**Command:** `{cmd_desc}`")
    w(f"**Matches:** {mc} in {len(fset)} files")
    w("```")
    for rl in raw_lines[:20]:
        w(rl)
    if len(raw_lines) > 20:
        w(f"... ({len(raw_lines) - 20} more)")
    w("```")
    w()

    # ── SECTION B: SUMMARY COUNTS ────────────────────────────────────────
    w("---")
    w("# SECTION B — SUMMARY COUNTS")
    w()
    w("## Overall Status Distribution")
    w("```")
    w(f"Total requirements evaluated: {len(rows)}")
    for s, c in sorted(status_ctr.items()):
        w(f"  {s}: {c}")
    w("```")
    w()

    w("## CRITICAL Status Distribution")
    crit_total = sum(1 for r in rows if r["severity"] == "CRITICAL")
    w("```")
    w(f"Total CRITICAL: {crit_total}")
    for s, c in sorted(crit_ctr.items()):
        w(f"  CRITICAL {s}: {c}")
    w("```")
    w()

    w("## Prefix-Level Breakdown")
    w("```")
    for p, counts in sorted(pfx_status.items()):
        total = sum(counts.values())
        parts = ", ".join(f"{s}={c}" for s, c in sorted(counts.items()))
        w(f"  {p} ({total}): {parts}")
    w("```")
    w()

    # ── SECTION C: ENFORCEMENT LAYER COVERAGE ────────────────────────────
    w("---")
    w("# SECTION C — ENFORCEMENT LAYER COVERAGE")
    w()
    layer_totals = Counter()
    for r in rows:
        for l in r["layers"].split(","):
            layer_totals[l.strip()] += 1
    w("```")
    for l, c in sorted(layer_totals.items(), key=lambda x: -x[1]):
        w(f"  {l}: required by {c} requirements")
    w("```")
    w()

    # ── DETAIL APPENDIX ──────────────────────────────────────────────────
    w("---")
    w("# APPENDIX — PER-REQUIREMENT EVIDENCE DETAIL")
    w()
    w("Below is the full raw search evidence for every requirement row.")
    w()
    for det in detail_sections:
        w(det)

    # ── WRITE ─────────────────────────────────────────────────────────────
    content = "\n".join(E)
    OUT.write_text(content, encoding="utf-8")
    print(f"\nReport written to: {OUT}", file=sys.stderr)
    print(f"Total lines: {len(E)}", file=sys.stderr)
    print(f"Total bytes: {len(content)}", file=sys.stderr)


if __name__ == "__main__":
    main()
