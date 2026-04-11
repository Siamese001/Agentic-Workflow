# Windsurf VSCodium Decision Log

## Purpose

Durable record of all decisions, assumptions, and constraints that shaped the VSCodium extensions policy for this repo. Each entry is a stable reference point for future reviews, reversals, or escalations. Entries are not deleted — superseded decisions are marked with status SUPERSEDED and linked to the replacing entry.

---

## Current Baseline Decision

Open VSX (`open-vsx.org`) is the default and sole approved extension gallery for VSCodium in this repo. Visual Studio Marketplace is blocked as a hard legal constraint. Named Microsoft-ecosystem extensions are blocked. Approved replacements are on record. GitHub Copilot and non-Microsoft third-party compatibility are provisional.

---

## Accepted Assumptions

- This repo uses VSCodium, not official Microsoft VS Code.
- The VSCodium project's upstream documentation is the authoritative source for compatibility facts.
- Policy decisions below are bounded by what the local source notes (`@docs/external/vscodium/`) support. Where sources are partial, decisions are marked PROVISIONAL.
- No facts have been sourced from web search or inferred beyond the local source notes.

---

## Final Decisions

---

### D001 — Default Extension Gallery: Open VSX

- **Decision:** Open VSX Registry (`open-vsx.org`) is the default and sole approved extension gallery.
- **Rationale:** VSCodium's `product.json` defaults to Open VSX out of the box. No reconfiguration required. Microsoft Marketplace is legally blocked (see D002). Open VSX is the only compliant gallery with a documented VSCodium adapter.
- **Source:** `@docs/external/vscodium/extensions.md` §OpenVSX Usage, §Marketplace Strategy
- **Status:** FINAL

---

### D002 — Visual Studio Marketplace: Hard Block

- **Decision:** Visual Studio Marketplace (`marketplace.visualstudio.com`) is blocked. This is a hard legal constraint — not a preference and not overridable by any developer-level configuration.
- **Rationale:** Microsoft's Terms of Use explicitly restrict the marketplace to "Visual Studio Products and Services." VSCodium is not a Microsoft product. Extensions on the marketplace may also carry independent licenses forbidding non-Microsoft use and may include telemetry. The block applies equally to direct installs, `.vsix` redistribution sourced from the marketplace, and any `product.json` or environment variable override pointing at the marketplace.
- **Source:** `@docs/external/vscodium/extensions.md` §Visual Studio Marketplace, §Marketplace Strategy
- **Status:** FINAL

---

### D003 — Named Incompatible Extension Blocklist

- **Decision:** The following eight extensions are blocked in this repo:
  `ms-vscode.cpptools`, `ms-python.python`, `MS-vsliveshare.vsliveshare`,
  `ms-vscode-remote.remote-containers`, `ms-vscode-remote.remote-ssh`,
  `ms-vscode-remote.remote-ssh-edit`, `ms-vscode-remote.remote-wsl`,
  `James-Yu.latex-workshop`.
- **Rationale:** All eight are confirmed incompatible by the VSCodium project. Seven are blocked by a dual mechanism: Microsoft license restriction AND runtime product ID check. LaTeX Workshop is blocked by an independent maintainer decision (not a Microsoft license issue). Both blocking mechanisms are independent — the `extensionAllowedProposedApi` workaround does not reliably bypass either.
- **Source:** `@docs/external/vscodium/extensions-compatibility.md` §Confirmed Incompatible Extensions
- **Status:** FINAL

---

### D004 — Approved Replacement Extensions

- **Decision:** The following Open VSX extensions are the approved replacements for blocked Microsoft-ecosystem extensions:
  - C/C++ editing: `llvm-vs-code-extensions.vscode-clangd`
  - C/C++ debugging: `webfreak.debug`
  - Python: `detachhead.basedpyright`
  - Remote SSH: `jeanp413.open-remote-ssh` (requires `AllowTcpForwarding yes`)
  - Remote WSL: `jeanp413.open-remote-wsl`
- **Rationale:** All five are confirmed by the VSCodium project as functional replacements. All are available on Open VSX. No confirmed replacement exists for Live Share, Remote - Containers, or Remote - SSH: Editing Config Files.
- **Source:** `@docs/external/vscodium/extensions-compatibility.md` §Replacements
- **Status:** FINAL

---

### D005 — Proprietary Debugger Block

- **Decision:** The C# debugger bundled with `OmniSharp/omnisharp-vscode` and the C++ Windows debugger bundled with `Microsoft/vscode-cpptools` are blocked. Approved C# debug path: Samsung `netcoredbg`. Approved C++ debug path: `webfreak.debug` (Native Debug).
- **Rationale:** Both debuggers are restrictively licensed to official VS Code builds only. This is documented by the respective extension maintainers (omnisharp-vscode#2491, vscode-cpptools#21).
- **Source:** `@docs/external/vscodium/extensions.md` §Proprietary Debugging Tools
- **Status:** FINAL

---

### D006 — Manual `.vsix` Fallback: Permitted from Upstream Source Repos

- **Decision:** Manual `.vsix` installation is permitted as a fallback when an extension is unavailable on Open VSX, provided the `.vsix` is sourced from the extension's own upstream release page (e.g., the extension's GitHub Releases). `.vsix` files sourced from or redistributed via Visual Studio Marketplace are not permitted.
- **Rationale:** Explicitly documented as a fallback path by the VSCodium project. The distinction between upstream source repo and VS Marketplace is a legal requirement, not a technical one.
- **Source:** `@docs/external/vscodium/extensions.md` §Fallback Paths
- **Status:** FINAL

