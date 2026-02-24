async function listPicklists(forceRefresh = false) {
    const resultDiv = document.getElementById('picklistsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading picklists...';

    try {
        const url = forceRefresh ? `${API_URL}/picklists?refresh=true` : `${API_URL}/picklists`;
        const result = await fetch(url);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Picklist ID</th><th>Priority</th><th>Status</th><th>Customer Email</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${record.id}</td>
                    <td>${fields.priority || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.customer_email || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No picklists found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('picklistsResult')) listPicklists();
});

async function updatePicklistStatus() {
    const picklistId = document.getElementById('picklistId').value.trim();
    const status = document.getElementById('picklistStatus').value;
    if (!picklistId) { showToast('Please enter a Picklist ID', 'warning'); return; }

    const resultDiv = document.getElementById('picklistResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Updating status...';

    try {
        const result = await fetch(`${API_URL}/picklists/${picklistId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        const json = await result.json();
        showToast('Picklist status updated', 'success');
        resultDiv.textContent = JSON.stringify(json, null, 2);
    } catch (error) {
        showToast('Failed to update picklist', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

async function optimizeRoute() {
    const picklistId = document.getElementById('routePicklistId').value.trim();
    if (!picklistId) { showToast('Please enter a Picklist ID', 'warning'); return; }

    const resultDiv = document.getElementById('routeResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Optimizing route...';

    try {
        const result = await fetch(`${API_URL}/picklists/${picklistId}/route`);
        const json = await result.json();
        showToast('Route optimized', 'success');
        resultDiv.textContent = JSON.stringify(json, null, 2);
    } catch (error) {
        showToast('Failed to optimize route', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

async function generateQR() {
    const picklistId = document.getElementById('qrPicklistId').value.trim();
    if (!picklistId) { showToast('Please enter a Picklist ID', 'warning'); return; }

    const resultDiv = document.getElementById('qrResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Generating QR code...';

    try {
        const result = await fetch(`${API_URL}/picklists/${picklistId}/qr`);
        const json = await result.json();
        showToast('QR code generated', 'success');
        resultDiv.textContent = JSON.stringify(json, null, 2);
    } catch (error) {
        showToast('Failed to generate QR', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
    }
}
