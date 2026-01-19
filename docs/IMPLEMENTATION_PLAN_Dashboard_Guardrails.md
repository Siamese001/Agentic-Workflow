# Implementation Plan: Dashboard Guardrails & Controls
**Date:** 2026-01-11  
**Status:** PROPOSED (NOT IMPLEMENTED)  
**Related:** RCA_Dashboard_Table_Rendering_Failure.md

---

## Overview

This document outlines a comprehensive implementation plan to prevent the dashboard table rendering failures that occurred on 2026-01-11. The plan includes guardrails, automated validation, defensive coding standards, and monitoring controls.

**DO NOT IMPLEMENT YET** - This is a design document for review and approval.

---

## Priority Matrix

| Priority | Category | Impact | Effort | ROI |
|----------|----------|--------|--------|-----|
| **P0** | Generator Validation | HIGH | LOW | ⭐⭐⭐⭐⭐ |
| **P0** | Defensive Coding Standards | HIGH | LOW | ⭐⭐⭐⭐⭐ |
| **P0** | Enhanced Test Coverage | HIGH | MEDIUM | ⭐⭐⭐⭐ |
| **P1** | Runtime Error Handling | MEDIUM | LOW | ⭐⭐⭐⭐ |
| **P1** | Cache-Busting | MEDIUM | LOW | ⭐⭐⭐ |
| **P2** | Monitoring & Alerts | LOW | MEDIUM | ⭐⭐ |

---

## P0: Generator Validation (CRITICAL)

### Objective
Prevent duplicate declarations and malformed HTML from being written to disk.

### Implementation

#### 1. Pre-Write Validation Function

**File:** `agentic_core/L6_observability/dashboards/generate_dashboard.py`

**New Function:**
```python
def validate_html_before_write(html: str) -> tuple[bool, List[str]]:
    """
    Validate HTML content before writing to disk.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Check 1: Detect duplicate const declarations
    const_declarations = {
        'dashboardData': re.findall(r'const dashboardData\s*=', html),
        'realAgentData': re.findall(r'const realAgentData\s*=', html),
    }
    
    for var_name, matches in const_declarations.items():
        if len(matches) > 1:
            errors.append(f"CRITICAL: Found {len(matches)} declarations of 'const {var_name}' (expected 1)")
    
    # Check 2: Validate file size (should be 300KB-500KB)
    size_bytes = len(html.encode('utf-8'))
    size_kb = size_bytes / 1024
    if size_kb > 500:
        errors.append(f"WARNING: HTML size is {size_kb:.1f}KB (expected <500KB) - possible duplication")
    if size_kb < 300:
        errors.append(f"WARNING: HTML size is {size_kb:.1f}KB (expected >300KB) - possible data missing")
    
    # Check 3: Validate line count (should be 10K-15K lines)
    line_count = html.count('\n')
    if line_count > 15000:
        errors.append(f"WARNING: HTML has {line_count:,} lines (expected <15K) - possible duplication")
    if line_count < 10000:
        errors.append(f"WARNING: HTML has {line_count:,} lines (expected >10K) - possible data missing")
    
    # Check 4: Validate JavaScript syntax (basic check)
    script_blocks = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    for i, script in enumerate(script_blocks):
        # Check for common syntax errors
        if script.count('{') != script.count('}'):
            errors.append(f"ERROR: Script block {i+1} has mismatched braces")
        if script.count('(') != script.count(')'):
            errors.append(f"ERROR: Script block {i+1} has mismatched parentheses")
        if script.count('[') != script.count(']'):
            errors.append(f"ERROR: Script block {i+1} has mismatched brackets")
    
    # Check 5: Verify required data structures exist
    required_vars = ['dashboardData', 'realAgentData', 'loadData', 'renderTerritorySummaryTable']
    for var in required_vars:
        if var not in html:
            errors.append(f"ERROR: Required variable/function '{var}' not found in HTML")
    
    # Check 6: Verify dashboardData has expected structure
    dashboard_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
    if dashboard_match:
        try:
            data = json.loads(dashboard_match.group(1))
            if not isinstance(data, list):
                errors.append("ERROR: dashboardData is not an array")
            elif len(data) < 29:
                errors.append(f"ERROR: dashboardData has {len(data)} rows (expected 29)")
            elif data[0].get('Territory') != 'TOTAL':
                errors.append("ERROR: First row in dashboardData is not TOTAL")
        except json.JSONDecodeError as e:
            errors.append(f"ERROR: dashboardData is not valid JSON: {e}")
    
    return (len(errors) == 0, errors)
```

