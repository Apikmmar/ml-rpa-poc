async function listStocks() {
    const resultDiv = document.getElementById('stocksResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading stocks...';

    try {
        const result = await fetch(`${API_URL}/stocks`);
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

async function receiveGoods() {
    const sku = document.getElementById('goodsSku').value;
    const quantity = document.getElementById('goodsQty').value;
    const location = document.getElementById('goodsLocation').value;
    const rack = document.getElementById('goodsRack').value;
    const received_by = document.getElementById('receivedBy').value;
    
    if (!sku || !quantity || !location || !rack) {
        alert('Please fill in all required fields');
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
            const errorText = await result.text();
            throw new Error(`HTTP ${result.status}: ${errorText}`);
        }
        
        const json = await result.json();
        resultDiv.textContent = JSON.stringify(json, null, 2);
        resultDiv.style.color = 'green';
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
        resultDiv.style.color = 'red';
        console.error('Receive goods error:', error);
    }
}

async function listGoodsReceipts() {
    const resultDiv = document.getElementById('receiptsResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading goods receipts...';

    try {
        const result = await fetch(`${API_URL}/stocks/goods-receipts`);
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
