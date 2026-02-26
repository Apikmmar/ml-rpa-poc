async function listPicklists(forceRefresh = false) {
    const resultDiv = document.getElementById('picklistsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading picklists...';

    try {
        const url = forceRefresh ? `${API_URL}/picklists?refresh=true` : `${API_URL}/picklists`;
        const result = await fetch(url);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Picklist ID</th><th>Order ID</th><th>Priority</th><th>Status</th><th>Customer Email</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                const orderIds = Array.isArray(fields.order_id) ? fields.order_id.join(', ') : (fields.order_id || 'N/A');
                table += `<tr>
                    <td>${record.id}</td>
                    <td>${orderIds}</td>
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

function clearPicklistForm() {
    document.getElementById('picklistId').value = '';
    document.getElementById('picklistStatus').value = '';
    const resultDiv = document.getElementById('picklistResult');
    resultDiv.textContent = '';
    resultDiv.style.color = '';
}

async function updatePicklistStatus() {
    const picklistId = document.getElementById('picklistId').value.trim();
    const status = document.getElementById('picklistStatus').value;
    if (!picklistId) { showToast('Please enter a Picklist ID', 'warning'); return; }
    if (!status) { showToast('Please select a Status', 'warning'); return; }

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
        if (!result.ok) {
            const errCode = json.detail ? (typeof json.detail === 'string' ? JSON.parse(json.detail)?.error : json.detail) : null;
            const errMsg = errCode === 'NOT_FOUND' ? `Picklist "${picklistId}" not found. Please check the Picklist ID and try again.` : (errCode || 'Failed to update picklist status.');
            showToast(errMsg, 'error');
            resultDiv.style.color = 'red';
            resultDiv.textContent = errMsg;
            return;
        }
        showToast('Picklist status updated', 'success');
        resultDiv.style.color = 'green';
        resultDiv.textContent = `Picklist ${json.picklist_id} has been updated to "${json.status}".`;
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
        if (!result.ok) {
            showToast('Failed to optimize route', 'error');
            resultDiv.style.color = 'red';
            resultDiv.textContent = json.detail || 'Failed to optimize route.';
            return;
        }
        showToast('Route optimized', 'success');
        const stops = json.optimized_route;
        if (!stops || stops.length === 0) {
            resultDiv.textContent = 'No stops found for this picklist.';
            return;
        }
        let table = `<p style="color:green">Optimized route for Picklist ${json.picklist_id} — ${stops.length} stop(s)</p>`;
        table += '<table><thead><tr><th>#</th><th>SKU</th><th>Qty</th><th>Location</th><th>Rack</th></tr></thead><tbody>';
        stops.forEach((stop, i) => {
            table += `<tr><td>${i + 1}</td><td>${stop.sku}</td><td>${stop.qty}</td><td>${stop.location}</td><td>${stop.rack}</td></tr>`;
        });
        table += '</tbody></table>';
        resultDiv.innerHTML = table;
    } catch (error) {
        showToast('Failed to optimize route', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
    }
}