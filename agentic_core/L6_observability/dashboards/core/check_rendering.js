// Dashboard Rendering Check Script
// Run this in browser console to diagnose rendering issues

console.log('=== Dashboard Rendering Check ===\n');

// Check 1: Data loaded
console.log('1. Data Check:');
console.log('   dashboardData:', typeof dashboardData !== 'undefined' ? `${dashboardData.length} items` : 'MISSING');
console.log('   recommendationsData:', typeof recommendationsData !== 'undefined' ? `${recommendationsData.length} items` : 'MISSING');
console.log('   gaugeData:', typeof gaugeData !== 'undefined' ? 'Present' : 'MISSING');

// Check 2: DOM elements
console.log('\n2. DOM Elements:');
const elements = {
    'kpiGrid': document.getElementById('kpiGrid'),
    'healthChart': document.getElementById('healthChart'),
    'healingChart': document.getElementById('healingChart'),
    'riskMatrix': document.getElementById('riskMatrix'),
    'complianceChart': document.getElementById('complianceChart'),
    'observabilityChart': document.getElementById('observabilityChart'),
    'complexityChart': document.getElementById('complexityChart'),
    'interviewQuestions': document.getElementById('interviewQuestions'),
    'recommendationsList': document.getElementById('recommendationsList'),
    'topRecommendations': document.getElementById('topRecommendations')
};

Object.entries(elements).forEach(([name, el]) => {
    if (el) {
        const hasContent = el.innerHTML.length > 0;
        console.log(`   ${name}: ${hasContent ? '✓ Rendered' : '⚠ Empty'} (${el.innerHTML.length} chars)`);
    } else {
        console.log(`   ${name}: ✗ MISSING`);
    }
});

// Check 3: Plotly
console.log('\n3. Plotly Library:');
console.log('   Loaded:', typeof Plotly !== 'undefined' ? '✓ Yes' : '✗ No');

// Check 4: Functions
console.log('\n4. Functions Defined:');
const functions = ['renderKPIBoxes', 'renderHealthChart', 'renderHealingChart', 'loadData'];
functions.forEach(fn => {
    console.log(`   ${fn}:`, typeof window[fn] === 'function' ? '✓' : '✗');
});

// Check 5: Tabs
console.log('\n5. Tab Navigation:');
const tabs = document.querySelectorAll('.nav-tab');
console.log(`   Total tabs: ${tabs.length}`);
tabs.forEach(tab => {
    console.log(`   - ${tab.textContent.trim()}: target="${tab.dataset.target}"`);
});

// Check 6: Active content
console.log('\n6. Visible Content:');
const tabContents = document.querySelectorAll('.tab-content');
tabContents.forEach(content => {
    const isVisible = content.style.display !== 'none';
    console.log(`   ${content.id}: ${isVisible ? 'Visible' : 'Hidden'}`);
});

console.log('\n=== Check Complete ===');
