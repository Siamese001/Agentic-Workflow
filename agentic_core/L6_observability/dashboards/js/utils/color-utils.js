/**
 * Color Logic and Thresholds
 */

// Standard RAG (Red-Amber-Green) thresholds
function getColor(value, highGood = true) {
    const v = parseFloat(value);
    if (isNaN(v)) return '#6b7280'; // Gray for N/A

    if (highGood) {
        if (v >= 85) return '#16a34a';  // Green
        if (v >= 75) return '#42a35a';  // Light Green
        if (v >= 60) return '#96b746';  // Yellow-Green
        if (v >= 40) return '#eab308';  // Yellow
        if (v >= 20) return '#ea580c';  // Orange
        return '#dc2626';               // Red
    } else {  // Low good (e.g. Complexity)
        if (v <= 10) return '#16a34a';
        if (v <= 15) return '#42a35a';
        if (v <= 20) return '#96b746';
        if (v <= 30) return '#eab308';
        if (v <= 40) return '#ea580c';
        return '#dc2626';
    }
}

// Safe wrapper for visualization
function getWorstCaseColor(value) {
    if (value === 'N/A' || value === undefined || value === null) return '#6b7280';
    return getColor(parseFloat(value), true);
}

// Dynamic gradient background generator
function getGradientBg(value) {
    if (value === 'N/A' || value === undefined || typeof value !== 'number') return 'transparent';
    
    // Normalize 0-100 to 0-1
    const normalized = Math.max(0, Math.min(100, value)) / 100;
    let r, g, b;

    // Red -> Yellow -> Green interpolation
    if (normalized < 0.5) {
        // Red (255, 200, 200) to Yellow (255, 255, 200)
        r = 255;
        g = Math.round(200 + (55 * (normalized * 2)));
        b = 200;
    } else {
        // Yellow (255, 255, 200) to Green (200, 255, 200)
        r = Math.round(255 - (55 * ((normalized - 0.5) * 2)));
        g = 255;
        b = 200;
    }
    
    // Return as semi-transparent RGBA for table cells
    return `rgba(${r}, ${g}, ${b}, 0.3)`;
}
