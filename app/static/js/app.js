/* CRM Produto Digital - Base JS */

function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(function(el) {
        el.classList.remove('active');
    });
    document.querySelectorAll('.nav-btn').forEach(function(el) {
        el.classList.remove('active');
    });
    document.getElementById('tab-' + tab).classList.add('active');
    event.target.classList.add('active');
}

// Load dashboard stats
async function loadStats() {
    try {
        var resp = await fetch('/api/metrics/summary');
        if (resp.ok) {
            var data = await resp.json();
            document.getElementById('total-students').textContent = data.total_students || 0;
            document.getElementById('total-leads').textContent = data.total_leads || 0;
            document.getElementById('total-orders').textContent = data.total_orders || 0;
            document.getElementById('conversion-rate').textContent = (data.conversion_rate || 0) + '%';
        }
    } catch (e) {
        console.log('Metrics API not yet implemented');
    }
}

document.addEventListener('DOMContentLoaded', loadStats);
