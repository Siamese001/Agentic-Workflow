# Dashboard Modularization Implementation Plan

**Document Version:** 1.0  
**Created:** 2026-01-15  
**Target File:** `c:\Git\Agentic-Workflow\agentic_core\L6_observability\dashboards\autonomy_dashboard.html`  
**Current Size:** 598KB (15,395 lines)  
**Target Architecture:** Modular, maintainable, testable components

---

## Executive Summary

The autonomy dashboard has grown to 598KB with embedded data, styles, and JavaScript in a single monolithic HTML file. This plan outlines a **6-phase modularization** strategy to decompose the dashboard into maintainable, testable modules while preserving all functionality and ensuring backward compatibility.

### Key Metrics
- **Current State:** 1 file, 598KB, ~15,395 lines
- **Target State:** ~15 files, modular architecture
- **Estimated Effort:** 40-60 hours across 6 phases
- **Risk Level:** Medium (requires careful data flow management)

---

## Architecture Analysis

### Current Structure
```
autonomy_dashboard.html (598KB)
├── HTML Structure (500 lines)
├── CSS Styles (450 lines)
├── Embedded Data (12,000+ lines)
│   ├── dashboardData array
│   ├── realAgentData object
│   ├── recommendationsData array
│   └── strategicObservationsData object
└── JavaScript (2,500+ lines)
    ├── Utility functions (500 lines)
    ├── Rendering functions (1,200 lines)
    ├── Data processing (400 lines)
    ├── Event handlers (200 lines)
    └── API/polling logic (200 lines)
```

### Target Architecture
```
dashboards/
├── autonomy_dashboard.html (core structure, 200 lines)
├── css/
│   ├── variables.css (color scheme, spacing)
│   ├── layout.css (grid, containers, responsive)
│   ├── components.css (KPI boxes, cards, tables)
│   └── charts.css (Plotly customizations)
├── js/
│   ├── config.js (constants, thresholds)
│   ├── utils/
│   │   ├── color-utils.js (getColor, thresholds)
│   │   ├── math-utils.js (stats, distributions)
│   │   ├── format-utils.js (formatters, badges)
│   │   └── random-utils.js (seeded PRNG)
│   ├── data/
│   │   ├── data-loader.js (fetch/load data)
│   │   └── data-processor.js (aggregations, filters)
│   ├── renderers/
│   │   ├── table-renderer.js (territory & quality tables)
│   │   ├── chart-renderer.js (Plotly charts)
│   │   ├── kpi-renderer.js (KPI boxes)
│   │   └── modal-renderer.js (drill-down modals)
│   ├── controllers/
│   │   ├── tab-controller.js (tab switching)
│   │   ├── filter-controller.js (table filters)
│   │   └── refresh-controller.js (auto-refresh)
│   └── main.js (initialization, orchestration)
└── data/
    ├── dashboard_data.json (territory metrics)
    ├── agent_data.json (per-agent distributions)
    ├── recommendations.json (prioritized actions)
    └── observations.json (strategic insights)
```

---

## Phase 1: Extract CSS Styles

### Objective
Separate all CSS into modular stylesheets for maintainability and reusability.

### Tasks
1. **Create CSS directory structure**
   - `css/variables.css` - CSS custom properties (colors, spacing, shadows)
   - `css/layout.css` - Grid systems, containers, responsive breakpoints
   - `css/components.css` - KPI boxes, cards, tables, buttons
   - `css/charts.css` - Chart-specific styles, tooltips

2. **Extract and organize styles**
   - Move `:root` variables to `variables.css`
   - Move layout/grid styles to `layout.css`
   - Move component styles to `components.css`
   - Move chart/tooltip styles to `charts.css`

3. **Update HTML references**
   - Replace `<style>` block with `<link>` tags
   - Maintain load order for cascade dependencies

### Deliverables
- `css/variables.css` (~50 lines)
- `css/layout.css` (~150 lines)
- `css/components.css` (~200 lines)
- `css/charts.css` (~50 lines)
- Updated `autonomy_dashboard.html` with CSS links

### Testing Cases

#### TC1.1: Visual Regression - Layout Integrity
**Objective:** Ensure no visual changes after CSS extraction  
**Steps:**
1. Take screenshot of original dashboard (all tabs)
2. Apply CSS modularization
3. Take screenshot of modularized dashboard (all tabs)
4. Compare screenshots pixel-by-pixel
5. Verify responsive breakpoints (1600px, 1200px, 768px)

