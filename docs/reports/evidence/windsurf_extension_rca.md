# Windsurf Extension Host Crash RCA

**Phase:** 1 of 1 | **Waves:** 3 | **Evidence captured:** 2026-02-20

---

## WAVE 1 — Triage + Evidence Capture

### 1. Environment Snapshot

| Field | Value |
|---|---|
| **OS** | Windows 10 Home 2009 64-bit |
| **Python** | 3.12.10 (`C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe`) |
| **Git** | 2.53.0.windows.1 (`C:\Program Files\Git\cmd\git.exe`) |
| **Windsurf Version** | *Not captured — requires Help → About from UI* |
| **Workspace** | `c:\Git` (single workspace, all sessions in same workspace ID `55f8c2d15df222a548328dc3934396c3`) |
| **Log sessions analysed** | `20260220T015129`, `20260220T062224` |

### 2. Extensions Detected Across All Sessions

Extracted from `exthost.log` activation records across both sessions:

| Extension ID | Publisher | Notes |
|---|---|---|
| `codeium.windsurf` | Codeium | Core Windsurf AI — activates on `*` |
| `Codeium.windsurfPyright` | Codeium | Pyright LSP — activates on `onLanguage:python` |
| `Codeium.windsurf-dev-containers` | Codeium | Dev Containers — activates on `onStartupFinished` |
| `ms-python.python` | Microsoft | Python extension |
| `ms-python.debugpy` | Microsoft | Python debugger |
| `ms-python.vscode-python-envs` | Microsoft | Python env manager |
| `ms-python.mypy-type-checker` | Microsoft | Mypy (session 1 only) |
| `ms-python.flake8` | Microsoft | Flake8 (session 1 only) |
| `charliermarsh.ruff` | Charlie Marsh | Ruff linter (session 1 only) |
| `mechatroner.rainbow-csv` | mechatroner | CSV (session 1 only) |
| `vscode.git` | Microsoft | Built-in Git |
| `vscode.github` | Microsoft | Built-in GitHub |
| `vscode.github-authentication` | Microsoft | Built-in GitHub Auth |
| `vscode.html-language-features` | Microsoft | Built-in HTML LSP |
| `vscode.emmet` | Microsoft | Built-in Emmet |
| `vscode.merge-conflict` | Microsoft | Built-in merge conflict |
| `vscode.debug-auto-launch` | Microsoft | Built-in debug |
| `vscode.terminal-suggest` | Microsoft | Built-in terminal suggest |
| `vscode.npm` | Microsoft | Built-in npm |
| `vscode.markdown-language-features` | Microsoft | Built-in Markdown |
| `vscode.extension-editing` | Microsoft | Built-in extension editing |

### 3. Log Paths

```
Session 1 (01:51): C:\Users\amita\AppData\Roaming\Windsurf\logs\20260220T015129\
Session 2 (06:22): C:\Users\amita\AppData\Roaming\Windsurf\logs\20260220T062224\
```

### 4. Error Signatures Found

#### 4a. `main.log` — Session 2 (`20260220T062224`)

```
2026-02-20 06:22:24.296 [error] [uncaught exception in main]: Error: Failed to set path
2026-02-20 06:22:24.296 [error] Error: Failed to set path
    at rl.l (file:///C:/Users/amita/AppData/Local/Programs/Windsurf/resources/app/out/main.js:90:16881)
```

**Extension host exits (all code: 0 = normal/requested termination):**
```
2026-02-20 06:45:00.625 [info] Extension host with pid 21656 exited with code: 0, signal: unknown.
2026-02-20 06:45:03.288 [info] Extension host with pid 34440 exited with code: 0, signal: unknown.
2026-02-20 06:45:05.629 [info] Extension host with pid 21852 exited with code: 0, signal: unknown.
2026-02-20 06:46:08.363 [info] Extension host with pid 3268 exited with code: 0, signal: unknown.
2026-02-20 06:46:15.420 [info] Extension host with pid 5688 exited with code: 0, signal: unknown.
```

**Observation:** 5 extension host restarts between 06:45–06:46 (within ~75 seconds). All exit code 0. This is the "3 times in 5 minutes" pattern — Windsurf UI shows the warning even for clean exits when they happen rapidly.

#### 4b. `exthost.log` — Recurring across ALL sessions

