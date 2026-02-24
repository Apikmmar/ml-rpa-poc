async function approveTransfer() {
    const transferId = document.getElementById('approveTransferId').value.trim();
    if (!transferId) { showToast('Please enter a Transfer ID', 'warning'); return; }

    const resultDiv = document.getElementById('approveResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Approving transfer...';

    try {
        const result = await fetch(`${API_URL}/stock-transfers/${transferId}/approve`, { method: 'PATCH' });
        const json = await result.json();
        if (!result.ok) {
            const errMsg = json.detail || 'Failed to approve transfer.';
            showToast(errMsg, 'error');
            resultDiv.style.color = 'red';
            resultDiv.textContent = errMsg;
            return;
        }
        showToast('Transfer approved', 'success');
        resultDiv.style.color = 'green';
        resultDiv.textContent = `Transfer ${json.transfer_id} has been approved. Stock location has been updated.`;
    } catch (error) {
        showToast('Failed to approve transfer', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

function clearApproveForm() {
    document.getElementById('approveTransferId').value = '';
    const resultDiv = document.getElementById('approveResult');
    resultDiv.textContent = '';
    resultDiv.style.color = '';
}

function clearTransferForm() {
    document.getElementById('fromLocation').value = '';
    document.getElementById('toLocation').value = '';
    document.getElementById('fromRack').value = '';
    document.getElementById('toRack').value = '';
    document.getElementById('transferSku').value = '';
    document.getElementById('transferQty').value = '';
    const resultDiv = document.getElementById('transferResult');
    resultDiv.textContent = '';
    resultDiv.style.color = '';
}

async function createTransfer() {
    const from_location = document.getElementById('fromLocation').value.trim();
    const to_location = document.getElementById('toLocation').value.trim();
    const from_rack = document.getElementById('fromRack').value.trim();
    const to_rack = document.getElementById('toRack').value.trim();
    const sku = document.getElementById('transferSku').value.trim();
    const quantity = parseInt(document.getElementById('transferQty').value);
    const requested_by = 'System';

    if (!from_location || !to_location || !from_rack || !to_rack || !sku || !requested_by) {
        showToast('All fields are required', 'warning'); return;
    }
    if (!quantity || quantity < 1) {
        showToast('Quantity must be at least 1', 'warning'); return;
    }

    const params = new URLSearchParams({ from_location, to_location, from_rack, to_rack, sku, quantity, requested_by });

    const resultDiv = document.getElementById('transferResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Creating transfer...';

    try {
        const result = await fetch(`${API_URL}/stock-transfers?${params}`, { method: 'POST' });
        const json = await result.json();
        if (!result.ok) {
            const errMsg = json.detail || 'Failed to create transfer.';
            showToast(errMsg, 'error');
            resultDiv.style.color = 'red';
            resultDiv.textContent = errMsg;
            return;
        }
        showToast('Transfer created successfully', 'success');
        resultDiv.style.color = 'green';
        const statusMsg = json.status === 'Completed'
            ? `Transfer ${json.transfer_id} auto-approved. Stock of "${sku}" (qty: ${quantity}) has been moved from ${from_location}/${from_rack} to ${to_location}/${to_rack}.`
            : `Transfer ${json.transfer_id} submitted for approval (qty > 30). Stock will be moved once approved by Ops.`;
        resultDiv.textContent = statusMsg;
    } catch (error) {
        showToast('Failed to create transfer', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

async function listTransfers(forceRefresh = false) {
    const resultDiv = document.getElementById('transfersResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading transfers...';

    try {
        const url = forceRefresh ? `${API_URL}/stock-transfers?refresh=true` : `${API_URL}/stock-transfers`;
        const result = await fetch(url);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Transfer ID</th><th>SKU</th><th>Quantity</th><th>From</th><th>To</th><th>Status</th><th>Requested By</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${record.id}</td>
                    <td>${fields.sku || 'N/A'}</td>
                    <td>${fields.quantity || 0}</td>
                    <td>${fields.from_location || 'N/A'}/${fields.from_rack || 'N/A'}</td>
                    <td>${fields.to_location || 'N/A'}/${fields.to_rack || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.requested_by || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No transfers found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('transfersResult')) listTransfers();
});
