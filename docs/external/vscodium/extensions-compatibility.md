# VSCodium — Extensions Compatibility Source Notes

**Source of truth:** https://raw.githubusercontent.com/VSCodium/vscodium/master/docs/extensions-compatibility.md  
**Retrieval date:** 2026-04-11  
**Status:** Full coverage of all sections.

---

## Incompatibility Root Cause

- Most Microsoft extensions are **license-restricted** to run only on Microsoft products.
- Additional proprietary code in those extensions performs product ID checks at runtime.
- Both mechanisms (license + runtime check) independently block usage in VSCodium.

## Confirmed Incompatible Extensions

All sourced from Visual Studio Marketplace (`marketplace.visualstudio.com`):

- `ms-vscode.cpptools` — C/C++
- `James-Yu.latex-workshop` — LaTeX Workshop (explicitly unsupported; stated in extension FAQ)
- `MS-vsliveshare.vsliveshare` — Live Share
- `ms-python.python` — Python
- `ms-vscode-remote.remote-containers` — Remote - Containers
- `ms-vscode-remote.remote-ssh` — Remote - SSH
- `ms-vscode-remote.remote-ssh-edit` — Remote - SSH: Editing Configuration Files
- `ms-vscode-remote.remote-wsl` — Remote - WSL

## Open VSX Replacement Extensions

### C/C++
- [`llvm-vs-code-extensions.vscode-clangd`](https://open-vsx.org/extension/llvm-vs-code-extensions/vscode-clangd) — full-featured editing including IntelliSense
- [`webfreak.debug`](https://open-vsx.org/extension/webfreak/debug) — Native Debug, GDB + LLDB debugging; note: many other working debug extensions exist including microcontroller-specialized ones

### Python
- [`detachhead.basedpyright`](https://open-vsx.org/extension/detachhead/basedpyright) — BasedPyright

### Remote Development
- [`jeanp413.open-remote-ssh`](https://open-vsx.org/extension/jeanp413/open-remote-ssh) — Open Remote - SSH (requires `AllowTcpForwarding yes` on SSH server)
- [`jeanp413.open-remote-wsl`](https://open-vsx.org/extension/jeanp413/open-remote-wsl) — Open Remote - WSL

## Extension Compatibility Risks

- An extension on Open VSX is not guaranteed to be compatible; Microsoft license restrictions and runtime product checks are extension-specific.
- The replacement list above is explicitly confirmed by the VSCodium project; it is not exhaustive.
- LaTeX Workshop is notable in that its maintainer explicitly states VSCodium is unsupported — it is not merely a Microsoft license issue.

## Supported vs. Unsupported

- **Supported:** Full content of the upstream compatibility doc.
- **Unsupported from local sources:** No section on general non-Microsoft third-party extensions that may have independent compatibility issues. Only Microsoft-ecosystem extensions are explicitly documented.