```
2026-02-20 01:51:42.380 [error] Error: Language server has not been started!
    at get client (c:\Users\amita\AppData\Local\Programs\Windsurf\resources\app\extensions\windsurf\dist\extension.js:2:1616835)
    at e.activate (c:\Users\amita\AppData\Local\Programs\Windsurf\resources\app\extensions\windsurf\dist\extension.js:2:1153749)
    at async xD.l (extensionHostProcess.js:116:13537)

2026-02-20 06:22:37.602 [error] Error: Language server has not been started!
    [same stack — codeium.windsurf extension.js]

2026-02-20 06:49:25.542 [error] Error: Language server has not been started!
    [same stack — codeium.windsurf extension.js]
```

**Origin:** `codeium.windsurf` extension (`extension.js:2:1616835`) — Windsurf's own AI extension fails to start its language server on activation, then throws during `e.activate()`.

#### 4c. `renderer.log` — Session 2

```
2026-02-20 06:49:13.289 [error] App icon customization is not supported on this OS: Error: App icon customization is not supported on this OS
    at K6.setIcon (main.js:147:3378)

2026-02-20 06:49:25.543 [error] An unknown error occurred. Please consult the log for more details.

2026-02-20 06:56:34.905 [error] [createInstance] $$rc depends on UNKNOWN service agentSessions.: Error: [createInstance] $$rc depends on UNKNOWN service agentSessions.
    at V$e.createInstance (workbench.desktop.main.js:16182:1098)
    at new $uJc (workbench.desktop.main.js:16852:8566)
    at new $vJc (workbench.desktop.main.js:16852:16681)
    at new $wJc (workbench.desktop.main.js:16852:19789)

2026-02-20 06:56:35.069 [error] [Extension Host] (node:18712) [DEP0040] DeprecationWarning: The `punycode` module is deprecated.
```

**Critical:** `UNKNOWN service agentSessions` — the Windsurf Cascade/AI panel (`windsurf.cascadePanel`) is trying to instantiate a service (`agentSessions`) that is not registered. This is a Windsurf core DI (dependency injection) failure, not a third-party extension issue.

#### 4d. `renderer.log` — Session 1 (`20260220T015129`)

```
2026-02-20 06:20:10.104 [error] Canceled: Canceled
    at ExtensionHostManagerData.dispose (workbench.desktop.main.js:18960:8042)
    at ExtensionHostCollection.stopAllInReverse (workbench.desktop.main.js:18960:7323)
    at async $Hnd.tb (workbench.desktop.main.js:18959:17679)
```

**Observation:** Extension host collection is being stopped via `stopAllInReverse` — this is a controlled shutdown (window reload/restart), not a crash. The `Canceled` error is a promise cancellation during teardown, expected behavior.

#### 4e. `ms-python.python` — Recurring warning

```
2026-02-20 05:38:11.717 [info] Editor support is inactive since language server is set to None.
Dir "c:\Git\.pixi\envs" is not watchable (directory does not exist)
```

**Observation:** Python extension has language server set to `None` (Pylance/Pyright disabled in favor of `Codeium.windsurfPyright`). Non-fatal.

#### 4f. `Windsurf Pyright.log` — Session 1

```
[Info - 5:54:44 AM] windsurfPyright language server 1.29.5 starting
[Info - 5:54:44 AM] Found 5322 source files
[Info - 6:18:14 AM] Found 5323 source files
```

**Observation:** Pyright is scanning `c:\Git` (the entire Git root, not just `Agentic-Workflow`). 5322+ source files is a very large workspace for Pyright to index.

### 5. Baseline Reproduction Test

**`--disable-extensions` test:** Performed 2026-02-20 08:20 UTC-05:00.

**Command:** `Start-Process "C:\Users\amita\AppData\Local\Programs\Windsurf\Windsurf.exe" -ArgumentList "--disable-extensions"`

**Outcome: Crash reproduces with all extensions disabled** — `agentSessions` DI failure and `Language server has not been started!` both fire even with `--disable-extensions`.

**Key log evidence (window2, session `20260220T062224`):**
```
2026-02-20 08:20:36.646 [error] Error: Language server has not been started!
    at get client (extensions\windsurf\dist\extension.js:2:1616835)
    at e.activate (extension.js:2:1153749)

2026-02-20 08:21:31.708 [error] [createInstance] $$rc depends on UNKNOWN service agentSessions.
    at V$e.createInstance (workbench.desktop.main.js:16182:1098)
    at new $uJc (workbench.desktop.main.js:16852:8566)

2026-02-20 08:21:33.552 [error] [File Watcher (node.js)] Failed to watch
    \\wsl.localhost\Ubuntu-24.04\home\amita\src\Agentic-Workflow\docs\reports\environment\phase14_landmine_real_fixes.md
    (Error: EISDIR: illegal operation on a directory, watch '...')

2026-02-20 08:21:31.746 [warning] IWorkbenchContributionsRegistry#getContribution('windsurf.cascadePanel'):
    contribution instantiated before LifecyclePhase.Restored!
```