**Expected Result:** Zero visual differences, all breakpoints work identically

**Test Script:**
```python
# scripts/test_dashboard_css_extraction.py
import pytest
from selenium import webdriver
from PIL import Image, ImageChops

def test_visual_regression():
    driver = webdriver.Chrome()
    
    # Original
    driver.get('file:///c:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard_original.html')
    driver.save_screenshot('original.png')
    
    # Modularized
    driver.get('file:///c:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
    driver.save_screenshot('modularized.png')
    
    # Compare
    img1 = Image.open('original.png')
    img2 = Image.open('modularized.png')
    diff = ImageChops.difference(img1, img2)
    
    assert diff.getbbox() is None, "Visual differences detected"
```

#### TC1.2: CSS Variable Inheritance
**Objective:** Verify CSS custom properties cascade correctly  
**Steps:**
1. Open browser DevTools
2. Inspect KPI box element
3. Verify `--primary`, `--success`, `--danger` colors resolve
4. Change `--primary` in variables.css
5. Verify all primary-colored elements update

**Expected Result:** All CSS variables resolve correctly, changes propagate

#### TC1.3: Responsive Breakpoints
**Objective:** Ensure responsive design works across devices  
**Steps:**
1. Open dashboard in browser
2. Resize to 1600px width → verify 4-column KPI grid
3. Resize to 1200px width → verify 2-column chart grid
4. Resize to 768px width → verify 1-column layout, vertical tabs

**Expected Result:** Layout adapts smoothly at each breakpoint

#### TC1.4: Cross-Browser Compatibility
**Objective:** Verify CSS works in Chrome, Firefox, Edge  
**Steps:**
1. Open dashboard in Chrome → verify styles
2. Open dashboard in Firefox → verify styles
3. Open dashboard in Edge → verify styles
4. Check for vendor prefix requirements

**Expected Result:** Identical rendering across browsers

---

## Phase 2: Extract Data Files

### Objective
Move embedded data arrays to external JSON files for easier updates and version control.

### Tasks
1. **Create data directory**
   - `data/dashboard_data.json` - Territory metrics (dashboardData array)
   - `data/agent_data.json` - Per-agent distributions (realAgentData object)
   - `data/recommendations.json` - Prioritized recommendations
   - `data/observations.json` - Strategic observations

2. **Extract data from HTML**
   - Copy `dashboardData` array → `dashboard_data.json`
   - Copy `realAgentData` object → `agent_data.json`
   - Copy `recommendationsData` array → `recommendations.json`
   - Copy `strategicObservationsData` object → `observations.json`

3. **Create data loader module**
   - `js/data/data-loader.js` - Async fetch functions
   - Handle file:// protocol fallback
   - Add error handling and retry logic

### Deliverables
- `data/dashboard_data.json` (~400KB)
- `data/agent_data.json` (~150KB)
- `data/recommendations.json` (~5KB)
- `data/observations.json` (~3KB)
- `js/data/data-loader.js` (~100 lines)

### Testing Cases

#### TC2.1: Data Loading - Success Path
**Objective:** Verify all data files load correctly  
**Steps:**
1. Start local HTTP server: `python -m http.server 8080`
2. Navigate to `http://localhost:8080/autonomy_dashboard.html`
3. Open DevTools Network tab
4. Verify 4 JSON files load with 200 status
5. Verify dashboard renders with correct data

**Expected Result:** All data loads, dashboard displays correctly

**Test Script:**
```python
# scripts/test_dashboard_data_loading.py
import pytest
import json
from pathlib import Path

def test_data_files_exist():
    """Verify all data files exist"""
    base = Path('c:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/data')
    assert (base / 'dashboard_data.json').exists()
    assert (base / 'agent_data.json').exists()
    assert (base / 'recommendations.json').exists()
    assert (base / 'observations.json').exists()

def test_data_files_valid_json():
    """Verify all data files are valid JSON"""
    base = Path('c:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/data')
    
    for file in ['dashboard_data.json', 'agent_data.json', 'recommendations.json', 'observations.json']:
        with open(base / file) as f:
            data = json.load(f)
            assert data is not None

def test_dashboard_data_structure():
    """Verify dashboard_data.json has required fields"""
    with open('data/dashboard_data.json') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check TOTAL row exists
    total_row = next((r for r in data if r['Territory'] == 'TOTAL'), None)
    assert total_row is not None
    
    # Check required fields
    required_fields = ['Territory', 'Total', 'Compliant', 'Heal Cap %', 'Health']
    for field in required_fields:
        assert field in total_row

def test_agent_data_structure():
    """Verify agent_data.json has required structure"""
    with open('data/agent_data.json') as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    
    # Check at least one territory exists
    assert len(data) > 0
    
    # Check structure of first territory
    first_territory = next(iter(data.values()))
    assert 'healCap' in first_territory
    assert 'invocation' in first_territory
    assert isinstance(first_territory['healCap'], list)
```