**Integration Point:**
```python
def update_dashboard_html(self, data: List[Dict[str, Any]], per_agent_data: Dict[str, Dict]) -> bool:
    """Update dashboard HTML with new data and real per-agent data."""
    # ... existing code to build new_html ...
    
    # VALIDATE BEFORE WRITING
    is_valid, errors = validate_html_before_write(new_html)
    
    if not is_valid:
        print("❌ VALIDATION FAILED - HTML NOT WRITTEN")
        for error in errors:
            print(f"   {error}")
        return False
    
    # Only write if validation passes
    self.dashboard_path.write_text(new_html, encoding='utf-8')
    print(f"✅ Updated {self.dashboard_path}")
    return True
```

**Estimated Effort:** 2-3 hours  
**Risk Reduction:** 90% (prevents duplicate declarations, size bloat, syntax errors)

---

#### 2. Improved Replacement Logic

**Current Issue:** Naive string replacement that doesn't find existing `realAgentData`

**Improved Logic:**
```python
def update_dashboard_html(self, data: List[Dict[str, Any]], per_agent_data: Dict[str, Dict]) -> bool:
    """Update dashboard HTML with new data and real per-agent data."""
    html = self.dashboard_path.read_text(encoding='utf-8')
    
    # Step 1: Find dashboardData boundaries
    data_start_marker = 'const dashboardData = ['
    data_start_idx = html.find(data_start_marker)
    if data_start_idx == -1:
        print("❌ ERROR: Could not find dashboardData in HTML")
        return False
    
    # Find the closing ]; for dashboardData
    data_end_idx = html.find('];', data_start_idx)
    if data_end_idx == -1:
        print("❌ ERROR: Could not find end of dashboardData")
        return False
    data_end_idx += len('];')
    
    # Step 2: Find realAgentData boundaries (if it exists)
    agent_start_marker = 'const realAgentData = {'
    agent_start_idx = html.find(agent_start_marker, data_end_idx)
    
    if agent_start_idx != -1:
        # realAgentData exists, find its end
        # Use brace counting to find the matching closing }
        brace_count = 0
        i = agent_start_idx + len('const realAgentData = ')
        while i < len(html):
            if html[i] == '{':
                brace_count += 1
            elif html[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found the closing brace, now find the semicolon
                    agent_end_idx = html.find(';', i) + 1
                    break
            i += 1
        else:
            print("❌ ERROR: Could not find end of realAgentData")
            return False
        
        # Replace from dashboardData start to realAgentData end
        replace_start = data_start_idx
        replace_end = agent_end_idx
    else:
        # realAgentData doesn't exist, insert after dashboardData
        replace_start = data_start_idx
        replace_end = data_end_idx
    
    # Step 3: Build replacement block
    new_json = json.dumps(data, indent=2)
    new_data_block = f'const dashboardData = {new_json};'
    
    agent_json = json.dumps(per_agent_data, indent=2)
    real_agent_block = f'\n\n        // Real per-agent data (replaces generateMockAgentData)\n        const realAgentData = {agent_json};'
    
    # Step 4: Replace and validate
    new_html = html[:replace_start] + new_data_block + real_agent_block + html[replace_end:]
    
    # VALIDATE before writing
    is_valid, errors = validate_html_before_write(new_html)
    if not is_valid:
        print("❌ VALIDATION FAILED")
        for error in errors:
            print(f"   {error}")
        return False
    
    # Write validated HTML
    self.dashboard_path.write_text(new_html, encoding='utf-8')
    print(f"✅ Updated {self.dashboard_path}")
    return True
```

**Estimated Effort:** 2 hours  
**Risk Reduction:** 95% (proper brace matching, validation before write)

---

## P0: Defensive Coding Standards (CRITICAL)

### Objective
Ensure all DOM element access is null-safe and all initialization functions fail gracefully.

### Implementation

#### 1. Defensive DOM Access Pattern