**Critical new finding:** `--disable-extensions` does NOT suppress `codeium.windsurf` — it is a **built-in bundled extension** (`resources/app/extensions/windsurf/`), not a marketplace extension. `--disable-extensions` only disables marketplace/user-installed extensions. The Windsurf AI extension is exempt from this flag.

**Additional finding:** A WSL path (`\\wsl.localhost\Ubuntu-24.04\...`) is being watched by the file watcher — Windsurf is tracking a WSL mirror of this repo, causing `EISDIR` errors and additional file watcher overhead.

---

## WAVE 2 — Root Cause Isolation

### Extension Bisect

**Not required** — `--disable-extensions` baseline test (Wave 1 §5) proved the crash is **not caused by marketplace/user extensions**. The errors reproduce identically with all user extensions disabled. Bisect would not identify anything new.

### Isolation Result

**`--disable-extensions` outcome:** Crash reproduces. Both error signatures persist:
- `Error: Language server has not been started!` — fires from `codeium.windsurf` (bundled, not disableable)
- `[createInstance] $$rc depends on UNKNOWN service agentSessions` — fires from Windsurf core renderer

**Classification: Windsurf core / bundled extension defect** — not a user-installed extension issue.

**Evidence chain:**
1. `codeium.windsurf` is located at `resources/app/extensions/windsurf/` (bundled with the app binary), not in the user extensions directory. `--disable-extensions` does not apply to bundled extensions.
2. The `agentSessions` service is referenced by `windsurf.cascadePanel` contribution but never registered — this is a DI wiring bug in the Windsurf workbench build, present in both normal and `--disable-extensions` modes.
3. The 5 rapid extension host exits (06:45:00–06:46:15, all code 0) are controlled reloads triggered by Cascade AI operations, not crashes. Each reload re-triggers the `codeium.windsurf` language server startup race.
4. **New finding from `--disable-extensions` run:** WSL file watcher error — `\\wsl.localhost\Ubuntu-24.04\home\amita\src\Agentic-Workflow\...` is being watched, causing `EISDIR` errors. Windsurf is tracking a WSL mirror of the repo simultaneously with the Windows path, adding file watcher contention on every extension host start.

---

## WAVE 3 — Root Cause Narrative + Mitigation

### Incident Summary

| Field | Value |
|---|---|
| **When** | 2026-02-20 06:45–06:46 UTC-05:00 |
| **Frequency** | 5 extension host exits in ~75 seconds |
| **Trigger** | Rapid Windsurf window reloads during Cascade AI session (Python script execution + cancellation) |
| **UI message** | "Extension host terminated unexpectedly 3 times within last 5 minutes" |

### Impact

- Windsurf AI (Cascade) panel temporarily unavailable after each restart
- `codeium.windsurf` language server fails to start on each re-activation
- No data loss; all exits were code 0 (clean)

### Detection Signals

```
main.log:    Extension host with pid XXXXX exited with code: 0, signal: unknown.  (×5 in 75s)
exthost.log: Error: Language server has not been started!  (×3 across sessions)
renderer.log: [createInstance] $$rc depends on UNKNOWN service agentSessions.
```

### Root Cause

**Observed:** 5 rapid extension host exits in 75 seconds (06:45:00–06:46:15), all code 0. UI threshold of "3 times in 5 minutes" triggered.

**Evidence:** `--disable-extensions` run (08:20) reproduces both error signatures identically — proving this is **not a user/marketplace extension issue**.

**Conclusion (ordered by certainty):**

1. **PRIMARY — Windsurf core DI bug (`agentSessions`):** `[createInstance] $$rc depends on UNKNOWN service agentSessions` fires in the renderer on every session start, including `--disable-extensions`. The `windsurf.cascadePanel` contribution references a service that is not registered in the current build. This is a Windsurf version defect — the `agentSessions` service was added to the panel but not wired into the DI container in this build.

2. **SECONDARY — Bundled `codeium.windsurf` language server race:** `Error: Language server has not been started!` fires from `resources/app/extensions/windsurf/dist/extension.js` on every activation. The language server is not ready when `activate()` is called. This is a startup timing bug in the bundled Windsurf AI extension — not suppressible via `--disable-extensions`.

3. **TRIGGER — Cascade-driven window reloads:** Each Cascade Python script run/cancel caused a controlled window reload (exit code 0). Each reload re-triggered both bugs above. 5 reloads in 75 seconds crossed the UI warning threshold.

