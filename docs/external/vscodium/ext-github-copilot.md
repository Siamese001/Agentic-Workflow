# VSCodium — Extension: GitHub Copilot Source Notes

**Source of truth:** https://raw.githubusercontent.com/VSCodium/vscodium/master/docs/ext-github-copilot.md  
**Retrieval date:** 2026-04-11  
**Status:** Full coverage of the upstream document. Note: upstream doc is brief; limited detail available.

---

## GitHub Copilot Implications

- In VSCodium, **Copilot features are disabled and not configured by default** — unlike official VS Code.
- Copilot is not a simple install; it requires explicit per-user configuration steps.

## Required Steps to Enable Copilot

### Step 1 — Settings change
Add to user settings:
```json
"chat.disableAIFeatures": false
```

### Step 2 — Custom `product.json`
Create a custom `product.json` at the user config location for the platform:
- **Windows:** `%APPDATA%\VSCodium` or `%USERPROFILE%\AppData\Roaming\VSCodium`
- **macOS:** `~/Library/Application Support/VSCodium`
- **Linux:** `$XDG_CONFIG_HOME/VSCodium` or `~/.config/VSCodium`

(Replace `VSCodium` with `VSCodium - Insiders` if using the Insiders build.)

### Step 3 — Follow upstream Copilot CONTRIBUTING guide
Follow the [Running with Code OSS](https://github.com/microsoft/vscode-copilot-chat/blob/main/CONTRIBUTING.md#running-with-code-oss) guide using the `product.json` created above.

Required properties to add to `product.json`:
- `trustedExtensionAuthAccess`
- `defaultChatAgent`

Exact values for those properties are **not** specified in the VSCodium doc; the upstream Copilot CONTRIBUTING guide is the authoritative source.

## Fallback Path

- **Unsupported from local sources.** The upstream VSCodium doc does not document a fallback if Copilot cannot be configured. No alternative AI assistant is suggested in this document.

## Supported vs. Unsupported

- **Supported:** The configuration mechanism (settings flag + product.json + upstream Copilot guide reference) is fully documented.
- **Unsupported from local sources:**
  - Exact `product.json` property values for `trustedExtensionAuthAccess` and `defaultChatAgent` — must be retrieved from the Copilot CONTRIBUTING guide.
  - Whether Copilot works with the Insiders build beyond the path substitution note.
  - Authentication flow details (GitHub OAuth token handling in VSCodium).
  - Licensing implications of using Copilot in a non-Microsoft editor build.