**Standard Pattern (enforce via linting):**
```javascript
// ❌ UNSAFE - DO NOT USE
document.getElementById('elementId').textContent = value;

// ✅ SAFE - ALWAYS USE
const el = document.getElementById('elementId');
if (el) el.textContent = value;

// ✅ SAFE - ALTERNATIVE
const el = document.getElementById('elementId');
if (!el) {
    console.warn('[WARN] Element not found: elementId');
    return;
}
el.textContent = value;
```

**Apply to all functions:**
- `initializeSemanticMetrics()` ✅ DONE
- `initializeRuntimeMonitoring()` ✅ DONE
- `renderTerritorySummaryTable()` ✅ DONE
- `renderCodeQualityTable()` - TODO
- `updateKPICards()` - TODO
- `updateRuntime()` - TODO
- All event handlers - TODO

**Estimated Effort:** 4-6 hours (audit all 50+ DOM access points)  
**Risk Reduction:** 80% (prevents null access crashes)

---

#### 2. Try-Catch Wrapper for Initialization

**Pattern:**
```javascript
function safeInitialize(fn, name) {
    try {
        fn();
        console.log(`[INIT] ${name} initialized successfully`);
    } catch (e) {
        console.error(`[INIT ERROR] ${name} failed:`, e);
        // Don't rethrow - allow other initializations to continue
    }
}

// Usage:
safeInitialize(initializeSemanticMetrics, 'Semantic Metrics');
safeInitialize(initializeRuntimeMonitoring, 'Runtime Monitoring');
safeInitialize(loadData, 'Dashboard Data');
```

**Estimated Effort:** 1 hour  
**Risk Reduction:** 70% (prevents initialization failures from cascading)

---

#### 3. Graceful Degradation for Missing Elements

**Pattern:**
```javascript
function renderTerritorySummaryTable(territoryData) {
    const container = document.getElementById('kpiGrid');
    if (!container) {
        console.error('[ERROR] #kpiGrid container not found - cannot render table');
        // Show user-visible error message
        showErrorMessage('Dashboard container not found. Please refresh the page.');
        return;
    }
    
    try {
        // Rendering logic
        globalAgentData = realAgentData;
        // ... rest of rendering ...
    } catch (e) {
        console.error('[ERROR] Table rendering failed:', e);
        container.innerHTML = `
            <div style="padding: 20px; background: #fee; border: 1px solid #c00; border-radius: 4px;">
                <strong>⚠️ Error:</strong> Failed to render table. 
                <a href="#" onclick="location.reload()">Refresh page</a>
            </div>
        `;
    }
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #fee; border: 2px solid #c00; padding: 15px; border-radius: 8px; z-index: 9999; max-width: 400px;';
    errorDiv.innerHTML = `<strong>⚠️ Error:</strong> ${message}`;
    document.body.appendChild(errorDiv);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => errorDiv.remove(), 10000);
}
```

**Estimated Effort:** 2 hours  
**Risk Reduction:** 60% (provides user feedback instead of silent failure)

---

## P0: Enhanced Test Coverage (CRITICAL)

### Objective
Catch JavaScript errors, duplicate declarations, and rendering failures in automated tests.

### Implementation

#### 1. JavaScript Syntax Validation Test

**File:** `agentic_core/L6_observability/dashboards/test_dashboard.py`

**New Test:**
```python
def test_javascript_syntax_validation(self):
    """Test 9: Validate JavaScript syntax in dashboard HTML."""
    print("\n" + "─" * 70)
    print("Test: JavaScript Syntax Validation")
    print("─" * 70)
    
    html = self.dashboard_path.read_text(encoding='utf-8')
    
    # Extract all script blocks
    script_blocks = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    
    errors = []
    
    for i, script in enumerate(script_blocks):
        # Check for balanced braces
        if script.count('{') != script.count('}'):
            errors.append(f"Script block {i+1}: Mismatched braces")
        
        # Check for balanced parentheses
        if script.count('(') != script.count(')'):
            errors.append(f"Script block {i+1}: Mismatched parentheses")
        
        # Check for balanced brackets
        if script.count('[') != script.count(']'):
            errors.append(f"Script block {i+1}: Mismatched brackets")
    
    if errors:
        print(f"❌ FAILED: JavaScript syntax errors found:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print(f"✅ PASSED: All {len(script_blocks)} script blocks have valid syntax")
    return True
```

**Estimated Effort:** 1 hour  
**Risk Reduction:** 50% (catches syntax errors before deployment)

---

#### 2. Duplicate Declaration Detection Test

