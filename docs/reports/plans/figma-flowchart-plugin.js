// =============================================================================
// AGENTIC CONTROL FLOW v2 — Figma Plugin Script
// =============================================================================
// HOW TO USE:
// 1. Open Figma → Plugins → Development → New Plugin → "Figma Design" type
// 2. Replace the code in code.ts with this script
// 3. Run the plugin
// =============================================================================

// ---------- HELPERS ----------

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  return { r, g, b };
}

function setFill(node, hex) {
  node.fills = [{ type: "SOLID", color: hexToRgb(hex) }];
}

function setStroke(node, hex, weight) {
  node.strokes = [{ type: "SOLID", color: hexToRgb(hex) }];
  node.strokeWeight = weight || 2;
}

function createCard(x, y, w, h, fillHex, strokeHex, name) {
  const frame = figma.createFrame();
  frame.name = name;
  frame.x = x;
  frame.y = y;
  frame.resize(w, h);
  setFill(frame, fillHex);
  setStroke(frame, strokeHex, 2);
  frame.cornerRadius = 12;
  frame.clipsContent = true;
  return frame;
}

function createText(text, x, y, fontSize, bold, colorHex) {
  const node = figma.createText();
  node.x = x;
  node.y = y;
  node.characters = text;
  node.fontSize = fontSize || 12;
  if (bold) {
    node.fontName = { family: "Inter", style: "Bold" };
  } else {
    node.fontName = { family: "Inter", style: "Regular" };
  }
  if (colorHex) {
    node.fills = [{ type: "SOLID", color: hexToRgb(colorHex) }];
  }
  return node;
}

function createBullets(items, startX, startY, fontSize, colorHex) {
  const nodes = [];
  items.forEach((item, i) => {
    const t = createText("• " + item, startX, startY + i * (fontSize + 6), fontSize, false, colorHex);
    nodes.push(t);
  });
  return nodes;
}

function createPill(text, x, y, fillHex, textHex) {
  const rect = figma.createRectangle();
  rect.x = x;
  rect.y = y;
  rect.resize(text.length * 7 + 20, 24);
  setFill(rect, fillHex);
  rect.cornerRadius = 12;

  const label = createText(text, x + 10, y + 4, 11, true, textHex);
  return [rect, label];
}

function createArrow(x1, y1, x2, y2, colorHex, dashed) {
  const line = figma.createLine();
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);

  line.x = x1;
  line.y = y1;
  line.resize(len, 0);
  line.rotation = -angle;
  setStroke(line, colorHex, 2);

  if (dashed) {
    line.dashPattern = [8, 4];
  }

  // Arrowhead
  const arrow = figma.createPolygon();
  arrow.pointCount = 3;
  arrow.resize(10, 10);
  arrow.x = x2 - 5;
  arrow.y = y2 - 5;
  arrow.rotation = -angle + 90;
  setFill(arrow, colorHex);
  arrow.strokes = [];

  return [line, arrow];
}

function createArrowWithLabel(x1, y1, x2, y2, label, colorHex, dashed) {
  const parts = createArrow(x1, y1, x2, y2, colorHex, dashed);
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;
  const t = createText(label, midX - label.length * 3, midY - 16, 10, false, colorHex);
  t.name = "ArrowLabel: " + label;
  return [...parts, t];
}

function createInnerBox(parent, relX, relY, w, h, fillHex, strokeHex, title, bullets, textColor) {
  const box = figma.createFrame();
  box.name = "Inner: " + title;
  box.x = relX;
  box.y = relY;
  box.resize(w, h);
  setFill(box, fillHex);
  setStroke(box, strokeHex, 1);
  box.cornerRadius = 8;
  box.clipsContent = true;

  const titleNode = createText(title, 8, 6, 11, true, textColor || "#1A1A1A");
  box.appendChild(titleNode);

  if (bullets && bullets.length > 0) {
    const bNodes = createBullets(bullets, 8, 24, 9, textColor || "#333333");
    bNodes.forEach(n => box.appendChild(n));
  }

  parent.appendChild(box);
  return box;
}

// ---------- MAIN ----------

