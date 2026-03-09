# Forbidden Methods Checklist

**Use this checklist to verify compliance with §3.5.**

## Constitutional Prohibition

Low-signal search is FORBIDDEN as a primary analysis method.

## Forbidden Primary Methods

These methods MUST NOT be used as the primary way to determine:
- Blast radius
- Architecture
- Ownership
- Call flow
- Dependency direction
- Dead code
- Test coverage
- Whether a component is unused
- Whether a file is authoritative

### ❌ Grep / Ripgrep

```
FORBIDDEN USAGE:
❌ grep -r "import file1" .
❌ rg "def function_a"
❌ grep -r "class MyAgent"

WHY FORBIDDEN:
- Cannot distinguish between imports, comments, strings, or actual usage
- Cannot determine direction of dependency
- Cannot detect dynamic resolution (registry, factory)
- Cannot detect inheritance or protocol realization
- Misses call edges hidden in lambdas, decorators, or dynamic dispatch
```

### ❌ Regex-Only Repo Sweeps

```
FORBIDDEN USAGE:
❌ re.findall(r'from (\S+) import', file_content)
❌ re.search(r'class \w+\((\w+)\)', file_content)

WHY FORBIDDEN:
- Regex cannot parse Python AST correctly
- Misses nested structures
- Fails on multi-line statements
- Cannot resolve imports to actual modules
- Cannot handle dynamic imports
```

### ❌ Filename-Only Guesses

```
FORBIDDEN USAGE:
❌ "file1.py probably depends on file2.py because they're in the same directory"
❌ "test_file1.py probably tests file1.py because of naming convention"
❌ "This file is probably unused because I don't see it imported anywhere"

WHY FORBIDDEN:
- Filename similarity does not prove dependency
- Files can have dependencies across directories
- Test files may use indirect imports via fixtures
- Files may be used via dynamic imports, registry, or CLI entrypoints
```

### ❌ Substring Hunts

```
FORBIDDEN USAGE:
❌ "Search for 'MyClass' to find all usages"
❌ "Search for 'function_a' to find all callers"

WHY FORBIDDEN:
- String search finds comments, docstrings, and unrelated code
- Cannot distinguish between definition and usage
- Cannot determine call direction
- Misses aliased imports (import X as Y)
```

### ❌ IDE Search Result Counts

```
FORBIDDEN USAGE:
❌ "IDE shows 5 references to this function, so blast radius is 5 files"
❌ "Find all references shows no results, so this is dead code"

WHY FORBIDDEN:
- IDE search may not index all files
- IDE search may miss dynamic resolution
- IDE search may include false positives (comments, strings)
- IDE search may not handle registry/factory patterns
```

### ❌ "Search Until Something Looks Right"

```
FORBIDDEN USAGE:
❌ grep for "import" until you find something that looks related
❌ Search for class names until you find a plausible dependency
❌ Keep searching until you find a test file that might cover this code

WHY FORBIDDEN:
- Non-deterministic
- Confirmation bias (find what you expect, not what exists)
- Misses systematic relationships
- Cannot prove completeness
```

## Permitted Secondary Usage

Text search MAY be used ONLY in these limited cases:

### ✅ After Graph Analysis (Secondary Confirmation)

```
PERMITTED USAGE:
1. Build AST dependency graph
2. Graph shows: file1.py imports common/utils.py
3. Use grep to confirm exact import statement for documentation:
   grep "from common.utils import" file1.py

This is SECONDARY confirmation, not PRIMARY analysis.
```

### ✅ Literal String Constants

```
PERMITTED USAGE:
1. Graph shows: file1.py registers agent with name "my_agent"
2. Use grep to find all registry lookups for "my_agent":
   grep '"my_agent"' .

This is searching for EXACT literal strings, not inferring structure.
```

### ✅ Exact Constants

```
PERMITTED USAGE:
1. Graph shows: file1.py uses config constant THRESHOLD
2. Use grep to find definition of THRESHOLD:
   grep "THRESHOLD = " config/settings.py

This is finding EXACT constant definition, not inferring dependencies.
```

## Verification Checklist

Before using any search method, verify:

- [ ] Have I built the AST dependency graph first?
- [ ] Am I using search as PRIMARY analysis? (If YES → FORBIDDEN)
- [ ] Am I using search as SECONDARY confirmation? (If YES → PERMITTED)
- [ ] Am I searching for exact literal strings/constants? (If YES → PERMITTED)
- [ ] Am I inferring structure from search results? (If YES → FORBIDDEN)
- [ ] Could this search result be wrong? (If YES → MUST verify with graph)

## Graph vs Text Search Decision Tree

```
START: Need to determine dependencies/impact

Q: Have you built AST dependency graph?
├─ NO → STOP. Build graph first (§3.4 MANDATORY)
└─ YES → Continue

Q: What do you need to find?
├─ Dependency relationships → Use GRAPH (text search FORBIDDEN)
├─ Call flow → Use GRAPH (text search FORBIDDEN)
├─ Test coverage → Use GRAPH (text search FORBIDDEN)
├─ Blast radius → Use GRAPH (text search FORBIDDEN)
├─ Exact literal string → Text search PERMITTED (after graph)
└─ Constant definition → Text search PERMITTED (after graph)

Q: Do graph and text search disagree?
├─ YES → GRAPH WINS (unless you prove graph is incomplete)
└─ NO → Proceed with graph-backed conclusion
```

## Example: Correct Usage

```
CORRECT SEQUENCE:
1. Build AST dependency graph for file1.py
2. Graph shows:
   - file1.py imports common/utils.py
   - file1.py is imported by file2.py, apps_lic/engines/control_plane.py
   - file1.py::function_a is called by file2.py::process_data

3. Use grep to confirm exact import statement for documentation:
   $ grep "from common.utils import" file1.py
   from common.utils import helper_function

4. Document in evidence:
   "Per AST dependency graph, file1.py imports common/utils.py.
    Confirmed via grep: 'from common.utils import helper_function'"
```

## Example: Incorrect Usage

```
INCORRECT SEQUENCE (CONSTITUTIONAL VIOLATION):
1. Use grep to find dependencies:
   $ grep -r "import file1" .
   file2.py:from file1 import function_a
   tests/test_file1.py:import file1

2. Conclude: "file1.py is used by file2.py and tests/test_file1.py"

WHY WRONG:
- Did not build AST dependency graph first (§3.4 violation)
- Used grep as PRIMARY analysis method (§3.5 violation)
- Missed dynamic imports, registry lookups, factory resolution
- Cannot determine call direction or edge types
- May have false positives (comments, strings)
```

## Constitutional References

- **§3.4:** AST dependency graphs are PRIMARY and REQUIRED analysis primitive
- **§3.5:** Low-signal search FORBIDDEN as primary analysis method
- **§3.5:** Text search MAY be used only after graph analysis, as secondary confirmation
- **§3.5:** If graph and text search disagree, graph wins