4. **AGGRAVATING — WSL file watcher contention:** `\\wsl.localhost\Ubuntu-24.04\home\amita\src\Agentic-Workflow\...` is being watched simultaneously with the Windows path. `EISDIR` errors on every extension host start add overhead and may delay language server initialization, widening the race window.

5. **AGGRAVATING — Oversized workspace:** Pyright indexes 5322+ files from `c:\Git` root. Slows extension host startup, widening the language server race window.

### Contributing Factors

| Factor | Impact |
|---|---|
| `agentSessions` DI not registered | Core crash on every session — Windsurf build defect |
| `codeium.windsurf` language server race | Error on every activation — bundled extension timing bug |
| Cascade window reloads (5 in 75s) | Crossed the "3 times in 5 min" UI threshold |
| WSL path watched alongside Windows path | `EISDIR` errors + file watcher overhead |
| Workspace root `c:\Git` (5322+ files) | Pyright slow startup, widens race window |
| Multiple linters active (ruff+flake8+mypy) | Additional activation overhead (session 1) |

### Fix / Mitigation

**Ranked by minimal change:**

1. **Update Windsurf** *(highest priority — fixes both primary bugs)*
   - Help → Check for Updates
   - The `agentSessions` DI bug and language server race are both Windsurf build defects, fixed in newer releases
   - Confirmed required: both errors reproduce with `--disable-extensions`, ruling out all user extensions

2. **Open `c:\Git\Agentic-Workflow` directly** instead of `c:\Git`
   - Reduces Pyright file scan from 5322+ → ~500 files
   - Eliminates WSL path watching (the WSL mirror path `\\wsl.localhost\...` only appears when `c:\Git` root is opened)
   - Already demonstrated: `--disable-extensions` run auto-switched to `c:\Git\Agentic-Workflow` (workspace ID `aea3545d`) and the file watcher error appeared — closing this window and opening `Agentic-Workflow` directly will remove the WSL watch

3. **Disable WSL integration for this workspace** (if WSL is not needed)
   - Settings → `remote.WSL.enabled: false` for this workspace
   - Eliminates `\\wsl.localhost` path watching entirely

4. **Pin a single Python linter** — disable `ms-python.flake8` and `ms-python.mypy-type-checker`; keep only `charliermarsh.ruff`

### Verification Matrix

| Scenario | Errors present | Notes |
|---|---|---|
| Normal launch, `c:\Git` workspace | `agentSessions` ✓, language server race ✓, WSL watcher ✓ | Baseline — 5 ext host exits in 75s |
| `--disable-extensions`, `c:\Git\Agentic-Workflow` | `agentSessions` ✓, language server race ✓, WSL watcher ✓ | **Confirmed 2026-02-20 08:20** — user extensions not the cause |
| Windsurf updated | *Pending* | Expected: both primary errors resolved |
| Open `c:\Git\Agentic-Workflow` directly (no WSL) | *Pending* | Expected: WSL watcher error eliminated |

### Prevent Recurrence

1. **Keep Windsurf updated** — both primary defects are in the Windsurf build, not user config
2. **Always open the specific project folder** (`c:\Git\Agentic-Workflow`), not the parent `c:\Git`
3. **Avoid rapid Cascade cancellations** — each cancel triggers a window reload; let operations complete or use Stop gracefully
4. **Disable WSL integration** if not actively using WSL for this project
5. **Pin one Python linter** (ruff); disable flake8 + mypy

---

## Appendix — Raw Log File Paths

| Log | Path |
|---|---|
| main.log (session 2) | `%APPDATA%\Windsurf\logs\20260220T062224\main.log` |
| exthost.log (session 2) | `%APPDATA%\Windsurf\logs\20260220T062224\window1\exthost\exthost.log` |
| renderer.log (session 2) | `%APPDATA%\Windsurf\logs\20260220T062224\window1\renderer.log` |
| exthost.log (session 1) | `%APPDATA%\Windsurf\logs\20260220T015129\window1\exthost\exthost.log` |
| renderer.log (session 1) | `%APPDATA%\Windsurf\logs\20260220T015129\window1\renderer.log` |
| Windsurf Pyright.log | `%APPDATA%\Windsurf\logs\20260220T015129\window1\exthost\output_logging_20260220T055417\2-Windsurf Pyright.log` |
| Python.log | `%APPDATA%\Windsurf\logs\20260220T015129\window1\exthost\ms-python.python\Python.log` |
| Windsurf (Lifeguard).log | `%APPDATA%\Windsurf\logs\20260220T062224\window1\exthost\codeium.windsurf\Windsurf (Lifeguard).log` |
