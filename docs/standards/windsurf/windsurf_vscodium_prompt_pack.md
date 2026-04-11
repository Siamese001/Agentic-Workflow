# Windsurf VSCodium Prompt Pack

## Purpose

Reusable prompt templates for VSCodium extension and marketplace work in this repo. All templates are grounded in the validated policy docs and decision log. Do not modify template wording without also updating those source docs.

---

## How To Use

1. Copy the relevant template block into your Windsurf prompt.
2. Replace bracketed placeholders (`[EXTENSION_ID]`, `[REQUESTED_CAPABILITY]`, etc.) with actual values before submitting.
3. Templates reference `@` file paths — Windsurf will resolve these against the repo root.
4. Templates with a **PROVISIONAL** marker must not be treated as final policy. See the policy file for unblock conditions.

---

## Template 1 — Recommend Marketplace Strategy

```
Objective: Recommend the correct extension gallery strategy for a VSCodium development environment in this repo.

Context files:
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Approved Extension Sources
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Blocked Sources
- @docs/standards/windsurf/windsurf_vscodium_decision_log.md §D001, §D002

Task:
1. State the approved default gallery and confirm no configuration is required to use it.
2. State whether Visual Studio Marketplace is blocked or merely discouraged, and cite the legal basis from the policy file.
3. List the two permitted self-hosted gallery options and their adoption status in this repo.
4. Do not recommend any gallery not listed in §Approved Extension Sources.

Output format:
- Default gallery: one line
- VS Marketplace status: one line, must include the word BLOCKED
- Self-hosted options: compact bullet list with adoption status
- No prose beyond what is listed above

Stop: After the three output items are complete. Do not add recommendations beyond what the policy file states.
```

---

## Template 2 — Evaluate Extension Compatibility Risk

```
Objective: Assess whether a named extension is safe to install in VSCodium in this repo.

Input required: [EXTENSION_ID] — provide the exact extension ID (e.g., ms-python.python)

Context files:
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Blocked Extensions
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Approved Replacement Extensions
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Extension Compatibility Triage
- @docs/standards/windsurf/windsurf_vscodium_decision_log.md §D003, §D004, §D011

Task:
1. Check whether [EXTENSION_ID] appears in the §Blocked Extensions table.
   - If yes: state BLOCKED, cite the block reason from the table, and name the approved replacement if one exists in §Approved Replacement Extensions.
   - If no: proceed to step 2.
2. Check whether [EXTENSION_ID] is a Microsoft-published extension (publisher prefix ms-* or MS-*).
   - If yes: flag as high risk — dual-mechanism incompatibility possible even if not yet listed.
3. If the extension is not Microsoft-published and not on the blocklist: apply the triage protocol from §Extension Compatibility Triage. State that compatibility is PROVISIONAL — case-by-case per D011.
4. Do not invent compatibility verdicts for extensions not covered by the policy file.

Output format:
- Verdict: BLOCKED / HIGH RISK / PROVISIONAL (one word + one line reason)
- Approved replacement (if applicable): extension ID + Open VSX source
- Required action: one line

Stop: After verdict, replacement (if any), and required action. Do not add general compatibility advice.
```

---

## Template 3 — Assess a Proprietary Extension Request

```
Objective: Assess whether a requested proprietary or Microsoft-ecosystem extension can be used in VSCodium in this repo, and identify the correct path forward.

Input required: [EXTENSION_ID] and [REQUESTED_CAPABILITY] (e.g., "ms-vscode-remote.remote-ssh" / "SSH remote development")

Context files:
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Blocked Extensions
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Approved Replacement Extensions
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Proprietary Debugger Policy
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Extension Compatibility Triage
- @docs/standards/windsurf/windsurf_vscodium_decision_log.md §D003, §D004, §D005, §D009

Task:
1. Confirm whether [EXTENSION_ID] is on the blocklist. If yes, state BLOCKED and cite the dual-mechanism rule from §Canonical Principles (policy file line 42).
2. Check whether an approved Open VSX replacement covers [REQUESTED_CAPABILITY]. If yes, name it with its Open VSX ID and note any configuration requirements (e.g., AllowTcpForwarding).
3. Assess whether extensionAllowedProposedApi is a viable workaround: state that it is a partial workaround only and that it silently fails if the extension hard-codes a VS Code product ID check (per D009). Do not recommend it without flagging this risk.
4. If no replacement is confirmed in the policy file, explicitly state that no replacement is documented in local sources — do not invent one.

Output format:
- Extension status: BLOCKED or NOT LISTED (one line)
- Replacement available: extension ID + Open VSX ID, or "None confirmed in local sources"
- extensionAllowedProposedApi viability: one line
- Required action: one line

Stop: After the four output items. Do not propose workarounds not covered in the policy file.
```

---

## Template 4 — Assess Copilot Setup Implications

