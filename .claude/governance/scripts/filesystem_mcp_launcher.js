#!/usr/bin/env node
/**
 * filesystem_mcp_launcher.js
 *
 * Hardened launcher for @modelcontextprotocol/server-filesystem.
 *
 * Design goals:
 *   - Uses process.execPath (the running node binary), so no hard-coded fnm path.
 *   - Resolves the server script via `npm prefix -g`, so Node upgrades do not require config edits.
 *   - Keeps stdout reserved for MCP JSON-RPC traffic only.
 *   - Uses explicit stdio proxying instead of bare `inherit`, allowing readiness detection and
 *     startup timeout enforcement for the child MCP server.
 *   - Fails fast with actionable diagnostics if Node, npm, or the package is missing.
 *   - Cleans up the child process deterministically on wrapper shutdown.
 *
 * Usage (invoked from mcp.json):
 *   node .claude/governance/scripts/filesystem_mcp_launcher.js <allowed-directory> [additional-allowed-directory...]
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

const STARTUP_TIMEOUT_MS = 15000;
const READY_MARKER = "Secure MCP Filesystem Server running on stdio";

function die(msg, exitCode = 1) {
  process.stderr.write("[filesystem_mcp_launcher] FATAL: " + msg + "\n");
  process.exit(exitCode);
}

function writeStderr(msg) {
  process.stderr.write("[filesystem_mcp_launcher] " + msg + "\n");
}

function clearTimer(timer) {
  if (timer) {
    clearTimeout(timer);
  }
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
    maxBuffer: 1024 * 1024,
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
      "\n  Then restart the editor." +
      "\n  See docs/guides/filesystem_mcp_operations.md"
  );
}

// --- Collect allowed-directory arguments ---
const allowedDirs = process.argv.slice(2);
if (allowedDirs.length === 0) {
  die(
    "No allowed directory argument provided. " +
      "Expected: node filesystem_mcp_launcher.js <allowed-dir> [additional-allowed-dir...]"
  );
}

// --- W2 hardening: validate each allowed dir against a denylist ---
// The filesystem MCP server enforces its own path scoping to the provided
// allowed dirs, but we additionally refuse to even launch when any allowed
// dir resolves inside a forbidden zone (user home, system dirs). This guards
// against misconfigured mcp.json invocations and rogue user-home
// config overrides that point the server at sensitive territory.
const FORBIDDEN_PATH_PREFIXES = [
  // Windows user home — contains .env, .ssh, tokens
  path.resolve("C:/Users"),
  // Windows system dirs
  path.resolve("C:/Windows"),
  "C:/Program Files",
  "C:/ProgramData",
  // POSIX system dirs
  "/etc",
  "/root",
  "/var/lib",
  "/usr",
  "/sys",
  "/proc",
  // Home dirs on macOS / Linux
  "/Users",
  "/home",
];

function isInsideForbiddenZone(dir) {
  const resolved = path.resolve(dir);
  const resolvedLower = resolved.toLowerCase();
  // Only block if the allowed dir is EXACTLY a forbidden prefix or strictly
  // inside one. A repo path under C:/Users/<name>/Git/<repo> is allowed by
  // intent (user workspaces live there) — so we exempt any path that passes
  // through the repo root (AGENTIC_REPO_ROOT env or process.cwd() fallback).
  const repoRoot = path.resolve(
    process.env.AGENTIC_REPO_ROOT || process.cwd()
  ).toLowerCase();
  if (resolvedLower.startsWith(repoRoot)) {
    return false; // repo root itself overrides forbidden-prefix match
  }
  for (const prefix of FORBIDDEN_PATH_PREFIXES) {
    const p = path.resolve(prefix).toLowerCase();
    if (resolvedLower === p || resolvedLower.startsWith(p + path.sep)) {
      return true;
    }
  }
  return false;
}

for (const dir of allowedDirs) {
  if (isInsideForbiddenZone(dir)) {
    die(
      "Allowed directory " + dir + " resolves inside a forbidden zone. " +
      "Filesystem MCP refuses to expose system dirs, user home, or /etc. " +
      "Check the repo MCP config and AGENTIC_REPO_ROOT. " +
      "See docs/guides/filesystem_mcp_operations.md"
    );
  }
}

// --- Spawn the MCP server ---
// Do NOT use stdio: "inherit" here.
// We proxy stdin/stdout/stderr explicitly so we can:
//   1) keep stdout clean for MCP traffic,
//   2) detect child readiness from stderr,
//   3) enforce a bounded startup timeout,
//   4) cleanly tear down the child on parent exit.
const child = spawn(process.execPath, [serverScript, ...allowedDirs], {
  stdio: ["pipe", "pipe", "pipe"],
  windowsHide: true,
  shell: false,
  cwd: path.resolve(allowedDirs[0]),
  env: process.env,
});

let isReady = false;
let hasExited = false;
let stderrBuffer = "";
let startupTimer = null;

function markReady() {
  if (isReady) {
    return;
  }
  isReady = true;
  clearTimer(startupTimer);
}

function killChild(signal = "SIGTERM") {
  if (hasExited || child.killed) {
    return;
  }
  try {
    child.kill(signal);
  } catch (_) {
    // Ignore secondary cleanup failures.
  }
}

function hardFailStartup(msg) {
  clearTimer(startupTimer);
  writeStderr(msg);
  killChild("SIGTERM");
  setTimeout(() => killChild("SIGKILL"), 750).unref();
  setTimeout(() => process.exit(1), 1000).unref();
}

startupTimer = setTimeout(() => {
  if (!isReady && !hasExited) {
    hardFailStartup(
      "Startup timeout after " + STARTUP_TIMEOUT_MS +
        " ms waiting for filesystem MCP readiness marker. " +
        "The child process likely hung before fully initializing."
    );
  }
}, STARTUP_TIMEOUT_MS);

child.on("error", (err) => {
  hasExited = true;
  clearTimer(startupTimer);
  die("Failed to start server-filesystem: " + err.message);
});

child.stderr.on("data", (chunk) => {
  const text = chunk.toString("utf8");
  process.stderr.write(chunk);

  if (!isReady) {
    stderrBuffer = (stderrBuffer + text).slice(-8192);
    if (stderrBuffer.includes(READY_MARKER)) {
      markReady();
    }
  }
});

child.stdout.on("data", (chunk) => {
  process.stdout.write(chunk);
});

process.stdin.on("error", () => {
  // Ignore stdin proxying errors that can happen during shutdown.
});

child.stdin.on("error", () => {
  // Ignore child stdin write-after-close during shutdown races.
});

process.stdin.pipe(child.stdin);

process.stdin.on("end", () => {
  if (!hasExited) {
    try {
      child.stdin.end();
    } catch (_) {
      // Ignore shutdown races.
    }
  }
});

function forwardAndExit(signal, code) {
  killChild(signal);
  setTimeout(() => process.exit(code), 250).unref();
}

process.on("SIGINT", () => forwardAndExit("SIGINT", 130));
process.on("SIGTERM", () => forwardAndExit("SIGTERM", 143));
process.on("SIGHUP", () => forwardAndExit("SIGHUP", 129));
process.on("exit", () => killChild("SIGTERM"));

child.on("close", (code, signal) => {
  hasExited = true;
  clearTimer(startupTimer);

  if (signal) {
    process.exit(1);
    return;
  }

  process.exit(code !== null ? code : 1);
});
