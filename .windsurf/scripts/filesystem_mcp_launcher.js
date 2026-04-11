#!/usr/bin/env node
/**
 * filesystem_mcp_launcher.js
 *
 * Stable, version-pin-free launcher for @modelcontextprotocol/server-filesystem.
 *
 * Design:
 *   - Uses process.execPath (the running node binary) — no hard-coded fnm path.
 *   - Resolves the server script via `npm prefix -g` — survives Node upgrades and
 *     fnm version switches without any config edits.
 *   - No npx, no npm registry fetch, no shell dependency.
 *   - Fails with actionable diagnostics if Node or the package is missing.
 *
 * Usage (invoked by Windsurf from mcp_config.json):
 *   node .windsurf/scripts/filesystem_mcp_launcher.js <allowed-directory>
 *
 * Operator note: docs/guides/filesystem_mcp_operations.md
 */

"use strict";

const { execFileSync, spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const PACKAGE_SUBPATH = path.join(
  "node_modules",
  "@modelcontextprotocol",
  "server-filesystem",
  "dist",
  "index.js"
);

function die(msg) {
  process.stderr.write("[filesystem_mcp_launcher] FATAL: " + msg + "\n");
  process.exit(1);
}

// --- Resolve global npm prefix dynamically ---
// Use node_modules/npm/bin/npm-cli.js co-located with process.execPath.
// This is the same approach as npx.cmd and works on Windows without
// needing 'npm' in PATH (npm is a .cmd file, not directly spawnSync-able).
const nodeDir = path.dirname(process.execPath);
const npmCliPath = path.join(nodeDir, "node_modules", "npm", "bin", "npm-cli.js");

if (!fs.existsSync(npmCliPath)) {
  die(
    "npm-cli.js not found at: " + npmCliPath +
      "\n  Expected alongside node.exe. Ensure npm is bundled with this Node install." +
      "\n  See docs/guides/filesystem_mcp_operations.md"
  );
}

let globalPrefix;
try {
  globalPrefix = execFileSync(process.execPath, [npmCliPath, "prefix", "-g"], {
    encoding: "utf8",
    timeout: 10000,
    windowsHide: true,
  }).trim();
} catch (e) {
  die(
    "Cannot determine npm global prefix (node npm-cli.js prefix -g failed: " +
      e.message +
      "). See docs/guides/filesystem_mcp_operations.md"
  );
}

if (!globalPrefix) {
  die(
    "npm prefix -g returned empty string. " +
      "Ensure the active Node version is set via fnm. " +
      "See docs/guides/filesystem_mcp_operations.md"
  );
}

// --- Locate the server script ---
const serverScript = path.join(globalPrefix, PACKAGE_SUBPATH);

if (!fs.existsSync(serverScript)) {
  die(
    "server-filesystem not found at: " +
      serverScript +
      "\n  Install with: npm install -g @modelcontextprotocol/server-filesystem@2026.1.14" +
      "\n  Then restart Windsurf." +
      "\n  See docs/guides/filesystem_mcp_operations.md"
  );
}

// --- Collect allowed-directory arguments ---
const allowedDirs = process.argv.slice(2);
if (allowedDirs.length === 0) {
  die(
    "No allowed directory argument provided. " +
      "Expected: node filesystem_mcp_launcher.js <allowed-dir>"
  );
}

// --- Spawn the MCP server ---
// Use process.execPath so the child uses exactly the same node binary.
const child = spawn(process.execPath, [serverScript, ...allowedDirs], {
  stdio: "inherit",
  windowsHide: true,
});

child.on("error", (err) => {
  die("Failed to start server-filesystem: " + err.message);
});

child.on("exit", (code, signal) => {
  process.exit(code !== null ? code : 1);
});