```
⚠️ PROVISIONAL — This template covers a section of policy that is not fully settled.
Do not treat output as final policy. See §GitHub Copilot Policy (PROVISIONAL) in the policy file.

Objective: Assess what is and is not policy-settled about GitHub Copilot in VSCodium for this repo, and state the interim stance clearly.

Context files:
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §GitHub Copilot Policy (PROVISIONAL)
- @docs/standards/windsurf/windsurf_vscodium_decision_log.md §D010

Task:
1. State the default Copilot status in VSCodium (enabled or disabled by default).
2. List only the source-backed configuration steps from §Minimum required steps. Do not complete or fill in the missing product.json values — state explicitly that exact values for trustedExtensionAuthAccess and defaultChatAgent are not specified in local sources and must be retrieved from the Copilot CONTRIBUTING guide.
3. State the four unresolved items from §What remains unresolved verbatim.
4. State the interim repo stance from §Interim stance: individual developer choice, neither enforced nor blocked.
5. Do not assert any licensing or authentication claim about Copilot in non-Microsoft builds. These are explicitly unsupported from local sources.

Output format:
- Default status: one line
- Source-backed setup steps: numbered list, maximum 4 items
- Unresolved items: bullet list, verbatim from policy file
- Interim stance: one line
- PROVISIONAL banner: must appear at the top of the response

Stop: After the four output sections. If the user asks for exact product.json values, state they are unsupported from local sources and reference §Policy Gaps and Review Triggers in the policy file.
```

---

## Template 5 — Propose Fallback When Open VSX Lacks an Extension

```
Objective: Identify the correct ordered fallback path when a required extension is not available on Open VSX.

Input required: [EXTENSION_ID] and [CAPABILITY_NEEDED]

Context files:
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Approved Fallback Paths
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Approved Extension Sources
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Blocked Sources
- @docs/standards/windsurf/windsurf_vscodium_decision_log.md §D006, §D007, §D008

Task:
1. Confirm [EXTENSION_ID] is absent from Open VSX (user must confirm; do not assert availability without verification).
2. Apply the fallback order from §Approved Fallback Paths:
   a. Request publication to open-vsx.org — state both paths (maintainer request, or PR to open-vsx/publish-extensions).
   b. Manual .vsix from the extension's own upstream release page only. Explicitly state: .vsix files sourced from, redistributed from, or originally downloaded from Visual Studio Marketplace by any party are not permitted regardless of how they are delivered.
   c. VSIX Manager for local file management or multi-source fallback.
   d. Self-hosted gallery if air-gapped or regulated context applies.
3. If [EXTENSION_ID] is on the §Blocked Extensions list: state the fallback path does not apply — the block is due to incompatibility, not gallery absence. Redirect to §Approved Replacement Extensions.
4. Do not suggest sourcing .vsix from Visual Studio Marketplace under any framing.

Output format:
- Fallback path: ordered list a–d with applicability note for each
- VS Marketplace reminder: explicit one-line prohibition
- Blocked extension redirect (if applicable): one line

Stop: After the ordered fallback list and VS Marketplace prohibition line. Do not add general extension management advice.
```

---

## Template 6 — Validate a Planned Config Change Against Repo Policy

```
Objective: Check whether a planned VSCodium configuration change is compliant with repo policy before it is applied.

Input required: Describe the planned change — e.g., "Add marketplace.visualstudio.com as serviceUrl in product.json" or "Add ms-vscode-remote.remote-wsl to extensionAllowedProposedApi"

Context files:
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Alternate Gallery Configuration
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Blocked Sources
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Blocked Extensions
- @docs/standards/windsurf/windsurf_vscodium_extensions_policy.md §Extension Compatibility Triage
- @docs/standards/windsurf/windsurf_vscodium_decision_log.md §D002, §D009

Task:
1. Identify which policy section(s) govern the planned change.
2. Return a verdict: COMPLIANT / NON-COMPLIANT / REQUIRES REVIEW.
   - NON-COMPLIANT: change points any gallery config at marketplace.visualstudio.com, installs a blocked extension, or sources a .vsix from VS Marketplace by any party.
   - REQUIRES REVIEW: change adds an ID to extensionAllowedProposedApi (per D009 — individual review required; silent failure risk must be assessed).
   - COMPLIANT: change uses approved sources, approved extensions, and follows the documented product.json shape from §Alternate Gallery Configuration.
3. Cite the exact policy section and decision log entry that supports the verdict.
4. If the change touches GitHub Copilot configuration: flag the section as PROVISIONAL, cite §GitHub Copilot Policy (PROVISIONAL), and state that the change cannot be fully validated until D010 is resolved.
5. Do not approve any change that the policy file does not explicitly permit.

Output format:
- Verdict: COMPLIANT / NON-COMPLIANT / REQUIRES REVIEW (one word + one line reason)
- Governing policy section: exact section name + decision log entry ID
- Action required: one line
- Provisional flag (if Copilot-related): one line

Stop: After verdict, governing section, and action required. Do not suggest alternative config shapes unless the policy file explicitly documents them.
```

---

## Maintenance Notes

- Template wording is derived from `@docs/standards/windsurf/windsurf_vscodium_extensions_policy.md` (v1.0, 2026-04-11) and `@docs/standards/windsurf/windsurf_vscodium_decision_log.md`.
- If either policy doc is updated, audit all templates for stale section references, decision log IDs, or changed provisional boundaries before reusing.
- Templates 4 and 5 contain PROVISIONAL markers that must be promoted or removed only after D010 (Copilot) and D011 (non-MS third-party) are resolved in the decision log.
- Do not add new templates to this file without a corresponding entry in the decision log.
