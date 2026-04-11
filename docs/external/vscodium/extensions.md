# VSCodium — Extensions and Marketplace Source Notes

**Source of truth:** https://raw.githubusercontent.com/VSCodium/vscodium/master/docs/extensions.md  
**Retrieval date:** 2026-04-11  
**Status:** Full coverage of all sections.

---

## Marketplace Strategy

- VSCodium uses extensions for additional features, identical to VS Code's extension model.
- Microsoft **prohibits** use of the Microsoft Marketplace (`marketplace.visualstudio.com`) by any non-Microsoft product and prohibits redistribution of `.vsix` files sourced from it.
- Reference: https://github.com/microsoft/vscode/issues/31168

## OpenVSX Usage

- Default `product.json` in VSCodium points to [open-vsx.org](https://open-vsx.org/) as the extension gallery.
- Open VSX implements an adapter to the Marketplace API used by VS Code.
- Open VSX is described as a relatively new project; extension coverage is a known gap vs. Visual Studio Marketplace.
- Using the Extensions view in VSCodium defaults to Open VSX — no configuration required.

## Alternate Marketplace Configuration

Two mechanisms to switch from the pre-set Open VSX Registry:

**Environment variables (all strings, set before launch):**
- `VSCODE_GALLERY_SERVICE_URL` *(required)*
- `VSCODE_GALLERY_ITEM_URL` *(required)*
- `VSCODE_GALLERY_EXTENSION_URL_TEMPLATE` *(required)*
- `VSCODE_GALLERY_CACHE_URL` *(optional)*
- `VSCODE_GALLERY_CONTROL_URL` *(optional)*
- `VSCODE_GALLERY_RESOURCE_URL_TEMPLATE` *(optional)*

**Custom `product.json`** at per-OS user config location:
- Windows: `%APPDATA%\VSCodium` or `%USERPROFILE%\AppData\Roaming\VSCodium`
- macOS: `~/Library/Application Support/VSCodium`
- Linux: `$XDG_CONFIG_HOME/VSCodium` or `~/.config/VSCodium`

`product.json` shape:
```jsonc
{
  "extensionsGallery": {
    "serviceUrl": "",       // required
    "itemUrl": "",          // required
    "cacheUrl": "",
    "controlUrl": "",
    "extensionUrlTemplate": "",  // required
    "resourceUrlTemplate": ""
  }
}
```

## Self-Hosted Gallery

Two confirmed working options:

1. **Open VSX (self-hosted)** — Eclipse open-source project. The public instance (run by Eclipse Foundation) is VSCodium's default endpoint; an enterprise can host their own instance. Provides a server, web UI, and CLI (`ovsx`) for publishing.
2. **code-marketplace** — Coder open-source project. Self-contained Go binary. Reads extensions from file storage and provides an API for VS Code–compatible editors. No frontend; no extension-author upload mechanism.

Use cases for self-hosting: regulated or security-conscious industries, air-gapped environments, enterprise extension control.

## Proprietary Debugging Tools

- The **C# debugger** bundled with Microsoft's `OmniSharp/omnisharp-vscode` extension is restrictively licensed to work **only with official VS Code builds**.
- The **C++ Windows debugger** bundled with `Microsoft/vscode-cpptools` is similarly restricted.
- References: omnisharp-vscode#2491, vscode-cpptools#21.
- **Workaround for C# debugging:** Use Samsung's open-source [netcoredbg](https://github.com/Samsung/netcoredbg). See VSCodium issue #82 for setup instructions.

## Proprietary Extensions

- Some extensions (e.g., Remote Development pack) only function with the official VS Code product due to hard-coded product ID checks.
- **Partial workaround:** Add the extension's internal ID to `extensionAllowedProposedApi` in the VSCodium installation's `product.json`:
  ```jsonc
  "extensionAllowedProposedApi": [
    "ms-vscode-remote.vscode-remote-extensionpack",
    "ms-vscode-remote.remote-wsl"
  ]
  ```
- This workaround does **not** work if the extension is hard-coded to check for the official VS Code product ID.

## Visual Studio Marketplace Usage (Unsupported Path)

- VS Marketplace Terms of Use explicitly restrict usage to "Visual Studio Products and Services."
- Extensions on VS Marketplace may have licenses that explicitly forbid use in non-Microsoft products and may include telemetry.
- VSCodium project offers no support for configurations that infringe these terms.

## VSIX Manager Extension (Fallback Path)

- The [VSIX Manager](https://github.com/zokugun/vscode-vsix-manager) extension (authored by the main VSCodium maintainer) supports:
  - Installing/managing extensions from multiple marketplaces simultaneously.
  - Managing local `.vsix` files.
  - Installing directly from GitHub/Forgejo release pages.
  - Fallback options when a marketplace is temporarily inaccessible.
  - Enterprise use: private/self-hosted marketplaces alongside public ones.

## Fallback Paths When an Extension Is Unavailable

1. Ask extension maintainer to publish to open-vsx.org (publishing process documented in Open VSX Wiki).
2. Open a PR to [open-vsx/publish-extensions](https://github.com/open-vsx/publish-extensions) for the `@open-vsx` service account to publish on the extension's behalf.
3. Download the `.vsix` directly from the extension's source repo release page and install manually.
4. Use VSIX Manager extension for multi-marketplace + fallback management.

## Supported vs. Unsupported

- **Supported:** Full coverage of all sections in the upstream doc.
- **Unsupported from local sources:** None — complete content retrieved.
