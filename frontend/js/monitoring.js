async function listExceptions(refresh = false) {
    const resultDiv = document.getElementById('exceptionsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading exceptions...';
    try {
        const result = await fetch(`${API_URL}/exceptions${refresh ? '?refresh=true' : ''}`);
        const json = await result.json();
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Error Type</th><th>Message</th><th>Severity</th><th>Status</th><th>Assigned To</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr><td>${fields.error_type || 'N/A'}</td><td>${fields.error_message || 'N/A'}</td><td>${fields.severity || 'N/A'}</td><td>${fields.status || 'N/A'}</td><td>${fields.assigned_to || 'N/A'}</td><td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td></tr>`;
            });
            resultDiv.innerHTML = table + '</tbody></table>';
        } else { resultDiv.textContent = 'No exceptions found'; }
    } catch (error) { resultDiv.textContent = 'Error: ' + error.message; }
}

async function listAuditLogs(refresh = false) {
    const resultDiv = document.getElementById('auditLogsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading audit logs...';
    try {
        const result = await fetch(`${API_URL}/audit-logs${refresh ? '?refresh=true' : ''}`);
        const json = await result.json();
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Step</th><th>Status</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr><td>${fields.step || 'N/A'}</td><td>${fields.status || 'N/A'}</td><td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td></tr>`;
            });
            resultDiv.innerHTML = table + '</tbody></table>';
        } else { resultDiv.textContent = 'No audit logs found'; }
    } catch (error) { resultDiv.textContent = 'Error: ' + error.message; }
}

async function listBackorders(refresh = false) {
    const resultDiv = document.getElementById('backordersResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading backorders...';
    try {
        const result = await fetch(`${API_URL}/backorders${refresh ? '?refresh=true' : ''}`);
        const json = await result.json();
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>SKU</th><th>Quantity</th><th>Status</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr><td>${(Array.isArray(fields.sku) ? fields.sku.join(', ') : fields.sku) || 'N/A'}</td><td>${fields.qty_needed || 0}</td><td>${fields.status || 'N/A'}</td><td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td></tr>`;
            });
            resultDiv.innerHTML = table + '</tbody></table>';
        } else { resultDiv.textContent = 'No backorders found'; }
    } catch (error) { resultDiv.textContent = 'Error: ' + error.message; }
}

async function listNotifications(refresh = false) {
    const resultDiv = document.getElementById('notificationsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading notifications...';
    try {
        const result = await fetch(`${API_URL}/notifications${refresh ? '?refresh=true' : ''}`);
        const json = await result.json();
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Type</th><th>Recipient</th><th>Customer Email</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr><td>${fields.type || 'N/A'}</td><td>${fields.recipient || 'N/A'}</td><td>${(Array.isArray(fields.customer_email) ? fields.customer_email.join(', ') : fields.customer_email) || 'N/A'}</td><td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td></tr>`;
            });
            resultDiv.innerHTML = table + '</tbody></table>';
        } else { resultDiv.textContent = 'No notifications found'; }
    } catch (error) { resultDiv.textContent = 'Error: ' + error.message; }
}

async function getMetrics(refresh = false) {
    const resultDiv = document.getElementById('metricsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading metrics...';
    try {
        const result = await fetch(`${API_URL}/metrics/dashboard${refresh ? '?refresh=true' : ''}`);
        const json = await result.json();
        const byStatus = Object.entries(json.orders_by_status || {}).map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('');
        resultDiv.innerHTML = `<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px"><div class="metric-card"><h3>Total Orders</h3><p>${json.total_orders}</p></div><div class="metric-card"><h3>Audit Logs</h3><p>${json.total_audit_logs}</p></div><div class="metric-card"><h3>Success Rate</h3><p>${json.success_rate}%</p></div></div><div style="margin-top:16px"><strong>Orders by Status</strong><table><thead><tr><th>Status</th><th>Count</th></tr></thead><tbody>${byStatus}</tbody></table></div>`;
    } catch (error) { resultDiv.textContent = 'Error: ' + error.message; }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('exceptionsResult')) listExceptions();
    if (document.getElementById('auditLogsResult')) listAuditLogs();
    if (document.getElementById('backordersResult')) listBackorders();
    if (document.getElementById('notificationsResult')) listNotifications();
    if (document.getElementById('metricsResult')) getMetrics();
});
