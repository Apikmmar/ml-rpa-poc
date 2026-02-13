async function listExceptions() {
    const resultDiv = document.getElementById('exceptionsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading exceptions...';

    try {
        const result = await fetch(`${API_URL}/exceptions`);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Error Type</th><th>Message</th><th>Severity</th><th>Status</th><th>Assigned To</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${fields.error_type || 'N/A'}</td>
                    <td>${fields.error_message || 'N/A'}</td>
                    <td>${fields.severity || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.assigned_to || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No exceptions found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

async function listAuditLogs() {
    const resultDiv = document.getElementById('auditLogsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading audit logs...';

    try {
        const result = await fetch(`${API_URL}/audit-logs`);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Step</th><th>Status</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${fields.step || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No audit logs found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

async function listBackorders() {
    const resultDiv = document.getElementById('backordersResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading backorders...';

    try {
        const result = await fetch(`${API_URL}/backorders`);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>SKU</th><th>Quantity</th><th>Customer Email</th><th>Status</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${fields.sku || 'N/A'}</td>
                    <td>${fields.quantity || 0}</td>
                    <td>${fields.customer_email || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No backorders found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

async function listNotifications() {
    const resultDiv = document.getElementById('notificationsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading notifications...';

    try {
        const result = await fetch(`${API_URL}/notifications`);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Type</th><th>Message</th><th>Recipient</th><th>Status</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${fields.notification_type || 'N/A'}</td>
                    <td>${fields.message || 'N/A'}</td>
                    <td>${fields.recipient || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No notifications found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

async function getMetrics() {
    const resultDiv = document.getElementById('metricsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading metrics...';

    try {
        const result = await fetch(`${API_URL}/metrics/dashboard`);
        const json = await result.json();
        resultDiv.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                <div class="metric-card">
                    <h3>Total Orders</h3>
                    <p style="font-size: 2em; font-weight: bold;">${json.total_orders}</p>
                </div>
                <div class="metric-card">
                    <h3>Total Audit Logs</h3>
                    <p style="font-size: 2em; font-weight: bold;">${json.total_audit_logs}</p>
                </div>
                <div class="metric-card">
                    <h3>Avg Processing Time</h3>
                    <p style="font-size: 2em; font-weight: bold;">${json.avg_processing_time}s</p>
                </div>
                <div class="metric-card">
                    <h3>Success Rate</h3>
                    <p style="font-size: 2em; font-weight: bold;">${json.success_rate}%</p>
                </div>
            </div>
        `;
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}
