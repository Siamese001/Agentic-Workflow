# Phase 14 Closeout - Windows Shell Evidence

## Wave 14.C1 - Confirm environment + repo root
```bash
cd C:\Git\Agentic-Workflow
pwd
python -V
pre-commit --version
git rev-parse --show-toplevel
git status --porcelain
```

Output:
```
PS C:\Git\Agentic-Workflow> cd C:\Git\Agentic-Workflow && pwd && python -V && pre-commit --version && git rev-parse --show-toplevel && git status --porcelain

Python 3.12.10
pre-commit 4.5.1
C:/Git/Agentic-Workflow
?? .tmp/
?? docs/reports/environment/phase_wsl_git_unification.md
```

## Wave 14.C2 - Prove Phase 14 commit contents match intended scope
```bash
cd C:\Git\Agentic-Workflow
git show --name-only --oneline 45caaa7dbb526ba5c5c58b7d941a9a393c00121a
git show --stat 45caaa7dbb526ba5c5c58b7d941a9a393c00121a
```

Output:
```
fatal: bad object 45caaa7dbb526ba5c5c58b7d941a9a393c00121a
```

Note: Commit hash 45caaa7dbb526ba5c5c58b7d941a9a393c00121a does not exist in Windows repo.

Actual HEAD commit:
```bash
git show --name-only --oneline HEAD
git show --stat HEAD
```

Output:
```
eb9ca34f1 (HEAD -> gravity-healing) env(wsl): normalize execution environment to Ubuntu (Phase 0)
docs/reports/environment/phase0_wsl_normalization.md
commit eb9ca34f12e92a203c4fc6edb9d9e0b2ca8c8c6f (HEAD -> gravity-healing)
Author: Siamese001 <siamese001@users.noreply.github.com>
Date:   Tue Feb 17 12:08:51 2026 -0500

    env(wsl): normalize execution environment to Ubuntu (Phase 0)

 .../environment/phase0_wsl_normalization.md        | 95 ++++++++++------------
 1 file changed, 44 insertions(+), 51 deletions(-)
```

## Wave 14.C3 - Re-run gates on clean tree
```bash
cd C:\Git\Agentic-Workflow
git status --porcelain
pre-commit run check-anti-patterns -a -v --show-diff-on-failure
pre-commit run -a
pre-commit run -a
git status --porcelain
```

Output:
```
PS C:\Git\Agentic-Workflow> cd C:\Git\Agentic-Workflow && git status --porcelain && pre-commit run check-anti-patterns -a -v --show-diff-on-failure
?? .tmp/
?? docs/reports/environment/phase_wsl_git_unification.md
T3a: Anti-Pattern Landmine Detection.....................................Failed
- hook id: check-anti-patterns
- duration: 9.06s
- exit code: 1

[BLOCK] Found 8 NEW anti-pattern landmine(s) (out of 1413 total):
  • global_mutation: 1
  • magic_configuration: 5
  • silent_swallower: 2

[FAIL] validate_import_deps.py:56
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] validate_import_deps.py:94
   [silent_swallower] Silent exception swallower: catches Exception without raise or proper return
   Evidence: except Exception as e:...
   [FIX] Add proper error handling:

[FAIL] subprocess_runner.py:61
   [magic_configuration] Magic configuration: Hardcoded timeout=300 in function call
   Evidence: result = subprocess.run(...
   [FIX] Externalize timeout to configuration:

[FAIL] subprocess_runner.py:116
   [magic_configuration] Magic configuration: Hardcoded timeout=600 in function call
   Evidence: result = subprocess.run(...
   [FIX] Externalize timeout to configuration:

[FAIL] subprocess_runner.py:152
   [magic_configuration] Magic configuration: Hardcoded timeout=120 in function call
   Evidence: result = subprocess.run(...
   [FIX] Externalize timeout to configuration:

[FAIL] subprocess_runner.py:198
   [magic_configuration] Magic configuration: Hardcoded timeout=300 in function call
   Evidence: result = subprocess.run(...
   [FIX] Externalize timeout to configuration:

[FAIL] subprocess_runner.py:249
   [magic_configuration] Magic configuration: Hardcoded timeout=300 in function call
   Evidence: result = subprocess.run(...
   [FIX] Externalize timeout to configuration:

[FAIL] SubAtomicRegistryAgent.py:229
   [global_mutation] Global mutation: sys.path.insert() modifies global state at runtime
   Evidence: sys.path.insert(0, str(project_root))...
   [FIX] Remove runtime sys.path manipulation:

[ACTION] Fix NEW violations or add '# guardian: allow-<pattern>' to whitelist.
         To update baseline with current violations: python ops_scripts/ci/check_anti_patterns.py --write-baseline

PS C:\Git\Agentic-Workflow> pre-commit run -a && git status --porcelain && pre-commit run -a && git status --porcelain
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Failed
- hook id: end-of-file-fixer
- exit code: 1
- files were dealt

files were modified by by this hook

Fixing docs/reports/guardian/phase13_codevalidator_elimination.md
```

## File Modifications Detected
```bash
git status --porcelain
git diff --name-only
```

Output:
```
PS C:\Git\Agentic-Workflow> cd C:\Git\Agentic-Workflow && git status --porcelain && git diff --name-only
 M docs/reports/guardian/phase13_codevalidator_elimination.md
?? .tmp/
?? docs/reports/environment/phase_wsl_git_unification.md
docs/reports/guardian/phase13_codevalidator_elimination.md
```

## Summary
- Windows repo is on commit eb9ca34f1 (different from Phase 14 commit)
- Phase 14 commit 45caaa7dbb526ba5c5c58b7d941a9a393c00121a does not exist in Windows repo
- Windows repo still has the original Phase 14 violations (magic_configuration in subprocess_runner.py, global_mutation in SubAtomicRegistryAgent.py)
- Pre-commit hook modified docs/reports/guardian/phase13_codevalidator_elimination.md
- Phase 14 fixes are only present in WSL repo, not Windows repo
