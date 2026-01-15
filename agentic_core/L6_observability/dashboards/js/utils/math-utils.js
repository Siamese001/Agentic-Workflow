/**
 * Statistical Analysis Utilities
 */

function computeDistributionStats(values) {
    // Filter out N/A and non-numbers
    const numbers = values.filter(v => typeof v === 'number' && !isNaN(v));
    
    if (numbers.length === 0) return { min: 0, max: 0, avg: 0, stdDev: 0, count: 0 };
    
    const min = Math.min(...numbers);
    const max = Math.max(...numbers);
    const sum = numbers.reduce((a, b) => a + b, 0);
    const avg = sum / numbers.length;
    
    // Standard Deviation
    const sqDiff = numbers.map(v => Math.pow(v - avg, 2));
    const avgSqDiff = sqDiff.reduce((a, b) => a + b, 0) / numbers.length;
    const stdDev = Math.sqrt(avgSqDiff);
    
    return { min, max, avg, stdDev, count: numbers.length };
}

function countOutliers(values, threshold, direction = 'below') {
    const numbers = values.filter(v => typeof v === 'number' && !isNaN(v));
    if (direction === 'below') {
        return numbers.filter(v => v < threshold).length;
    } else {
        return numbers.filter(v => v > threshold).length;
    }
}

function getOutlierSummary(values, threshold, direction = 'below') {
    const numbers = values.filter(v => typeof v === 'number' && !isNaN(v));
    let atZero = 0;
    let belowThreshold = 0;
    
    numbers.forEach(v => {
        if (v === 0) atZero++;
        if (direction === 'below' && v < threshold) belowThreshold++;
        if (direction === 'above' && v > threshold) belowThreshold++;
    });
    
    return { atZero, belowThreshold, total: numbers.length };
}
