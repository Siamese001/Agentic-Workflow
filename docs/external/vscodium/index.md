# VSCodium — Index / Overview Source Notes

**Source of truth:** https://raw.githubusercontent.com/VSCodium/vscodium/master/docs/index.md  
**Retrieval date:** 2026-04-11  
**Status:** Full coverage of index/TOC content.

---

## Facts

- VSCodium is a community-driven, freely-licensed binary distribution of Microsoft's VS Code editor.
- Microsoft's VS Code source is MIT-licensed; the distributed product is under a separate not-FLOSS license and includes telemetry/tracking.
- VSCodium clones the `vscode` repo, applies a customized `product.json` that removes Microsoft-specific functionality (telemetry, gallery, logo), and publishes the resulting MIT-licensed binaries to GitHub Releases.
- Telemetry is disabled in VSCodium builds.
- The upstream doc set covers: Getting Started, Telemetry removal, Extensions and Marketplace, Migration from VS Code, Usage, Troubleshooting, and Other Resources.
- The four policy-relevant upstream documents are:
  - `docs/extensions.md` — marketplace, OpenVSX, alternate gallery, self-hosting, proprietary tools/extensions
  - `docs/extensions-compatibility.md` — incompatible extensions and replacements
  - `docs/ext-github-copilot.md` — Copilot configuration in VSCodium
  - `docs/migration.md` — migration from VS Code (out of scope for this policy pack)

## Supported vs. Unsupported

- **Supported:** Full TOC and project identity facts.
- **Unsupported from local sources:** Per-section deep content for Getting Started, Telemetry, Migration — not in scope for this doc pack.