---

### D007 — VSIX Manager: Approved Fallback Tooling

- **Decision:** The VSIX Manager extension is an approved tool for multi-marketplace management, local `.vsix` management, GitHub/Forgejo release installs, and offline/fallback scenarios.
- **Rationale:** Documented by the VSCodium project; authored by the main VSCodium maintainer. Supports the same fallback paths approved in D006.
- **Source:** `@docs/external/vscodium/extensions.md` §VSIX Manager Extension
- **Status:** FINAL

---

### D008 — Self-Hosted Gallery: Permitted, Not Required

- **Decision:** Self-hosted Open VSX (Eclipse OSS) and `code-marketplace` (Coder OSS) are permitted enterprise paths. Neither is currently required or adopted.
- **Rationale:** Both are confirmed working options documented by the VSCodium project. Adoption is appropriate for air-gapped, regulated, or compliance-driven environments. No current requirement exists in this repo.
- **Source:** `@docs/external/vscodium/extensions.md` §Self-Hosted Gallery
- **Status:** FINAL

---

### D009 — `extensionAllowedProposedApi`: Case-by-Case Review Only

- **Decision:** Adding any extension ID to `extensionAllowedProposedApi` in a shared or committed `product.json` requires individual review and approval. It is not blanket permitted.
- **Rationale:** This is a partial workaround that does not work if the extension hard-codes a VS Code product ID check. Silent failure is the documented outcome. Blanket approval would create false confidence.
- **Source:** `@docs/external/vscodium/extensions.md` §Proprietary Extensions
- **Status:** FINAL

---

## Provisional Decisions

---

### D010 — GitHub Copilot: Individual Developer Choice (PROVISIONAL)

- **Decision:** GitHub Copilot usage in VSCodium is neither enforced nor blocked. It is treated as an individual developer choice pending policy finalisation.
- **Rationale:** The configuration mechanism is documented (settings flag + custom `product.json` + Copilot CONTRIBUTING guide). However, exact `product.json` property values (`trustedExtensionAuthAccess`, `defaultChatAgent`), authentication flow details, and licensing implications for use in a non-Microsoft editor build are **unsupported from local sources**. A complete, enforceable policy cannot be written without these facts.
- **Source:** `@docs/external/vscodium/ext-github-copilot.md`
- **Status:** PROVISIONAL
- **Unblock condition:** Fetch and review `github.com/microsoft/vscode-copilot-chat/blob/main/CONTRIBUTING.md`; review GitHub/Microsoft licensing terms for Copilot outside VS Code builds.

---

### D011 — Non-Microsoft Third-Party Extension Compatibility: Case-by-Case (PROVISIONAL)

- **Decision:** No general policy is set for non-Microsoft third-party extensions. Compatibility is assessed case-by-case on discovery. Findings are documented in the triage log and may trigger a policy update.
- **Rationale:** The upstream VSCodium project does not catalogue non-Microsoft third-party extension risks. The local source notes have no coverage of this category beyond the LaTeX Workshop exception (which is maintainer-stated, not derived from a general rule). Inventing a blanket stance without upstream backing would exceed the evidence.
- **Source:** `@docs/external/vscodium/extensions-compatibility.md` §Supported vs. Unsupported
- **Status:** PROVISIONAL
- **Unblock condition:** Accumulate case-by-case triage findings; re-evaluate when pattern emerges or upstream VSCodium project publishes broader compatibility guidance.

---

## Known Constraints

- Microsoft Marketplace ToU prohibits non-Microsoft product access — no workaround exists within legal bounds.
- Seven confirmed-incompatible extensions have a dual blocking mechanism (license + runtime product ID check) that cannot be reliably bypassed.
- LaTeX Workshop incompatibility is independent of Microsoft licensing — it is a maintainer-stated position.
- The `extensionAllowedProposedApi` workaround silently fails for hard-coded product ID checks with no error surfaced to the user.
- VSCodium disables Copilot by default; enabling it requires per-user `product.json` customisation with values not specified in VSCodium docs.

---

## Open Risks

| Risk | Severity | Status |
|---|---|---|
| Copilot `product.json` values unknown — setup instructions incomplete | Medium | OPEN — blocks finalising D010 |
| Copilot auth/licensing outside VS Code — compliance implications unknown | High | OPEN — blocks D010 |
| Non-MS third-party extension compatibility undocumented | Low–Medium | OPEN — case-by-case triage |
| No replacement confirmed for Live Share, Remote - Containers | Medium | OPEN — no upstream path documented |
| `extensionAllowedProposedApi` silent failure risk | Low | MITIGATED — review gate in D009 |

---

## Review Triggers

- Any upstream VSCodium release that changes `product.json` defaults or extension compatibility docs.
- New confirmed-incompatible extension discovered during triage → add to D003 blocklist.
- New confirmed-compatible Open VSX replacement discovered → add to D004.
- Copilot CONTRIBUTING guide reviewed → update D010 to FINAL.
- Compliance or air-gap requirement raised → re-evaluate D008 (self-hosted gallery adoption).
- `extensionAllowedProposedApi` addition proposed → individual review per D009.

---

## Change Log

| Date | Entry | Change | Author |
|---|---|---|---|
| 2026-04-11 | D001–D011 | Initial policy decisions recorded | Policy workflow |
