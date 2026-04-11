# Windsurf VSCodium Extensions Policy

## Status

- **Policy version:** 1.0
- **Effective date:** 2026-04-11
- **Provisional sections:** [GitHub Copilot Policy](#github-copilot-policy-provisional), [Extension Compatibility Triage](#extension-compatibility-triage)
- **Next review trigger:** See [Policy Gaps and Review Triggers](#policy-gaps-and-review-triggers)

---

## Purpose

Define which extension sources, galleries, and individual extensions are approved, blocked, or provisional for use with VSCodium in this repository's development environment. This policy governs Windsurf AI assistant behavior when recommending, installing, or referencing extensions.

---

## Scope

- **Applies to:** All VSCodium installations used in this repo's development environment.
- **Does not apply to:** Official Microsoft VS Code builds. Extension policy for VS Code is governed separately.
- **Does not apply to:** CI/CD pipelines — extension installation in automation is out of scope for this policy version.

---

## In-Scope Source Docs

All policy statements below are derived exclusively from these local source notes:

- `@docs/external/vscodium/index.md` — project identity and doc TOC
- `@docs/external/vscodium/extensions.md` — marketplace strategy, gallery config, proprietary tools
- `@docs/external/vscodium/extensions-compatibility.md` — incompatible extensions and replacements
- `@docs/external/vscodium/ext-github-copilot.md` — Copilot configuration (partial)

---

## Canonical Principles

1. Microsoft Marketplace is **legally blocked** — not a preference, not configurable away.
2. Open VSX is the **default and sole approved gallery** for VSCodium in this repo.
3. An extension absent from Open VSX is not automatically blocked — approved fallback paths exist.
4. Incompatible extensions have **two independent blocking mechanisms**: license restriction and runtime product ID check. Either one alone is sufficient to block an extension; both must be bypassed for it to work.
5. Provisional sections are explicitly marked. Do not treat provisional guidance as final policy.

---

## Approved Extension Sources

### Primary: Open VSX Registry

- **URL:** https://open-vsx.org/
- **Status:** APPROVED — default
- VSCodium's `product.json` points here out of the box; no configuration required.
- All extension installs via the VSCodium Extensions view use this gallery by default.

### Approved Fallback: Manual `.vsix` from upstream source repo releases

- **Status:** APPROVED — fallback only
- Permitted when an extension is not available on Open VSX.
- The `.vsix` must be sourced from the extension's **own upstream release page** (e.g., GitHub Releases for that extension's repo).
- `.vsix` files sourced from, redistributed from, or originally downloaded from Visual Studio Marketplace — by any party — are **not permitted** under this fallback, regardless of how they are delivered.

### Approved Tooling: VSIX Manager Extension

- **Status:** APPROVED — fallback tooling
- GitHub: https://github.com/zokugun/vscode-vsix-manager — authored by the main VSCodium maintainer.
- Permitted use cases: multi-marketplace management, local `.vsix` management, GitHub/Forgejo release installs, offline environments, fallback when a marketplace is temporarily inaccessible.
- Source: `@docs/external/vscodium/extensions.md` §VSIX Manager Extension

### Permitted Enterprise Path: Self-Hosted Gallery

- **Status:** PERMITTED — not currently required
- Two confirmed working options (source: `@docs/external/vscodium/extensions.md` §Self-Hosted Gallery):
  - **Open VSX (self-hosted):** Eclipse open-source project; same API as the public instance. Provides server, web UI, and `ovsx` CLI for publishing.
  - **code-marketplace:** Coder open-source Go binary; reads extensions from file storage; no frontend or upload mechanism.
- Adopt this path if air-gapped, regulated, or compliance requirements arise.

---

## Blocked Sources

### Visual Studio Marketplace — **HARD BLOCK**

- **URL:** https://marketplace.visualstudio.com/
- **Status:** BLOCKED — legal constraint, no policy override
- Microsoft's Terms of Use explicitly restrict marketplace use to "Visual Studio Products and Services." VSCodium is not a Microsoft product.
- Extensions on this marketplace may carry additional licenses that explicitly forbid non-Microsoft use and may include telemetry.
- **This block is not configurable.** No `product.json` override, no environment variable, no VSIX Manager configuration authorises sourcing extensions from this marketplace in this repo.
- Source: `@docs/external/vscodium/extensions.md` §Visual Studio Marketplace

---

## Blocked Extensions

The following extensions are confirmed incompatible with VSCodium by the VSCodium project. Incompatibility arises from a **dual mechanism**: (1) license restricted to Microsoft products; (2) runtime product ID check. Both mechanisms independently block operation.

| Extension ID | Name | Block Reason |
|---|---|---|
| `ms-vscode.cpptools` | C/C++ | MS license + runtime check |
| `ms-python.python` | Python | MS license + runtime check |
| `MS-vsliveshare.vsliveshare` | Live Share | MS license + runtime check |
| `ms-vscode-remote.remote-containers` | Remote - Containers | MS license + runtime check |
| `ms-vscode-remote.remote-ssh` | Remote - SSH | MS license + runtime check |
| `ms-vscode-remote.remote-ssh-edit` | Remote - SSH: Editing Config Files | MS license + runtime check |
| `ms-vscode-remote.remote-wsl` | Remote - WSL | MS license + runtime check |
| `James-Yu.latex-workshop` | LaTeX Workshop | Maintainer-stated incompatibility (not an MS license issue) |

**Note on `extensionAllowedProposedApi`:** Adding a blocked extension's ID to `extensionAllowedProposedApi` in `product.json` is a **partial workaround only**. It does not work if the extension hard-codes a VS Code product ID check. Any proposed addition requires individual review — it is not blanket approved. See [Extension Compatibility Triage](#extension-compatibility-triage).

Source: `@docs/external/vscodium/extensions-compatibility.md`

---

## Approved Replacement Extensions

All replacements listed here are sourced from Open VSX and confirmed by the VSCodium project.

### C/C++

| Replacement | Open VSX ID | Replaces | Notes |
|---|---|---|---|
| clangd | `llvm-vs-code-extensions.vscode-clangd` | `ms-vscode.cpptools` | Full editing + IntelliSense |
| Native Debug | `webfreak.debug` | `ms-vscode.cpptools` (debug only) | GDB + LLDB; other debugger extensions also available |

### Python

| Replacement | Open VSX ID | Replaces | Notes |
|---|---|---|---|
| BasedPyright | `detachhead.basedpyright` | `ms-python.python` | — |

### Remote Development

| Replacement | Open VSX ID | Replaces | Notes |
|---|---|---|---|
| Open Remote - SSH | `jeanp413.open-remote-ssh` | `ms-vscode-remote.remote-ssh` | SSH server requires `AllowTcpForwarding yes` |
| Open Remote - WSL | `jeanp413.open-remote-wsl` | `ms-vscode-remote.remote-wsl` | — |

**No confirmed replacement exists for:** Live Share, Remote - Containers, Remote - SSH: Editing Config Files. These are unsupported from local sources — do not invent alternatives.

Source: `@docs/external/vscodium/extensions-compatibility.md` §Replacements

---

## Proprietary Debugger Policy

### C# Debugger (`OmniSharp/omnisharp-vscode`)

- **Status:** BLOCKED — restrictively licensed to official VS Code builds only.
- **Approved path:** Use Samsung's open-source [`netcoredbg`](https://github.com/Samsung/netcoredbg). Setup instructions: VSCodium issue #82.
- Source: `@docs/external/vscodium/extensions.md` §Proprietary Debugging Tools

### C++ Windows Debugger (`Microsoft/vscode-cpptools`)

- **Status:** BLOCKED — restrictively licensed to official VS Code builds only.
- **Approved path:** Use `webfreak.debug` (Native Debug) from Open VSX for GDB/LLDB-based debugging. See §Approved Replacement Extensions for the full C/C++ replacement table.
- Source: `@docs/external/vscodium/extensions.md` §Proprietary Debugging Tools

---

## Alternate Gallery Configuration

This section documents the supported configuration mechanisms. Switching from Open VSX requires explicit policy approval — it is not a developer-level decision.

### Environment Variables

Set before VSCodium launch. Required variables:

```
VSCODE_GALLERY_SERVICE_URL      (required)
VSCODE_GALLERY_ITEM_URL         (required)
VSCODE_GALLERY_EXTENSION_URL_TEMPLATE  (required)
VSCODE_GALLERY_CACHE_URL        (optional)
VSCODE_GALLERY_CONTROL_URL      (optional)
VSCODE_GALLERY_RESOURCE_URL_TEMPLATE   (optional)
```

### Custom `product.json`

Location by platform (replace `VSCodium` with `VSCodium - Insiders` for Insiders builds):

- **Windows:** `%APPDATA%\VSCodium` or `%USERPROFILE%\AppData\Roaming\VSCodium`
- **macOS:** `~/Library/Application Support/VSCodium`
- **Linux:** `$XDG_CONFIG_HOME/VSCodium` or `~/.config/VSCodium`

Required shape for gallery override:

```jsonc
{
  "extensionsGallery": {
    "serviceUrl": "",        // required
    "itemUrl": "",           // required
    "cacheUrl": "",
    "controlUrl": "",
    "extensionUrlTemplate": "",   // required
    "resourceUrlTemplate": ""
  }
}
```

**Policy constraint:** Pointing either mechanism at `marketplace.visualstudio.com` remains blocked regardless of method used.

Source: `@docs/external/vscodium/extensions.md` §Alternate Marketplace Configuration

---

## GitHub Copilot Policy (PROVISIONAL)

> ⚠️ **PROVISIONAL — Do not treat as final policy.** Configuration mechanism is documented. Exact `product.json` property values, authentication flow, and licensing implications in non-Microsoft builds are **unsupported from local sources**. This section will be finalised after fetching the Copilot CONTRIBUTING guide and reviewing licensing.

### What is known (source-backed)

- Copilot features are **disabled and not configured by default** in VSCodium — unlike official VS Code.
- Enabling Copilot requires explicit per-user steps; it is not a simple extension install.

### Minimum required steps (source-backed)

1. Add to user settings: `"chat.disableAIFeatures": false`
2. Create a custom `product.json` at the platform-specific user config location (paths listed in [Alternate Gallery Configuration](#alternate-gallery-configuration) above, same locations).
3. Follow the [Running with Code OSS](https://github.com/microsoft/vscode-copilot-chat/blob/main/CONTRIBUTING.md#running-with-code-oss) guide to populate `product.json`.
4. Required `product.json` properties: `trustedExtensionAuthAccess` and `defaultChatAgent`. **Exact values: see Copilot CONTRIBUTING guide — not specified in VSCodium docs.**

### Interim stance

- Do not enforce Copilot usage and do not block it.
- Treat as an individual developer choice pending policy finalisation.
- Do not include Copilot setup in onboarding scripts or shared configuration until this section is finalised.

### What remains unresolved (PROVISIONAL blockers)

- Exact values for `trustedExtensionAuthAccess` and `defaultChatAgent`.
- Whether a Copilot subscription/license is valid when used from a non-Microsoft editor build.
- GitHub OAuth token authentication flow in VSCodium.
- Whether the Insiders build path works beyond the directory name substitution.

**Unblock condition:** Fetch and review `github.com/microsoft/vscode-copilot-chat/blob/main/CONTRIBUTING.md`; review GitHub/Microsoft licensing terms for Copilot outside VS Code.

Source: `@docs/external/vscodium/ext-github-copilot.md`

---

## Extension Compatibility Triage

> ⚠️ **PROVISIONAL for non-Microsoft third-party extensions.** The VSCodium project documents only Microsoft-ecosystem incompatibilities. Non-Microsoft third-party extension compatibility is not catalogued upstream.

### Triage protocol for unlisted extensions

1. Check Open VSX for availability — if present, attempt install and test.
2. If the extension fails, determine whether it is a Microsoft license/runtime check issue or an independent maintainer decision (e.g., LaTeX Workshop).
3. If `extensionAllowedProposedApi` is proposed as a workaround, submit for individual review — note that hard-coded product ID checks will cause silent failure regardless.
4. If no Open VSX alternative exists: use approved fallback paths (manual `.vsix` from source repo, VSIX Manager).
5. Document findings and raise a review trigger to update this policy.

### `extensionAllowedProposedApi` review gate

Any proposed addition to `extensionAllowedProposedApi` in a shared or committed `product.json` must:
- Identify the specific extension ID and the reason the workaround is expected to succeed.
- Confirm the extension does not hard-code a VS Code product ID check.
- Be approved before inclusion in any shared configuration file.

Source: `@docs/external/vscodium/extensions.md` §Proprietary Extensions; `@docs/external/vscodium/extensions-compatibility.md`

---

## Approved Fallback Paths

When an extension is not available on Open VSX, apply these paths in order:

1. **Request publication to Open VSX** — Ask the extension maintainer to publish to `open-vsx.org`, or open a PR to [`open-vsx/publish-extensions`](https://github.com/open-vsx/publish-extensions) for the `@open-vsx` service account to publish on the extension's behalf.
2. **Manual `.vsix` install** — Download the `.vsix` from the extension's own upstream release page (e.g., the extension's GitHub Releases). Do not source `.vsix` from Visual Studio Marketplace.
3. **VSIX Manager** — Use the VSIX Manager extension for local file management, multi-source installs, or offline scenarios.
4. **Self-hosted gallery** — For enterprise or air-gapped scenarios: deploy a self-hosted Open VSX instance or `code-marketplace`.

Source: `@docs/external/vscodium/extensions.md` §Fallback Paths

---

## Marketplace Decision Matrix

| Scenario | Preferred Action | Fallback | Risk / Flag |
|---|---|---|---|
| Install a common extension | Search and install from Open VSX | Download `.vsix` from extension's upstream release page | None if on Open VSX |
| Extension absent from Open VSX | Open PR to `open-vsx/publish-extensions` | Manual `.vsix` from source repo | Confirm `.vsix` not from VS Marketplace |
| `ms-python.python` or any blocked MS extension requested | Block; redirect to approved replacement | None via VS Marketplace | Confirmed incompatible — dual mechanism |
| Remote SSH workflow needed | Install `jeanp413.open-remote-ssh` from Open VSX | None documented in local sources | Requires `AllowTcpForwarding yes` on SSH server |
| C# debugging needed | Use `netcoredbg` (Samsung OSS) | None from local sources | Setup per VSCodium issue #82 |
| LaTeX Workshop requested | Block; flag maintainer-stated incompatibility | None confirmed in local sources | Independent maintainer decision, not MS license |
| GitHub Copilot requested | Individual dev choice (PROVISIONAL) | No alternative documented in local sources | `product.json` values + auth/licensing unresolved |
| `extensionAllowedProposedApi` addition proposed | Submit for individual review | Skip extension if hard-coded product ID check present | May silently fail — cannot predict without testing |
| Air-gapped / regulated environment | Self-hosted Open VSX or `code-marketplace` | VSIX Manager + local `.vsix` files | Infrastructure setup required |
| `.vsix` sourced from VS Marketplace | **Block** | Use Open VSX or source repo release instead | ToU violation — legal exposure |

---

## Prompting Conventions for Windsurf

When prompting Windsurf for extension-related tasks in this repo, use these conventions to keep recommendations within policy bounds.

**Finding an extension:**
> Search `@docs/external/vscodium/extensions-compatibility.md` for a compatible replacement before suggesting any extension. If the requested extension is on the blocklist, state it is blocked and suggest the approved replacement.

**Checking marketplace source:**
> Before recommending an extension install, confirm the source is Open VSX (`open-vsx.org`). If the extension is only available on Visual Studio Marketplace, apply the fallback path in `@docs/standards/windsurf/windsurf_vscodium_extensions_policy.md` §Approved Fallback Paths.

**Copilot setup:**
> Copilot guidance is PROVISIONAL. Reference `@docs/standards/windsurf/windsurf_vscodium_extensions_policy.md` §GitHub Copilot Policy and flag that exact `product.json` values are unresolved. Do not invent values.

**Compatibility triage:**
> For any unlisted extension, follow the triage protocol in `@docs/standards/windsurf/windsurf_vscodium_extensions_policy.md` §Extension Compatibility Triage before recommending install.

---

## Policy Gaps and Review Triggers

| Gap | Status | Unblock Condition |
|---|---|---|
| Copilot `product.json` exact values (`trustedExtensionAuthAccess`, `defaultChatAgent`) | PROVISIONAL | Fetch and review Copilot CONTRIBUTING guide |
| Copilot auth/licensing in non-Microsoft builds | UNSUPPORTED | Review GitHub/Microsoft licensing policy for Copilot outside VS Code |
| Non-MS third-party extension compatibility catalogue | UNDOCUMENTED UPSTREAM | Case-by-case triage; update policy on discovery |
| `extensionAllowedProposedApi` additions | CASE-BY-CASE | Individual review per addition |
| Self-hosted gallery adoption | OPEN | Revisit if compliance or air-gap requirements arise |
| Live Share replacement | NOT DOCUMENTED | No upstream VSCodium replacement confirmed |
| Remote - Containers replacement | NOT DOCUMENTED | No upstream VSCodium replacement confirmed |

---

## Maintenance and Refresh Rules

- Refresh `@docs/external/vscodium/` source notes when upstream VSCodium docs change (watch: `github.com/VSCodium/vscodium/docs/`).
- Re-evaluate this policy after any upstream VSCodium release that changes `product.json` defaults or extension compatibility.
- Promote PROVISIONAL sections to FINAL only after all listed unblock conditions are satisfied.
- Do not add extensions to the approved replacement list without a confirmed Open VSX source and VSCodium-project backing.
- Log all policy changes in `@docs/standards/windsurf/windsurf_vscodium_decision_log.md`.
