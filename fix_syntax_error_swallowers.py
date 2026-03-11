"""
Replace file-scanner SyntaxError swallowers with AssertionError.

Pattern to replace:
    try:
        tree = ast.parse(...)
    except SyntaxError:  # guardian: allow-silent-swallower
        continue

With:
    try:
        tree = ast.parse(...)
    except SyntaxError as exc:
        raise AssertionError(f"SyntaxError in {<varname>}: {exc}") from exc
"""
import pathlib
import re

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = pathlib.Path(".")

FILES = [
    "tests/governance/test_req111_no_uuid4_determinism.py",
    "tests/governance/test_req114_no_wallclock_determinism.py",
    "tests/governance/test_req118_no_reflection_bypass.py",
    "tests/governance/test_req129_no_mutable_globals.py",
    "tests/governance/test_layer_sovereignty_guard.py",
    "tests/governance/test_oscillation_detector_wiring_invariant.py",
    "tests/governance/test_req414_network_egress_guard.py",
]

# Pattern: except SyntaxError:  # guardian: ... \n                continue
# The surrounding context varies (indentation) but pattern is consistent
PATTERN = re.compile(
    r"        except SyntaxError:  # guardian: allow-silent-swallower\n            continue\n",
)
REPLACEMENT = (
    "        except SyntaxError as exc:\n"
    "            raise AssertionError(f\"SyntaxError in scanned file: {exc}\") from exc\n"
)

# Pattern2: different indentation
PATTERN2 = re.compile(
    r"            except SyntaxError:  # guardian: allow-silent-swallower\n                continue\n",
)
REPLACEMENT2 = (
    "            except SyntaxError as exc:\n"
    "                raise AssertionError(f\"SyntaxError in scanned file: {exc}\") from exc\n"
)

# Pattern3: (SyntaxError, UnicodeDecodeError)
PATTERN3 = re.compile(
    r"            except \(SyntaxError, UnicodeDecodeError\) as e:  # guardian: allow-silent-swallower\n"
    r"                print\([^)]+\)\n",
)
REPLACEMENT3 = (
    "            except (SyntaxError, UnicodeDecodeError) as exc:\n"
    "                raise AssertionError(f\"Parse error in scanned file: {exc}\") from exc\n"
)

# Pattern4: bare except:  # guardian (for network egress guard)
PATTERN4 = re.compile(
    r"        except:  # guardian: allow-silent-swallower\n            pass\n",
)
REPLACEMENT4 = ""  # will handle manually


def fix_file(path: pathlib.Path) -> int:
    content = path.read_text(encoding="utf-8")
    original = content

    content = PATTERN.sub(REPLACEMENT, content)
    content = PATTERN2.sub(REPLACEMENT2, content)
    content = PATTERN3.sub(REPLACEMENT3, content)

    if content != original:
        path.write_text(content, encoding="utf-8")
        return content.count("raise AssertionError") - original.count("raise AssertionError")
    return 0


for fp in FILES:
    p = ROOT / fp
    if not p.exists():
        print(f"NOT FOUND: {fp}")
        continue
    n = fix_file(p)
    if n:
        print(f"Fixed {n} in: {fp}")
    else:
        # Check what's left
        content = p.read_text(encoding="utf-8")
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if "guardian: allow-silent-swallower" in line:
                context = lines[max(0, i-3):min(len(lines), i+2)]
                print(f"UNMATCHED in {fp}:{i}:")
                for c in context:
                    print(f"  {c!r}")