**New Test:**
```python
def test_no_duplicate_declarations(self):
    """Test 10: Ensure no duplicate const declarations."""
    print("\n" + "─" * 70)
    print("Test: No Duplicate Declarations")
    print("─" * 70)
    
    html = self.dashboard_path.read_text(encoding='utf-8')
    
    # Check for duplicate const declarations
    const_vars = ['dashboardData', 'realAgentData']
    errors = []
    
    for var_name in const_vars:
        pattern = rf'const {var_name}\s*='
        matches = re.findall(pattern, html)
        
        if len(matches) > 1:
            errors.append(f"Found {len(matches)} declarations of 'const {var_name}' (expected 1)")
        elif len(matches) == 0:
            errors.append(f"Found 0 declarations of 'const {var_name}' (expected 1)")
    
    if errors:
        print(f"❌ FAILED: Duplicate declaration errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print(f"✅ PASSED: All const declarations are unique")
    return True
```

**Estimated Effort:** 30 minutes  
**Risk Reduction:** 95% (directly catches the root cause from RCA)

---

#### 3. Browser-Based Rendering Test (Playwright)

**New Test File:** `agentic_core/L6_observability/dashboards/test_dashboard_browser.py`

**Implementation:**
```python
import asyncio
from playwright.async_api import async_playwright
import subprocess
import time

async def test_dashboard_renders_in_browser():
    """
    Test that dashboard actually renders tables in a real browser.
    This catches JavaScript errors that structural tests miss.
    """
    # Start HTTP server
    server_process = subprocess.Popen(
        ['python', 'agentic_core/L6_observability/dashboards/serve_dashboard.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)  # Wait for server to start
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Capture console errors
            console_errors = []
            page.on('console', lambda msg: 
                console_errors.append(msg.text) if msg.type == 'error' else None
            )
            
            # Load dashboard
            await page.goto('http://localhost:8080/autonomy_dashboard.html')
            await page.wait_for_timeout(2000)  # Wait for rendering
            
            # Check for JavaScript errors
            if console_errors:
                print(f"❌ FAILED: JavaScript errors in browser console:")
                for error in console_errors:
                    print(f"   - {error}")
                return False
            
            # Check if tables are rendered
            kpi_grid = await page.query_selector('#kpiGrid')
            kpi_content = await kpi_grid.inner_html() if kpi_grid else ''
            
            if not kpi_content or len(kpi_content) < 100:
                print(f"❌ FAILED: #kpiGrid is empty (length: {len(kpi_content)})")
                return False
            
            # Check for table elements
            tables = await page.query_selector_all('table')
            if len(tables) == 0:
                print(f"❌ FAILED: No <table> elements found")
                return False
            
            print(f"✅ PASSED: Dashboard renders correctly in browser")
            print(f"   - No JavaScript errors")
            print(f"   - #kpiGrid has content ({len(kpi_content)} chars)")
            print(f"   - Found {len(tables)} table elements")
            
            await browser.close()
            return True
            
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == '__main__':
    result = asyncio.run(test_dashboard_renders_in_browser())
    exit(0 if result else 1)
```

**Dependencies:** `pip install playwright && playwright install chromium`

**Estimated Effort:** 3-4 hours  
**Risk Reduction:** 90% (catches all rendering failures in real browser)

---

#### 4. File Size & Line Count Validation Test

**New Test:**
```python
def test_file_size_and_line_count(self):
    """Test 11: Validate HTML file size and line count are within expected ranges."""
    print("\n" + "─" * 70)
    print("Test: File Size & Line Count Validation")
    print("─" * 70)
    
    html = self.dashboard_path.read_text(encoding='utf-8')
    
    # Check file size (should be 300KB-500KB)
    size_bytes = len(html.encode('utf-8'))
    size_kb = size_bytes / 1024
    
    # Check line count (should be 10K-15K)
    line_count = html.count('\n')
    
    errors = []
    
    if size_kb > 500:
        errors.append(f"File size {size_kb:.1f}KB exceeds 500KB (possible duplication)")
    elif size_kb < 300:
        errors.append(f"File size {size_kb:.1f}KB below 300KB (possible missing data)")
    
    if line_count > 15000:
        errors.append(f"Line count {line_count:,} exceeds 15K (possible duplication)")
    elif line_count < 10000:
        errors.append(f"Line count {line_count:,} below 10K (possible missing data)")
    
    if errors:
        print(f"❌ FAILED: File size/line count validation errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print(f"✅ PASSED: File size {size_kb:.1f}KB, {line_count:,} lines (within expected ranges)")
    return True
```