async function main() {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Bold" });

  const page = figma.currentPage;

  // Master frame
  const master = figma.createFrame();
  master.name = "Agentic Control Flow v2";
  master.resize(3200, 2400);
  setFill(master, "#FAFAF8");
  master.clipsContent = false;

  // ======= TITLE =======
  const title = createText(
    "AGENTIC CONTROL FLOW v2: A++ Enforceable L2 Control Spec + Control Plane",
    400, 10, 24, true, "#1A1A2E"
  );
  title.name = "Title";
  master.appendChild(title);

  // ===========================================================
  // L4: KNOWLEDGE SYSTEM (top-center)
  // ===========================================================
  const l4 = createCard(580, 60, 580, 210, "#B8D8F8", "#5A9BD5", "L4-KnowledgeSystem");
  master.appendChild(l4);

  const l4title = createText("L4: KNOWLEDGE SYSTEM", 16, 8, 14, true, "#002B55");
  l4.appendChild(l4title);

  createInnerBox(l4, 12, 36, 270, 160, "#D0E8F8", "#5A9BD5",
    "SEMANTIC MEMORY (KG & Vector DB)",
    ["Ontology Management", "Embedding Services", "Fast Retrieval"],
    "#002B55"
  );

  createInnerBox(l4, 294, 36, 270, 160, "#D0E8F8", "#5A9BD5",
    "EPISODIC MEMORY",
    ["Experience Replay", "Past Trajectories", "Outcome Linking"],
    "#002B55"
  );

  // KG satellite
  const kgSat = createCard(340, 90, 200, 60, "#B8D8F8", "#5A9BD5", "KnowledgeGraph-Satellite");
  master.appendChild(kgSat);
  const kgText = createText("KNOWLEDGE GRAPH\n(Structured Memory)", 10, 8, 10, true, "#002B55");
  kgSat.appendChild(kgText);

  // ===========================================================
  // L1: ADVANCED COGNITIVE ENGINE (top-right)
  // ===========================================================
  const l1 = createCard(1700, 60, 540, 240, "#FFF3B0", "#E6C84D", "L1-CognitiveEngine");
  master.appendChild(l1);

  const l1title = createText("L1: ADVANCED COGNITIVE ENGINE", 16, 8, 14, true, "#4A3800");
  l1.appendChild(l1title);

  createInnerBox(l1, 12, 36, 250, 190, "#FFF8D0", "#E6C84D",
    "WORKING MEMORY (Internal State)",
    ["Schema", "History", "Rules", "Deterministic Time"],
    "#4A3800"
  );

  createInnerBox(l1, 274, 36, 250, 190, "#FFF8D0", "#E6C84D",
    "THOUGHT GENERATION & COGNITIVE SAFETY",
    ["Episodic Memory", "Trajectory Replay", "Prompt Optimization", "Token Management"],
    "#4A3800"
  );

  // ===========================================================
  // L6: EVENT & ANOMALY DETECTION (far left)
  // ===========================================================
  const l6 = createCard(60, 310, 400, 360, "#C8A8E8", "#8B5DAA", "L6-EventAnomalyDetection");
  master.appendChild(l6);

  const l6title = createText("L6: EVENT & ANOMALY DETECTION LAYER", 12, 8, 13, true, "#2A0050");
  l6.appendChild(l6title);

  createBullets([
    "Multi-modal Data Ingestion (Logs, Metrics)",
    "Real-Time Stream Processing",
    "Anomaly Detection (Signal Correlation, ML)",
    "Signal Correlation & Deduplication"
  ], 16, 32, 10, "#2A0050").forEach(n => l6.appendChild(n));

  // NEW: Guardian-to-L6 Contract
  createInnerBox(l6, 12, 110, 376, 130, "#E8E0F0", "#7B68AE",
    "GUARDIAN-TO-L6 CONTRACT (NEW)",
    [
      "GuardianResult schema (guardian_contract.py)",
      "Correlation ID grouping for CI runs",
      "Max 30s runtime, 512KB artifacts, depth=10",
      "POSIX repo-relative paths only"
    ],
    "#2A0050"
  );

  // NEW: Telemetry emissions
  createInnerBox(l6, 12, 250, 376, 100, "#DDD0F0", "#8B5DAA",
    "TELEMETRY EMISSIONS",
    [
      "telemetry.event → Metrics Dashboard",
      "incident.json → Incident Response",
      "aggregate.json → Impact Assessment"
    ],
    "#2A0050"
  );

  // ===========================================================
  // L0: CORE LOGIC & ROUTING (left-center)
  // ===========================================================
  const l0 = createCard(60, 710, 400, 380, "#D4E8C2", "#8CB369", "L0-CoreLogicRouting");
  master.appendChild(l0);

  const l0title = createText("L0: CORE LOGIC & ROUTING", 16, 8, 14, true, "#1A3300");
  l0.appendChild(l0title);

  createInnerBox(l0, 12, 34, 376, 150, "#E0F0D0", "#8CB369",
    "CONTEXTUAL ROUTER & POLICY ENFORCER",
    [
      "Policy Config Verification (Timestamp, Config Versions)",
      "Typed Trace Parsing (Chat, SQL, Stream, Patch)",
      "Strict Routing (Read-Only)",
      "Healing, Human Escalation"
    ],
    "#1A3300"
  );

  // NEW: LCD+ Skeleton
  createInnerBox(l0, 12, 196, 376, 170, "#E0F0E0", "#66BB6A",
    "LCD+ CANONICAL SKELETON (NEW)",
    [
      "6-folder: config/ types/ reasoning/ engines/ validators/ utils/",
      "Nuance: tools/ scripts/ data/",
      "Flat engines (no subfolders)",
      "Dissolved: domain/ shared/ logic_nodes/ core/",
      "489 .py files compile clean",
      "~130 import paths updated"
    ],
    "#1B5E20"
  );

  // ===========================================================
  // L5: GOVERNANCE & SAFETY (center)
  // ===========================================================
  const l5 = createCard(500, 440, 520, 440, "#F2B8C6", "#D35D7A", "L5-GovernanceSafety");
  master.appendChild(l5);

  const l5title = createText("L5: GOVERNANCE & SAFETY", 16, 8, 14, true, "#4A0020");
  l5.appendChild(l5title);

  createInnerBox(l5, 12, 34, 496, 40, "#F8D0DD", "#D35D7A",
    "BUDGET GUARD (Token/Token Checks)",
    [],
    "#4A0020"
  );

  createInnerBox(l5, 12, 82, 496, 140, "#F8D0DD", "#D35D7A",
    "GUARDIAN (VALIDATION GATE)",
    [
      "Decision: Pass → RESULT",
      "Escalate → HIL",
      "Enforces Hard Rules Only",
      "Safety Boundaries",
      "Budget Markers (fast goes)"
    ],
    "#4A0020"
  );

  // NEW: AI-Checking-AI
  createInnerBox(l5, 12, 230, 496, 100, "#FFE4E1", "#CD5C5C",
    "AI-CHECKING-AI REMEDIATION (NEW)",
    [
      "Deterministic Guardian Tests (no heuristic AI validation)",
      "4 violations remediated: Autonomy, Canon, Architecture, Phase5",
      "32 test cases, 8 guardian tests, 98.5%+ health score"
    ],
    "#8B0000"
  );

  // NEW: Compound Suffix + FCA
  createInnerBox(l5, 12, 338, 496, 90, "#FFE4E1", "#CD5C5C",
    "FCA DEDUP + COMPOUND SUFFIX RESOLUTION (NEW)",
    [
      "92 files renamed (compound suffix conflicts)",
      "64+ import paths corrected (reasoning/ vs validators/)",
      "FileClassificationAgent delegates to Classification Kernel"
    ],
    "#8B0000"
  );

  // ===========================================================
  // L3: HUMAN REVIEW GATE (center-right)
  // ===========================================================
  const l3 = createCard(1060, 500, 300, 240, "#FFD699", "#E6A030", "L3-HumanReviewGate");
  master.appendChild(l3);

  const l3title = createText("L3: HUMAN REVIEW GATE", 16, 8, 14, true, "#4A2800");
  l3.appendChild(l3title);

  const l3sub = createText("(APPROVAL QUEUE)", 16, 28, 11, false, "#4A2800");
  l3.appendChild(l3sub);

  createBullets([
    "Approval Audit (RESULT)",
    "Approved Decision",
    "(Remediation Pointer)"
  ], 16, 52, 10, "#4A2800").forEach(n => l3.appendChild(n));

  // AUTO-PASS pill
  const [apRect, apLabel] = createPill("AUTO-PASS (No HIL, No Healing)", 1080, 470, "#4CAF50", "#FFFFFF");
  master.appendChild(apRect);
  master.appendChild(apLabel);

  // ===========================================================
  // L2: SYMMETRIC VALIDATOR-HEALER PIPE (far right)
  // ===========================================================
  const l2 = createCard(1400, 440, 420, 380, "#FFF3B0", "#E6C84D", "L2-ValidatorHealerPipe");
  master.appendChild(l2);

  const l2title = createText("L2: SYMMETRIC VALIDATOR-HEALER PIPE", 12, 8, 13, true, "#4A3800");
  l2.appendChild(l2title);

  const l2sub = createText("(HEALING & ROLLBACK)", 12, 28, 11, false, "#4A3800");
  l2.appendChild(l2sub);

  createBullets([
    "Applies Approved Fix Only",
    "Deterministic Order",
    "Emits RESULT"
  ], 16, 52, 10, "#4A3800").forEach(n => l2.appendChild(n));

  // NEW: Canonical Executors
  createInnerBox(l2, 12, 110, 396, 250, "#E0F0E0", "#66BB6A",
    "6 CANONICAL EXECUTORS (NEW — 190→149 agents)",
    [
      "HOPPipelineExecutor — 9 HOP stages → 1 (apps_lic)",
      "RGValidationExecutor — 4 RG validators → 1 (apps_rg)",
      "LICValidationExecutor — 2 LIC validators → 1 (apps_lic)",
      "ObservabilityProbeExecutor — 6 obs agents → 1 (L6)",
      "RGStrategyExecutor — 3 strategy agents → 1 (apps_rg)",
      "InspectorExecutor — 3 inspectors → 1 (L5)",
      "",
      "19 retirements | 28 merge shims | -4339 LOC",
      "62/62 consolidation tests pass"
    ],
    "#1B5E20"
  );

  // Emit RESULT arrow placeholder
  const emitResult = createText("Emit RESULT →", 1830, 620, 12, true, "#4A3800");
  master.appendChild(emitResult);

  // ===========================================================
  // CI GOVERNANCE BADGE (top-right corner)
  // ===========================================================
  const ciBadge = createCard(2500, 10, 460, 200, "#E8E0F0", "#7B68AE", "CI-GovernanceBadge");
  master.appendChild(ciBadge);

  const ciTitle = createText("CI GOVERNANCE GATES", 16, 8, 13, true, "#2A0050");
  ciBadge.appendChild(ciTitle);

  createBullets([
    "ssot_verify.yml — Blueprint enforcement + phantom",
    "ssot-kernel-guardrail.yml — Shadow logic + 68 tests",
    "guardian-tests.yml — Deterministic guardian tests",
    "agent-sprawl-check.yml — Agent count ceiling",
    "FORBIDDEN in CI: --update-phantom-baseline etc."
  ], 12, 32, 10, "#2A0050").forEach(n => ciBadge.appendChild(n));

  // ===========================================================
  // CONTROL PLANE (bottom full-width section)
  // ===========================================================
  const cp = createCard(40, 1140, 3120, 500, "#E8E0F0", "#7B68AE", "ControlPlane");
  master.appendChild(cp);

  const cpTitle = createText(
    "CONTROL PLANE — Structural Governance & Deterministic Enforcement",
    16, 10, 18, true, "#2A0050"
  );
  cp.appendChild(cpTitle);

  const cpSub = createText(
    "All governance decisions trace to these SSOTs — no heuristic overrides",
    16, 36, 11, false, "#5A4080"
  );
  cp.appendChild(cpSub);

  // --- CP Card 1: Classification Kernel ---
  const cp1 = createCard(68, 1210, 580, 400, "#F0E68C", "#BDB76B", "CP1-ClassificationKernel");
  cp1.dashPattern = [6, 3];
  master.appendChild(cp1);

  const cp1t = createText("CLASSIFICATION KERNEL SSOT", 12, 8, 13, true, "#333300");
  cp1.appendChild(cp1t);
  const cp1path = createText("agentic_core/core/classification_kernel.py", 12, 28, 9, false, "#666633");
  cp1.appendChild(cp1path);

  createBullets([
    "Zero-dependency (stdlib only)",
    "LRU-cached (maxsize=1024)",
    "classify_file_standalone(path) → FileType (20 types)",
    "is_agent_file(path) / is_agent_or_orchestrator(path)",
    "19-priority classification queue",
    "SyntaxError / UnicodeDecodeError → IGNORE + log",
    "classification_cache_context() for batch ops",
    "",
    "0 shadow logic remaining (7→0 liquidated)",
    "68 contract tests (parametrized)",
    "2601 files scanned by guardrail",
    "CI: ssot-kernel-guardrail.yml"
  ], 12, 50, 9, "#333300").forEach(n => cp1.appendChild(n));

  // --- CP Card 2: Blueprint Enforcement ---
  const cp2 = createCard(672, 1210, 580, 400, "#FFE4E1", "#CD5C5C", "CP2-BlueprintEnforcement");
  master.appendChild(cp2);

  const cp2t = createText("BLUEPRINT ENFORCEMENT ENGINE", 12, 8, 13, true, "#8B0000");
  cp2.appendChild(cp2t);
  const cp2path = createText("structure_blueprint/enforcement/ (6 modules)", 12, 28, 9, false, "#AA3333");
  cp2.appendChild(cp2path);

  createBullets([
    "territory_diff — Undeclared/missing subfolders (ceil=20)",
    "leaf_node — No root .py in allow_root_py=False dirs",
    "volatile_rules — No inbound imports to volatile territories",
    "mixin_ast — Naming + flat + AST compliance (50 files)",
    "blueprint_hash — SHA-256 lock over 20 blueprint .py files",
    "cross_layer — Layer inversion detection (3356 edges)",
    "",
    "2751 files parsed | 0 errors",
    "6/6 checks pass | debt headroom=1",
    "Warnings: 18 budgeted (16 opt + 2 debt)",
    "0 unbudgeted warnings | 0 errors",
    "CI: ssot_verify.yml"
  ], 12, 50, 9, "#8B0000").forEach(n => cp2.appendChild(n));

  // --- CP Card 3: Phantom Baseline ---
  const cp3 = createCard(1276, 1210, 580, 400, "#FFE4E1", "#CD5C5C", "CP3-PhantomBaseline");
  master.appendChild(cp3);

  const cp3t = createText("PHANTOM BASELINE LOCK SYSTEM", 12, 8, 13, true, "#8B0000");
  cp3.appendChild(cp3t);
  const cp3path = createText("phantom_baseline.json — Non-growing debt contract", 12, 28, 9, false, "#AA3333");
  cp3.appendChild(cp3path);

  createBullets([
    "current == baseline → PASS (LOCKED)",
    "current < baseline → PASS (improvement, not persisted)",
    "current > baseline → HARD FAIL (no override)",
    "baseline missing → FAIL (unless --init-phantom-baseline)",
    "baseline corrupt → FAIL (unless --repair-phantom-baseline)",
    "",
    "29 phantom = 29 baseline → LOCKED",
    "",
    "FORBIDDEN IN CI:",
    "  --update-phantom-baseline",
    "  --init-phantom-baseline",
    "  --repair-phantom-baseline",
    "  --acknowledge-import-change"
  ], 12, 50, 9, "#8B0000").forEach(n => cp3.appendChild(n));

  // --- CP Card 4: Agent Consolidation ---
  const cp4 = createCard(1880, 1210, 580, 400, "#E0F0E0", "#66BB6A", "CP4-AgentConsolidation");
  master.appendChild(cp4);

  const cp4t = createText("AGENT CONSOLIDATION REGISTRY", 12, 8, 13, true, "#1B5E20");
  cp4.appendChild(cp4t);
  const cp4sub = createText("190 → 149 active agents (target ≤150)", 12, 28, 10, true, "#2E7D32");
  cp4.appendChild(cp4sub);

  createBullets([
    "19 retirements (zero domain logic, boilerplate stubs)",
    "28 merge shims (import-alias, no ClassDef)",
    "6 canonical executors created:",
    "  HOPPipelineExecutor — 9 HOP stages (apps_lic)",
    "  RGValidationExecutor — 4 validators (apps_rg)",
    "  LICValidationExecutor — 2 validators (apps_lic)",
    "  ObservabilityProbeExecutor — 6 agents (L6)",
    "  RGStrategyExecutor — 3 strategies (apps_rg)",
    "  InspectorExecutor — 3 inspectors (L5)",
    "",
    "-4339 LOC | -41 discovery nodes",
    "62/62 consolidation tests pass",
    "Audit: 7 phases all PASS (A-G)"
  ], 12, 50, 9, "#1B5E20").forEach(n => cp4.appendChild(n));

  // --- CP Card 5: Dependency Governance ---
  const cp5 = createCard(2484, 1210, 580, 400, "#B8D8F8", "#5A9BD5", "CP5-DependencyGovernance");
  master.appendChild(cp5);

  const cp5t = createText("DEPENDENCY GOVERNANCE", 12, 8, 13, true, "#002B55");
  cp5.appendChild(cp5t);
  const cp5sub = createText("57 dist packages | 4 buckets", 12, 28, 10, true, "#0D47A1");
  cp5.appendChild(cp5sub);

  createBullets([
    "core (19): pydantic, numpy, redis, networkx, libcst...",
    "dev (1): pytest",
    "infra (34): openai, anthropic, fastapi, dash, boto3...",
    "sdks (3): provider-specific SDKs",
    "phantom/stale (17): refs to removed modules",
    "",
    "Shipping contract excludes:",
    "  tests/ | ops_scripts/ | data/",
    "  */scripts/ | */dashboards/",
    "",
    "Import allowlist: 7 stdlib modules in _constants.py",
    "Allowlist hash locked in SHA-256",
    "Immutable: frozenset + MappingProxyType (deep)"
  ], 12, 50, 9, "#002B55").forEach(n => cp5.appendChild(n));

  // ===========================================================
  // BOTTOM STRIP: ARTIFACT TAXONOMY
  // ===========================================================
  const strip = createCard(40, 1660, 3120, 180, "#F5F5F5", "#CCCCCC", "ObservabilityStrip");
  master.appendChild(strip);

  const stripTitle = createText("ENFORCEABLE ARTIFACT TAXONOMY", 16, 8, 13, true, "#333333");
  strip.appendChild(stripTitle);

  // Left: Classic artifacts
  createBullets([
    "RESULT (result.json) — Main Flow",
    "AGGREGATE (aggregate.json) — Conditional Flow",
    "INCIDENT (incident.json) — Incident Telemetry",
    "HEALING_PLAN (healing_plan.json) — Healing Plan"
  ], 16, 34, 10, "#333333").forEach(n => strip.appendChild(n));

  // Center: Routing
  createBullets([
    "APPROVED REMEDIATION POINTER",
    "  (Deterministic Trigger)",
    "METRICS DASHBOARD ↔ AUDIT LOG"
  ], 800, 34, 10, "#333333").forEach(n => strip.appendChild(n));

  // Right: New enforcement artifacts
  const newArtTitle = createText("NEW ENFORCEMENT ARTIFACTS:", 1600, 34, 11, true, "#8B0000");
  strip.appendChild(newArtTitle);

  createBullets([
    "enforcement_report.json — Machine-readable enforcement",
    "blueprint_integrity.sha256 — SHA-256 hash lock (20 files)",
    "guardian_{id}.json — Guardian results (L6 ingestible)",
    "phantom_baseline.json — Phantom debt register",
    "agent_discovery_full.json — Agent registry SSOT (149)"
  ], 1600, 54, 9, "#8B0000").forEach(n => strip.appendChild(n));

  // ===========================================================
  // FLOW ARROWS (main layer connections)
  // ===========================================================

  // L4 → L1: Context retrieval
  createArrowWithLabel(1160, 170, 1700, 170, "Context retrieval request", "#5A9BD5", true)
    .forEach(n => master.appendChild(n));

  // KG → L4: Advisory
  createArrowWithLabel(540, 120, 580, 120, "Advisory only", "#7F8C8D", true)
    .forEach(n => master.appendChild(n));

  // L6 → L0: Signal correlation
  createArrowWithLabel(260, 670, 260, 710, "Signal Correlation", "#8B5DAA", false)
    .forEach(n => master.appendChild(n));

  // L0 → L5: Route to governance
  createArrowWithLabel(460, 780, 500, 660, "Route to governance", "#2C3E50", false)
    .forEach(n => master.appendChild(n));

  // L5 → L3: Escalate → HIL
  createArrowWithLabel(1020, 600, 1060, 600, "Escalate → HIL", "#E6A030", false)
    .forEach(n => master.appendChild(n));

  // L5 → L2 (AUTO-PASS bypass)
  createArrowWithLabel(1020, 500, 1400, 500, "AUTO-PASS", "#4CAF50", false)
    .forEach(n => master.appendChild(n));

  // L3 → L2: Approved decision
  createArrowWithLabel(1360, 620, 1400, 620, "Approved Decision", "#E6A030", false)
    .forEach(n => master.appendChild(n));

  // L5 → bottom: Emit AGGREGATE
  createArrowWithLabel(760, 880, 760, 920, "Emit AGGREGATE artifact", "#E67E22", true)
    .forEach(n => master.appendChild(n));

  // Control Plane → L5: Enforcement
  createArrowWithLabel(760, 1140, 760, 880, "Structural enforcement", "#CD5C5C", true)
    .forEach(n => master.appendChild(n));

  // Control Plane → L0: Classification kernel
  createArrowWithLabel(358, 1140, 260, 1090, "Classification kernel → discovery", "#66BB6A", true)
    .forEach(n => master.appendChild(n));

  // Control Plane → L2: Canonical executors
  createArrowWithLabel(1610, 1140, 1610, 820, "Canonical executors", "#66BB6A", true)
    .forEach(n => master.appendChild(n));

  // ===========================================================
  // APPROVED REMEDIATION POINTER
  // ===========================================================
  const arp = createCard(780, 930, 400, 50, "#FFD699", "#E6A030", "ApprovedRemediationPointer");
  master.appendChild(arp);
  const arpText = createText("APPROVED REMEDIATION POINTER (Deterministic Trigger)", 12, 14, 10, true, "#4A2800");
  arp.appendChild(arpText);

  // L0 bottom route → ARP
  createArrowWithLabel(460, 960, 780, 960, "L0 routing", "#2C3E50", false)
    .forEach(n => master.appendChild(n));

  // ARP → Emit RESULT
  const emitR2 = createText("→ Emit RESULT", 1190, 942, 11, true, "#2C3E50");
  master.appendChild(emitR2);

  // ===========================================================
  // METRICS DASHBOARD + AUDIT LOG
  // ===========================================================
  const mdBox = createCard(500, 1020, 200, 50, "#E8E8E8", "#999999", "MetricsDashboard");
  master.appendChild(mdBox);
  const mdText = createText("METRICS DASHBOARD", 16, 14, 10, true, "#333333");
  mdBox.appendChild(mdText);

  const alBox = createCard(720, 1020, 160, 50, "#E8E8E8", "#999999", "AuditLog");
  master.appendChild(alBox);
  const alText = createText("AUDIT LOG", 16, 14, 10, true, "#333333");
  alBox.appendChild(alText);

  // Telemetry arrows from L6 area
  createArrowWithLabel(260, 670, 500, 1040, "Emit telemetry.event", "#C0392B", true)
    .forEach(n => master.appendChild(n));

  // ===========================================================
  // DONE
  // ===========================================================

  figma.viewport.scrollAndZoomIntoView([master]);
  figma.notify("Agentic Control Flow v2 created! 🎉");
  figma.closePlugin();
}

main();