#### TC2.2: Data Loading - Error Handling
**Objective:** Verify graceful degradation when data fails to load  
**Steps:**
1. Rename `dashboard_data.json` to simulate missing file
2. Open dashboard
3. Verify error message displays
4. Verify dashboard doesn't crash
5. Restore file, verify recovery

**Expected Result:** User-friendly error message, no JavaScript errors

#### TC2.3: Data Loading - file:// Protocol Fallback
**Objective:** Verify dashboard works when opened directly (no server)  
**Steps:**
1. Open `autonomy_dashboard.html` directly in browser (file://)
2. Verify fallback message displays
3. Verify instructions for running local server shown

**Expected Result:** Clear instructions, no console errors

#### TC2.4: Data Integrity - Field Validation
**Objective:** Ensure data files match expected schema  
**Steps:**
1. Load `dashboard_data.json`
2. Validate each row has required fields
3. Validate data types (numbers, strings, arrays)
4. Check for "N/A" handling in L0 territories

**Expected Result:** All data conforms to schema

---

## Phase 3: Extract Utility Functions

### Objective
Create reusable utility modules for common operations.

### Tasks
1. **Create utility modules**
   - `js/utils/color-utils.js` - Color coding, thresholds
   - `js/utils/math-utils.js` - Statistics, distributions
   - `js/utils/format-utils.js` - Formatters, badges
   - `js/utils/random-utils.js` - Seeded PRNG

2. **Extract functions**
   - Move `getColor()`, `getWorstCaseColor()` → `color-utils.js`
   - Move `computeDistributionStats()` → `math-utils.js`
   - Move `formatDistributionCell()`, `formatOutlierBadge()` → `format-utils.js`
   - Move `hashString()`, `mulberry32()`, `createSeededRandom()` → `random-utils.js`

3. **Add JSDoc documentation**
   - Document parameters, return types
   - Add usage examples
   - Include edge case handling

### Deliverables
- `js/utils/color-utils.js` (~80 lines)
- `js/utils/math-utils.js` (~100 lines)
- `js/utils/format-utils.js` (~150 lines)
- `js/utils/random-utils.js` (~60 lines)

### Testing Cases

#### TC3.1: Color Utils - Threshold Accuracy
**Objective:** Verify color coding matches business rules  
**Steps:**
1. Test `getColor(85, true)` → expect '#16a34a' (green)
2. Test `getColor(75, true)` → expect '#42a35a' (light green)
3. Test `getColor(40, true)` → expect '#eab308' (yellow)
4. Test `getColor(10, true)` → expect '#dc2626' (red)
5. Test `getColor(15, false)` → expect '#42a35a' (complexity inverted)

**Expected Result:** All thresholds return correct colors

**Test Script:**
```javascript
// scripts/test_color_utils.js
import { getColor, getWorstCaseColor } from '../js/utils/color-utils.js';

describe('Color Utils', () => {
  describe('getColor - High Good', () => {
    it('should return green for values >= 85', () => {
      expect(getColor(85, true)).toBe('#16a34a');
      expect(getColor(100, true)).toBe('#16a34a');
    });
    
    it('should return red for values < 20', () => {
      expect(getColor(10, true)).toBe('#dc2626');
      expect(getColor(0, true)).toBe('#dc2626');
    });
  });
  
  describe('getColor - Low Good (Complexity)', () => {
    it('should return green for values <= 10', () => {
      expect(getColor(5, false)).toBe('#16a34a');
      expect(getColor(10, false)).toBe('#16a34a');
    });
    
    it('should return red for values > 40', () => {
      expect(getColor(50, false)).toBe('#dc2626');
      expect(getColor(100, false)).toBe('#dc2626');
    });
  });
  
  describe('getWorstCaseColor', () => {
    it('should handle N/A values', () => {
      expect(getWorstCaseColor('N/A')).toBe('#6b7280');
    });
    
    it('should use min value for color', () => {
      expect(getWorstCaseColor(90)).toBe('#065f46');
      expect(getWorstCaseColor(10)).toBe('#dc2626');
    });
  });
});
```

#### TC3.2: Math Utils - Statistical Accuracy
**Objective:** Verify statistical calculations are correct  
**Steps:**
1. Test `computeDistributionStats([10, 20, 30, 40, 50])`
   - Expect: min=10, max=50, avg=30, stdDev≈14.14
2. Test with "N/A" values: `[10, "N/A", 30]`
   - Expect: Filters out "N/A", computes on [10, 30]
3. Test empty array: `[]`
   - Expect: {min: 0, max: 0, avg: 0, stdDev: 0}

**Expected Result:** All calculations match mathematical expectations

#### TC3.3: Format Utils - Edge Cases
**Objective:** Verify formatters handle edge cases  
**Steps:**
1. Test `formatDistributionCell("N/A", {})` → expect italic "N/A"
2. Test `formatDistributionCell(75.2, {min: 45, max: 100, stdDev: 18.3})`
   - Expect: "75.2% (45-100, σ=18.3)"
3. Test `formatOutlierBadge(3, 5, 50)`
   - Expect: Badge with "3 @0%" and "5 <50%"

**Expected Result:** All edge cases handled gracefully

#### TC3.4: Random Utils - Determinism
**Objective:** Verify seeded PRNG produces consistent results  
**Steps:**
1. Create seeded random: `const rng = createSeededRandom("test-seed")`
2. Generate 10 values: `const vals1 = Array(10).fill(0).map(() => rng())`
3. Reset seed: `const rng2 = createSeededRandom("test-seed")`
4. Generate 10 values: `const vals2 = Array(10).fill(0).map(() => rng2())`
5. Compare arrays

**Expected Result:** vals1 === vals2 (identical sequences)

---

## Phase 4: Extract Rendering Functions

### Objective
Modularize rendering logic into focused, testable modules.

### Tasks
1. **Create renderer modules**
   - `js/renderers/table-renderer.js` - Territory & quality tables
   - `js/renderers/chart-renderer.js` - Plotly charts
   - `js/renderers/kpi-renderer.js` - KPI boxes
   - `js/renderers/modal-renderer.js` - Drill-down modals

2. **Extract rendering functions**
   - Move `renderTerritorySummaryTable()`, `renderCodeQualityTable()` → `table-renderer.js`
   - Move `renderHealthChart()`, `renderComplexityChart()`, etc. → `chart-renderer.js`
   - Move KPI box rendering → `kpi-renderer.js`
   - Move `openDrillModal()` → `modal-renderer.js`

3. **Add dependency injection**
   - Pass DOM elements as parameters
   - Avoid global state access
   - Return render results for testing

### Deliverables
- `js/renderers/table-renderer.js` (~400 lines)
- `js/renderers/chart-renderer.js` (~600 lines)
- `js/renderers/kpi-renderer.js` (~150 lines)
- `js/renderers/modal-renderer.js` (~200 lines)

### Testing Cases

#### TC4.1: Table Renderer - Data Binding
**Objective:** Verify table renders correct data  
**Steps:**
1. Load test data: `[{Territory: "L1", Total: 10, Health: 85}]`
2. Call `renderTerritorySummaryTable(data, containerElement)`
3. Verify table has 1 row
4. Verify cells contain correct values
5. Verify sparklines render

**Expected Result:** Table matches input data exactly

**Test Script:**
```javascript
// scripts/test_table_renderer.js
import { renderTerritorySummaryTable } from '../js/renderers/table-renderer.js';

describe('Table Renderer', () => {
  let container;
  
  beforeEach(() => {
    container = document.createElement('div');
    container.id = 'test-container';
    document.body.appendChild(container);
  });
  
  afterEach(() => {
    document.body.removeChild(container);
  });
  
  it('should render territory summary table', () => {
    const data = [
      { Territory: 'L1 Cognition', Total: 27, Compliant: 27, Health: 82.5, 'Heal Cap %': 100 }
    ];
    
    renderTerritorySummaryTable(data, container);
    
    const rows = container.querySelectorAll('tbody tr');
    expect(rows.length).toBe(1);
    
    const cells = rows[0].querySelectorAll('td');
    expect(cells[0].textContent).toContain('L1 Cognition');
    expect(cells[1].textContent).toContain('27');
  });
  
  it('should handle N/A values for L0 territories', () => {
    const data = [
      { Territory: 'L0 Core', Total: 10, 'Heal Cap %': 'N/A', 'Invocation %': 'N/A' }
    ];
    
    renderTerritorySummaryTable(data, container);
    
    const naCell = container.querySelector('td[data-metric="heal-cap"]');
    expect(naCell.textContent).toContain('N/A');
    expect(naCell.style.fontStyle).toBe('italic');
  });
});
```

#### TC4.2: Chart Renderer - Plotly Integration
**Objective:** Verify charts render with correct Plotly config  
**Steps:**
1. Call `renderHealthChart(data, 'chart-container')`
2. Verify Plotly.newPlot called with correct data
3. Verify chart layout (margins, colors, axes)
4. Verify hover tooltips work
5. Test offline mode fallback

**Expected Result:** Charts render correctly, tooltips functional

#### TC4.3: KPI Renderer - Dynamic Styling
**Objective:** Verify KPI boxes apply correct CSS classes  
**Steps:**
1. Render KPI with value 90 → expect 'success' class
2. Render KPI with value 50 → expect 'warning' class
3. Render KPI with value 20 → expect 'danger' class
4. Verify sparklines render with trend arrows

**Expected Result:** CSS classes match value thresholds

#### TC4.4: Modal Renderer - Drill-Down Data
**Objective:** Verify drill-down modal shows correct agent details  
**Steps:**
1. Click territory row
2. Verify modal opens
3. Verify modal title matches territory
4. Verify agent list displays
5. Verify VS Code links are correct
6. Close modal, verify cleanup

**Expected Result:** Modal displays correct data, links work

---

## Phase 5: Extract Controllers

### Objective
Separate business logic and event handling into controller modules.

### Tasks
1. **Create controller modules**
   - `js/controllers/tab-controller.js` - Tab switching logic
   - `js/controllers/filter-controller.js` - Table filtering/sorting
   - `js/controllers/refresh-controller.js` - Auto-refresh, manual refresh

2. **Extract controller logic**
   - Move `openTab()` → `tab-controller.js`
   - Move filter/sort state management → `filter-controller.js`
   - Move `manualRefresh()`, auto-refresh interval → `refresh-controller.js`

3. **Implement event delegation**
   - Use event listeners instead of inline onclick
   - Add proper cleanup on page unload
   - Support keyboard navigation

### Deliverables
- `js/controllers/tab-controller.js` (~100 lines)
- `js/controllers/filter-controller.js` (~200 lines)
- `js/controllers/refresh-controller.js` (~80 lines)

### Testing Cases

#### TC5.1: Tab Controller - Navigation
**Objective:** Verify tab switching works correctly  
**Steps:**
1. Click "Strategic Health" tab → verify content shows
2. Click "Live Runtime" tab → verify content switches
3. Click "Recommendations" tab → verify content switches
4. Verify URL hash updates (#executive, #runtime, etc.)
5. Reload page with hash → verify correct tab active

**Expected Result:** Tabs switch smoothly, state persists in URL

**Test Script:**
```javascript
// scripts/test_tab_controller.js
import { TabController } from '../js/controllers/tab-controller.js';

describe('Tab Controller', () => {
  let controller;
  
  beforeEach(() => {
    // Setup DOM
    document.body.innerHTML = `
      <div class="nav-tabs">
        <a class="nav-tab active" data-target="executive">Executive</a>
        <a class="nav-tab" data-target="runtime">Runtime</a>
      </div>
      <div id="executive-content" class="tab-content"></div>
      <div id="runtime-content" class="tab-content" style="display:none;"></div>
    `;
    
    controller = new TabController();
  });
  
  it('should switch tabs on click', () => {
    const runtimeTab = document.querySelector('[data-target="runtime"]');
    runtimeTab.click();
    
    expect(runtimeTab.classList.contains('active')).toBe(true);
    expect(document.getElementById('runtime-content').style.display).not.toBe('none');
    expect(document.getElementById('executive-content').style.display).toBe('none');
  });
  
  it('should update URL hash', () => {
    const runtimeTab = document.querySelector('[data-target="runtime"]');
    runtimeTab.click();
    
    expect(window.location.hash).toBe('#runtime');
  });
  
  it('should restore tab from URL hash on load', () => {
    window.location.hash = '#runtime';
    controller.init();
    
    const runtimeTab = document.querySelector('[data-target="runtime"]');
    expect(runtimeTab.classList.contains('active')).toBe(true);
  });
});
```

#### TC5.2: Filter Controller - Table Filtering
**Objective:** Verify table filters work correctly  
**Steps:**
1. Apply filter: "Show only critical (Health < 50%)"
2. Verify only matching rows display
3. Apply sort: "Sort by Health ascending"
4. Verify rows reorder correctly
5. Clear filters → verify all rows return

**Expected Result:** Filters and sorts work correctly, state persists

#### TC5.3: Refresh Controller - Auto-Refresh
**Objective:** Verify auto-refresh works correctly  
**Steps:**
1. Wait 30 seconds → verify page reloads
2. Click "Refresh Now" → verify immediate reload
3. Verify refresh indicator pulses
4. Verify refresh status shows "Auto-refresh: 30s"

**Expected Result:** Auto-refresh works, manual refresh works

#### TC5.4: Filter Controller - Export Functionality
**Objective:** Verify CSV export works  
**Steps:**
1. Click "Export CSV" button
2. Verify download triggers
3. Open CSV file
4. Verify data matches table
5. Verify headers correct

**Expected Result:** CSV export contains correct data

---

## Phase 6: Create Main Orchestrator

### Objective
Create a main entry point that coordinates all modules.

### Tasks
1. **Create main.js**
   - Initialize data loader
   - Initialize renderers
   - Initialize controllers
   - Setup error handling
   - Coordinate module lifecycle

2. **Add configuration**
   - `js/config.js` - Constants, API endpoints, thresholds
   - Environment-specific settings
   - Feature flags

3. **Update HTML**
   - Add module script tags
   - Remove inline JavaScript
   - Add loading indicators

### Deliverables
- `js/main.js` (~200 lines)
- `js/config.js` (~50 lines)
- Updated `autonomy_dashboard.html` (~200 lines)

### Testing Cases

#### TC6.1: End-to-End - Full Dashboard Load
**Objective:** Verify complete dashboard loads and functions  
**Steps:**
1. Open dashboard in browser
2. Verify all data loads (4 JSON files)
3. Verify all tabs render
4. Verify all charts render
5. Verify all tables render
6. Verify no console errors

**Expected Result:** Dashboard fully functional, zero errors

**Test Script:**
```python
# scripts/test_dashboard_end_to_end_modular.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_full_dashboard_load():
    driver = webdriver.Chrome()
    driver.get('http://localhost:8080/autonomy_dashboard.html')
    
    # Wait for data to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'kpiGrid'))
    )
    
    # Verify tables rendered
    territory_table = driver.find_element(By.ID, 'kpiGrid')
    assert territory_table.text != '', "Territory table is empty"
    
    quality_table = driver.find_element(By.ID, 'codeQualityGrid')
    assert quality_table.text != '', "Quality table is empty"
    
    # Verify tabs work
    runtime_tab = driver.find_element(By.CSS_SELECTOR, '[data-target="runtime"]')
    runtime_tab.click()
    
    runtime_content = driver.find_element(By.ID, 'runtime-content')
    assert runtime_content.is_displayed(), "Runtime tab not visible"
    
    # Verify no console errors
    logs = driver.get_log('browser')
    errors = [log for log in logs if log['level'] == 'SEVERE']
    assert len(errors) == 0, f"Console errors found: {errors}"
    
    driver.quit()
```

#### TC6.2: Performance - Load Time
**Objective:** Verify dashboard loads within acceptable time  
**Steps:**
1. Open dashboard with DevTools Performance tab
2. Measure time to interactive
3. Measure time to first paint
4. Measure total load time
5. Compare to baseline (original monolithic)

**Expected Result:** Load time ≤ baseline + 10%

#### TC6.3: Error Handling - Missing Module
**Objective:** Verify graceful degradation when module fails  
**Steps:**
1. Rename `chart-renderer.js` to simulate missing file
2. Open dashboard
3. Verify error message displays
4. Verify tables still render (partial functionality)
5. Verify no JavaScript crashes

**Expected Result:** User-friendly error, partial functionality preserved

#### TC6.4: Backward Compatibility - Data Format
**Objective:** Verify dashboard works with old data format  
**Steps:**
1. Use old `agent_discovery_full.json` format
2. Verify data loader adapts
3. Verify dashboard renders
4. Verify no data loss

**Expected Result:** Backward compatible with existing data

---

## Phase 7: Integration Testing & Validation

### Objective
Comprehensive testing of modularized dashboard against original.

### Tasks
1. **Run full test suite**
   - Execute all 24 test cases
   - Generate coverage report
   - Document any failures

2. **Performance benchmarking**
   - Compare load times
   - Compare memory usage
   - Compare render times

3. **User acceptance testing**
   - Verify all features work
   - Verify no regressions
   - Collect feedback

### Testing Cases

#### TC7.1: Regression Test Suite
**Objective:** Verify zero regressions from original  
**Steps:**
1. Run all Phase 1-6 tests
2. Generate test report
3. Verify 100% pass rate

**Expected Result:** All tests pass

**Test Script:**
```bash
# scripts/run_all_dashboard_tests.sh
#!/bin/bash

echo "Running Dashboard Modularization Test Suite"
echo "==========================================="

# Phase 1: CSS Tests
echo "Phase 1: CSS Extraction Tests..."
pytest scripts/test_dashboard_css_extraction.py -v

# Phase 2: Data Loading Tests
echo "Phase 2: Data Loading Tests..."
pytest scripts/test_dashboard_data_loading.py -v

# Phase 3: Utility Tests
echo "Phase 3: Utility Function Tests..."
npm test -- test_color_utils.js
npm test -- test_math_utils.js

# Phase 4: Renderer Tests
echo "Phase 4: Renderer Tests..."
npm test -- test_table_renderer.js
npm test -- test_chart_renderer.js

# Phase 5: Controller Tests
echo "Phase 5: Controller Tests..."
npm test -- test_tab_controller.js
npm test -- test_filter_controller.js

# Phase 6: End-to-End Tests
echo "Phase 6: End-to-End Tests..."
pytest scripts/test_dashboard_end_to_end_modular.py -v

echo "==========================================="
echo "Test Suite Complete"
```

#### TC7.2: Performance Comparison
**Objective:** Verify modular version performs acceptably  
**Steps:**
1. Measure original dashboard load time (10 runs, average)
2. Measure modular dashboard load time (10 runs, average)
3. Compare memory footprint
4. Compare time to interactive

**Expected Result:** Performance within 10% of original

#### TC7.3: Cross-Browser Testing
**Objective:** Verify works in all major browsers  
**Steps:**
1. Test in Chrome (latest)
2. Test in Firefox (latest)
3. Test in Edge (latest)
4. Test in Safari (if available)

**Expected Result:** Works identically in all browsers

#### TC7.4: Accessibility Testing
**Objective:** Verify dashboard is accessible  
**Steps:**
1. Run Lighthouse accessibility audit
2. Test keyboard navigation
3. Test screen reader compatibility
4. Verify ARIA labels

**Expected Result:** Lighthouse score ≥ 90

---

## Risk Mitigation

### High Risks
1. **Data Loading Race Conditions**
   - **Mitigation:** Use Promise.all() for parallel loads, add loading indicators
   - **Test:** TC2.1, TC6.1

2. **CSS Cascade Conflicts**
   - **Mitigation:** Maintain load order, use specific selectors
   - **Test:** TC1.1, TC1.2

3. **Breaking Changes to Data Format**
   - **Mitigation:** Add schema validation, version data files
   - **Test:** TC6.4

### Medium Risks
1. **Browser Compatibility Issues**
   - **Mitigation:** Use ES6 modules with fallback, test cross-browser
   - **Test:** TC1.4, TC7.3

2. **Performance Degradation**
   - **Mitigation:** Lazy load modules, minimize HTTP requests
   - **Test:** TC6.2, TC7.2

---

## Rollout Strategy

### Phase Rollout
1. **Phase 1-2 (Week 1):** CSS + Data extraction
   - Low risk, high value
   - Run TC1.x, TC2.x tests
   - Deploy to dev environment

2. **Phase 3-4 (Week 2):** Utils + Renderers
   - Medium risk, high complexity
   - Run TC3.x, TC4.x tests
   - Deploy to staging

3. **Phase 5-6 (Week 3):** Controllers + Main
   - Medium risk, final integration
   - Run TC5.x, TC6.x tests
   - Deploy to staging

4. **Phase 7 (Week 4):** Integration testing
   - Run full test suite (TC7.x)
   - User acceptance testing
   - Deploy to production

### Rollback Plan
- Keep original `autonomy_dashboard_original.html` as backup
- Use feature flag to toggle between versions
- Monitor error rates post-deployment

---

## Success Metrics

### Quantitative
- **File Size:** Reduce main HTML from 598KB to <50KB
- **Maintainability:** Reduce average function length from 50 to <20 lines
- **Test Coverage:** Achieve >80% code coverage
- **Load Time:** Maintain load time within 10% of baseline
- **Error Rate:** Zero increase in console errors

### Qualitative
- **Developer Experience:** Easier to find and modify code
- **Code Reusability:** Utility functions reusable across dashboards
- **Debugging:** Easier to isolate and fix bugs
- **Extensibility:** Easier to add new features

---

## Appendix A: File Structure Summary

```
dashboards/
├── autonomy_dashboard.html (200 lines, -97% from 15,395)
├── autonomy_dashboard_original.html (backup)
├── css/
│   ├── variables.css (50 lines)
│   ├── layout.css (150 lines)
│   ├── components.css (200 lines)
│   └── charts.css (50 lines)
├── js/
│   ├── config.js (50 lines)
│   ├── main.js (200 lines)
│   ├── utils/
│   │   ├── color-utils.js (80 lines)
│   │   ├── math-utils.js (100 lines)
│   │   ├── format-utils.js (150 lines)
│   │   └── random-utils.js (60 lines)
│   ├── data/
│   │   ├── data-loader.js (100 lines)
│   │   └── data-processor.js (150 lines)
│   ├── renderers/
│   │   ├── table-renderer.js (400 lines)
│   │   ├── chart-renderer.js (600 lines)
│   │   ├── kpi-renderer.js (150 lines)
│   │   └── modal-renderer.js (200 lines)
│   └── controllers/
│       ├── tab-controller.js (100 lines)
│       ├── filter-controller.js (200 lines)
│       └── refresh-controller.js (80 lines)
├── data/
│   ├── dashboard_data.json (400KB)
│   ├── agent_data.json (150KB)
│   ├── recommendations.json (5KB)
│   └── observations.json (3KB)
└── tests/
    ├── test_css_extraction.py
    ├── test_data_loading.py
    ├── test_color_utils.js
    ├── test_math_utils.js
    ├── test_table_renderer.js
    ├── test_chart_renderer.js
    ├── test_tab_controller.js
    ├── test_filter_controller.js
    └── test_end_to_end_modular.py
```

**Total Files:** 30 (vs 1 original)  
**Total Lines of Code:** ~3,670 (vs 15,395 in single file)  
**Reduction:** 76% reduction in monolithic code

---

## Appendix B: Test Execution Checklist

### Pre-Deployment Checklist
- [ ] All Phase 1 tests pass (TC1.1-TC1.4)
- [ ] All Phase 2 tests pass (TC2.1-TC2.4)
- [ ] All Phase 3 tests pass (TC3.1-TC3.4)
- [ ] All Phase 4 tests pass (TC4.1-TC4.4)
- [ ] All Phase 5 tests pass (TC5.1-TC5.4)
- [ ] All Phase 6 tests pass (TC6.1-TC6.4)
- [ ] All Phase 7 tests pass (TC7.1-TC7.4)
- [ ] Visual regression tests pass
- [ ] Performance benchmarks acceptable
- [ ] Cross-browser tests pass
- [ ] Accessibility audit score ≥90
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Backup created
- [ ] Rollback plan tested

---

## Appendix C: Dependencies

### Required Tools
- **Python 3.8+** - For test scripts
- **Node.js 16+** - For JavaScript tests
- **pytest** - Python testing framework
- **Jest** - JavaScript testing framework
- **Selenium** - Browser automation
- **Lighthouse** - Accessibility/performance audits

### Installation
```bash
# Python dependencies
pip install pytest selenium pillow

# Node dependencies
npm install --save-dev jest @testing-library/dom

# Browser drivers
# Chrome: Download from https://chromedriver.chromium.org/
# Firefox: Download from https://github.com/mozilla/geckodriver/releases
```

---

**End of Implementation Plan**