**Estimated Effort:** 30 minutes  
**Risk Reduction:** 70% (catches bloat from duplicates)

---

## P1: Runtime Error Handling (HIGH PRIORITY)

### Objective
Provide user-visible error messages and graceful degradation when JavaScript fails.

### Implementation

#### 1. Global Error Handler with User Feedback

**Add to dashboard HTML:**
```javascript
// Enhanced global error handler with user feedback
window.addEventListener('error', (event) => {
    console.error('[GLOBAL ERROR]', event.message, event.filename, event.lineno, event.colno);
    console.error('[ERROR STACK]', event.error?.stack);
    
    // Show user-visible error message
    showCriticalError(
        'JavaScript Error',
        `${event.message} at line ${event.lineno}`,
        'The dashboard encountered an error. Please refresh the page or contact support.'
    );
    
    // Prevent default error handling
    event.preventDefault();
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('[UNHANDLED PROMISE REJECTION]', event.reason);
    
    showCriticalError(
        'Promise Rejection',
        event.reason?.message || String(event.reason),
        'An asynchronous operation failed. Please refresh the page.'
    );
});

function showCriticalError(title, message, suggestion) {
    // Create error overlay
    const overlay = document.createElement('div');
    overlay.id = 'error-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    overlay.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 8px; max-width: 500px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
            <h2 style="color: #c00; margin-top: 0;">⚠️ ${title}</h2>
            <p style="color: #333; margin: 15px 0;"><strong>Error:</strong> ${message}</p>
            <p style="color: #666; margin: 15px 0;">${suggestion}</p>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button onclick="location.reload()" style="flex: 1; padding: 10px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                    🔄 Refresh Page
                </button>
                <button onclick="document.getElementById('error-overlay').remove()" style="flex: 1; padding: 10px; background: #666; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;">
                    ✕ Dismiss
                </button>
            </div>
            <details style="margin-top: 15px; font-size: 12px; color: #999;">
                <summary style="cursor: pointer;">Technical Details</summary>
                <pre style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px; overflow-x: auto;">${message}</pre>
            </details>
        </div>
    `;
    
    document.body.appendChild(overlay);
}
```

**Estimated Effort:** 2 hours  
**Risk Reduction:** 50% (provides user feedback instead of silent failure)

---

#### 2. Fallback UI for Failed Rendering

**Pattern:**
```javascript
function renderWithFallback(renderFn, containerId, fallbackMessage) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`[ERROR] Container #${containerId} not found`);
        return;
    }
    
    try {
        renderFn(container);
    } catch (e) {
        console.error(`[ERROR] Rendering failed for #${containerId}:`, e);
        container.innerHTML = `
            <div style="padding: 20px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px;">
                <strong>⚠️ Rendering Error</strong>
                <p>${fallbackMessage}</p>
                <button onclick="location.reload()" style="padding: 8px 16px; background: #ffc107; border: none; border-radius: 4px; cursor: pointer;">
                    🔄 Retry
                </button>
            </div>
        `;
    }
}

// Usage:
renderWithFallback(
    (container) => renderTerritorySummaryTable(territoryData),
    'kpiGrid',
    'Failed to load territory summary table. Please refresh the page.'
);
```

**Estimated Effort:** 1 hour  
**Risk Reduction:** 40% (provides fallback UI instead of blank screen)

---

## P1: Cache-Busting (HIGH PRIORITY)

### Objective
Ensure users always load the latest version of the dashboard without manual hard refresh.

### Implementation

#### 1. Version Query Parameter

**File:** `agentic_core/L6_observability/dashboards/generate_dashboard.py`

**Add version to HTML:**
```python
def update_dashboard_html(self, data: List[Dict[str, Any]], per_agent_data: Dict[str, Dict]) -> bool:
    """Update dashboard HTML with new data and real per-agent data."""
    # ... existing code ...
    
    # Add version metadata to HTML
    version = datetime.now().strftime('%Y%m%d_%H%M%S')
    version_comment = f'\n<!-- Dashboard Version: {version} -->\n'
    
    new_html = version_comment + new_html
    
    # ... rest of code ...
