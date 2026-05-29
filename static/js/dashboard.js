// Dashboard Interactive Features
let autoRefreshInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
    startAutoRefresh();
});

function initializeCharts() {
    // Initialize any charts that need live data
    console.log('Dashboard initialized');
}

function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            refreshDashboard();
        });
    }
    
    // Date range picker
    const dateRange = document.getElementById('dateRange');
    if (dateRange) {
        dateRange.addEventListener('change', function() {
            updateDateRange(this.value);
        });
    }
}

function refreshDashboard() {
    showLoading();
    
    fetch('/api/dashboard_stats')
        .then(response => response.json())
        .then(data => {
            updateStats(data);
            hideLoading();
        })
        .catch(error => {
            console.error('Error refreshing dashboard:', error);
            hideLoading();
        });
}

function updateStats(data) {
    // Update stat cards with new data
    for (const [key, value] of Object.entries(data)) {
        const element = document.getElementById(`stat_${key}`);
        if (element) {
            element.textContent = formatNumber(value);
        }
    }
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function showLoading() {
    const loader = document.getElementById('loadingOverlay');
    if (loader) loader.style.display = 'flex';
}

function hideLoading() {
    const loader = document.getElementById('loadingOverlay');
    if (loader) loader.style.display = 'none';
}

function startAutoRefresh() {
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
    autoRefreshInterval = setInterval(() => {
        refreshDashboard();
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

function updateDateRange(range) {
    const now = new Date();
    let startDate;
    
    switch(range) {
        case 'today':
            startDate = new Date(now.setHours(0,0,0,0));
            break;
        case 'week':
            startDate = new Date(now.setDate(now.getDate() - 7));
            break;
        case 'month':
            startDate = new Date(now.setMonth(now.getMonth() - 1));
            break;
        default:
            startDate = new Date(now.setDate(now.getDate() - 30));
    }
    
    fetch(`/api/transactions?start=${startDate.toISOString()}&end=${new Date().toISOString()}`)
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
        });
}

function updateCharts(data) {
    // Update chart data dynamically
    console.log('Updating charts with new data');
}

// Export functionality
function exportData(format) {
    if (format === 'csv') {
        window.location.href = '/export_report';
    } else if (format === 'json') {
        fetch('/api/dashboard_stats')
            .then(response => response.json())
            .then(data => {
                const dataStr = JSON.stringify(data, null, 2);
                const blob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `fraud_report_${new Date().toISOString()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            });
    }
}