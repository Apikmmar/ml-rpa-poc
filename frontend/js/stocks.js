async function listStocks(forceRefresh = false) {
    const resultDiv = document.getElementById('stocksResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading stocks...';

    try {
        const url = forceRefresh ? `${API_URL}/stocks?refresh=true` : `${API_URL}/stocks`;
        const result = await fetch(url);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>SKU</th><th>Quantity</th><th>Reserved</th><th>Available</th><th>Location</th><th>Rack</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${fields.sku || 'N/A'}</td>
                    <td>${fields.quantity || 0}</td>
                    <td>${fields.reserved || 0}</td>
                    <td>${fields.available || 0}</td>
                    <td>${fields.location || 'N/A'}</td>
                    <td>${fields.rack || 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No stocks found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('stocksResult')) listStocks();
    if (document.getElementById('receiptsResult')) listGoodsReceipts();
});

function clearGoodsForm() {
    document.getElementById('goodsSku').value = '';
    document.getElementById('goodsQty').value = '';
    document.getElementById('goodsLocation').value = '';
    document.getElementById('goodsRack').value = '';
    const resultDiv = document.getElementById('goodsResult');
    resultDiv.textContent = '';
    resultDiv.style.color = '';
}

async function receiveGoods() {
    const sku = document.getElementById('goodsSku').value;
    const quantity = document.getElementById('goodsQty').value;
    const location = document.getElementById('goodsLocation').value;
    const rack = document.getElementById('goodsRack').value;
    const received_by = 'System';
    
    if (!sku || !quantity || !location || !rack) {
        showToast('SKU, Quantity, Location and Rack are required', 'warning');
        return;
    }
    if (parseInt(quantity) < 1) {
        showToast('Quantity must be at least 1', 'warning');
        return;
    }
    
    const params = new URLSearchParams({
        sku: sku,
        quantity: quantity,
        location: location,
        rack: rack,
        received_by: received_by
    });

    const resultDiv = document.getElementById('goodsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Processing goods receipt...';

    try {
        const result = await fetch(`${API_URL}/stocks/goods-receipt?${params}`, { method: 'POST' });
        
        if (!result.ok) {
            const json = await result.json();
            const errMsg = result.status === 404 ? `SKU "${sku}" not found in inventory. Please check the SKU and try again.` : (json.detail || 'Failed to receive goods.');
            showToast(errMsg, 'error');
            resultDiv.textContent = errMsg;
            resultDiv.style.color = 'red';
            return;
        }
        
        const json = await result.json();
        showToast('Goods received successfully', 'success');
        resultDiv.textContent = `${json.quantity} unit(s) of "${json.sku}" received at ${json.location} / ${json.rack}. Receipt ID: ${json.receipt_id}.`;
        resultDiv.style.color = 'green';
    } catch (error) {
        showToast('Failed to receive goods', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
        resultDiv.style.color = 'red';
        console.error('Receive goods error:', error);
    }
}

async function listGoodsReceipts(forceRefresh = false) {
    const resultDiv = document.getElementById('receiptsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading goods receipts...';

    try {
        const url = forceRefresh ? `${API_URL}/stocks/goods-receipts?refresh=true` : `${API_URL}/stocks/goods-receipts`;
        const result = await fetch(url);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>SKU</th><th>Quantity</th><th>Location</th><th>Rack</th><th>Received By</th><th>Status</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${fields.sku || 'N/A'}</td>
                    <td>${fields.quantity || 0}</td>
                    <td>${fields.location || 'N/A'}</td>
                    <td>${fields.rack || 'N/A'}</td>
                    <td>${fields.received_by || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No goods receipts found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}