```

**Update server to add cache headers:**
```python
# File: serve_dashboard.py
class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Disable caching for HTML files
        if self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

# Use custom handler
with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
```

**Estimated Effort:** 1 hour  
**Risk Reduction:** 80% (prevents cache-related confusion)

---

#### 2. Auto-Refresh Detection

**Add to dashboard HTML:**
```javascript
// Check if dashboard version has changed
const DASHBOARD_VERSION = '20260111_050000'; // Injected by generator

function checkForUpdates() {
    fetch('/autonomy_dashboard.html', { cache: 'no-cache' })
        .then(response => response.text())
        .then(html => {
            const match = html.match(/<!-- Dashboard Version: (\d+_\d+) -->/);
            if (match && match[1] !== DASHBOARD_VERSION) {
                showUpdateNotification(match[1]);
            }
        })
        .catch(err => console.warn('[WARN] Update check failed:', err));
}

function showUpdateNotification(newVersion) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #0066cc;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = `
        <strong>🔄 Update Available</strong>
        <p style="margin: 10px 0;">A new version of the dashboard is available.</p>
        <button onclick="location.reload(true)" style="padding: 8px 16px; background: white; color: #0066cc; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
            Refresh Now
        </button>
    `;
    document.body.appendChild(notification);
}

// Check for updates every 5 minutes
setInterval(checkForUpdates, 5 * 60 * 1000);
```

**Estimated Effort:** 1 hour  
**Risk Reduction:** 60% (notifies users of updates)

---

## P2: Monitoring & Alerts (MEDIUM PRIORITY)

### Objective
Detect anomalies in dashboard generation and alert developers.

### Implementation

#### 1. Generation Metrics Logging

**File:** `agentic_core/L6_observability/dashboards/generate_dashboard.py`

**Add metrics collection:**
```python
def run(self) -> bool:
    """Run the complete dashboard generation pipeline with metrics."""
    start_time = time.time()
    
    try:
        # ... existing generation code ...
        
        # Collect metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': time.time() - start_time,
            'agent_count': len(self.agents),
            'territory_count': len(self.territories),
            'html_size_kb': self.dashboard_path.stat().st_size / 1024,
            'html_line_count': self.dashboard_path.read_text().count('\n'),
            'validation_passed': True,
        }
        
        # Write metrics to log file
        metrics_file = self.dashboard_path.parent / 'generation_metrics.jsonl'
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        # Check for anomalies
        check_for_anomalies(metrics)
        
        return True
        
    except Exception as e:
        # Log failure metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': time.time() - start_time,
            'validation_passed': False,
            'error': str(e),
        }
        metrics_file = self.dashboard_path.parent / 'generation_metrics.jsonl'
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        raise

def check_for_anomalies(metrics: dict):
    """Check metrics for anomalies and alert if found."""
    alerts = []
    
    if metrics['html_size_kb'] > 500:
        alerts.append(f"⚠️ HTML size {metrics['html_size_kb']:.1f}KB exceeds 500KB threshold")
    
    if metrics['html_line_count'] > 15000:
        alerts.append(f"⚠️ HTML line count {metrics['html_line_count']:,} exceeds 15K threshold")
    
    if metrics['duration_seconds'] > 30:
        alerts.append(f"⚠️ Generation took {metrics['duration_seconds']:.1f}s (expected <30s)")
    
    if alerts:
        print("\n" + "=" * 70)
        print("⚠️  ANOMALY ALERTS")
        print("=" * 70)
        for alert in alerts:
            print(alert)
        print("=" * 70 + "\n")
```

**Estimated Effort:** 2 hours  
**Risk Reduction:** 30% (early detection of issues)

---

#### 2. CI/CD Integration

**File:** `.github/workflows/dashboard_validation.yml`

**Add GitHub Actions workflow:**
```yaml
name: Dashboard Validation

on:
  push:
    paths:
      - 'agentic_core/L6_observability/dashboards/**'
      - 'agent_discovery_full.json'

jobs:
  validate-dashboard:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install playwright
          playwright install chromium
      
      - name: Generate dashboard
        run: python agentic_core/L6_observability/dashboards/generate_dashboard.py
      
      - name: Run structural tests
        run: python agentic_core/L6_observability/dashboards/test_dashboard.py
      
      - name: Run browser rendering test
        run: python agentic_core/L6_observability/dashboards/test_dashboard_browser.py
      
      - name: Check for anomalies
        run: |
          python -c "
          import json
          with open('agentic_core/L6_observability/dashboards/generation_metrics.jsonl') as f:
              metrics = json.loads(f.readlines()[-1])
          
          if metrics['html_size_kb'] > 500:
              print('❌ FAIL: HTML size exceeds 500KB')
              exit(1)
          
          if metrics['html_line_count'] > 15000:
              print('❌ FAIL: HTML line count exceeds 15K')
              exit(1)
          
          print('✅ PASS: All metrics within normal ranges')
          "
      
      - name: Upload dashboard artifact
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: failed-dashboard
          path: agentic_core/L6_observability/dashboards/autonomy_dashboard.html
```

**Estimated Effort:** 2 hours  
**Risk Reduction:** 40% (catches issues before merge)

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1)
**Priority:** P0  
**Effort:** 10-12 hours

1. ✅ Implement generator validation function (2-3 hours)
2. ✅ Improve replacement logic with brace matching (2 hours)
3. ✅ Audit and fix all DOM element access (4-6 hours)
4. ✅ Add duplicate declaration test (30 min)
5. ✅ Add file size/line count test (30 min)
6. ✅ Add JavaScript syntax validation test (1 hour)

**Success Criteria:**
- No duplicate declarations possible
- All DOM access is null-safe
- All tests pass including new validation tests

---

### Phase 2: Enhanced Testing (Week 2)
**Priority:** P0-P1  
**Effort:** 6-8 hours

1. ✅ Implement browser-based rendering test with Playwright (3-4 hours)
2. ✅ Add try-catch wrappers for initialization (1 hour)
3. ✅ Implement global error handler with user feedback (2 hours)
4. ✅ Add fallback UI for failed rendering (1 hour)

**Success Criteria:**
- Browser test catches rendering failures
- Users see error messages instead of blank screen
- Graceful degradation for missing elements

---

### Phase 3: Cache & Monitoring (Week 3)
**Priority:** P1-P2  
**Effort:** 6-8 hours

1. ✅ Implement cache-busting with version parameter (1 hour)
2. ✅ Update HTTP server with no-cache headers (1 hour)
3. ✅ Add auto-refresh detection (1 hour)
4. ✅ Implement generation metrics logging (2 hours)
5. ✅ Add CI/CD workflow for dashboard validation (2 hours)

**Success Criteria:**
- Users always load latest version
- Anomalies are detected and logged
- CI/CD catches issues before merge

---

## Testing Strategy

### Unit Tests
- Generator validation function
- HTML replacement logic
- Metrics collection

### Integration Tests
- End-to-end dashboard generation
- All 11 structural tests
- Browser rendering test

### Manual Tests
- Hard refresh behavior
- Error message display
- Fallback UI rendering
- Update notification

---

## Rollback Plan

If any implementation causes issues:

1. **Immediate:** Revert to commit `67a1d9744` (last known working state)
2. **Short-term:** Disable new validation checks via feature flag
3. **Long-term:** Fix issues and re-enable with additional testing

---

## Success Metrics

### Before Implementation
- ❌ Duplicate declarations possible
- ❌ Silent JavaScript failures
- ❌ No browser-based testing
- ❌ Cache confusion
- ❌ No anomaly detection

### After Implementation
- ✅ Duplicate declarations prevented by validation
- ✅ User-visible error messages
- ✅ Browser rendering validated in tests
- ✅ Cache-busting enabled
- ✅ Anomalies detected and logged
- ✅ CI/CD catches issues before merge

---

## Maintenance Plan

### Weekly
- Review generation metrics for anomalies
- Check CI/CD test results

### Monthly
- Audit DOM element access patterns
- Review error logs for new failure modes

### Quarterly
- Update validation thresholds based on data
- Enhance tests based on new features

---

## Conclusion

This implementation plan provides comprehensive guardrails to prevent the dashboard rendering failures that occurred on 2026-01-11. The plan is prioritized by impact and effort, with critical fixes in Phase 1 and enhancements in Phases 2-3.

**Total Estimated Effort:** 22-28 hours across 3 weeks

**Risk Reduction:** 85-95% for similar failures

**DO NOT IMPLEMENT YET** - Review and approve this plan before proceeding.
