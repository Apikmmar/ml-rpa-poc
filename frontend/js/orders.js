function addItem() {
    const container = document.getElementById('itemsContainer');
    const row = document.createElement('div');
    row.className = 'item-row';
    row.innerHTML = '<input type="text" placeholder="SKU" class="item-sku"><input type="number" placeholder="Qty" class="item-qty" min="1"><button class="btn-outline" onclick="removeItem(this)" type="button"><i class="bi bi-trash"></i></button>';
    container.appendChild(row);
}

function removeItem(button) {
    const container = document.getElementById('itemsContainer');
    if (container.children.length > 1) {
        button.parentElement.remove();
    } else {
        const row = button.parentElement;
        row.querySelector('.item-sku').value = '';
        row.querySelector('.item-qty').value = '';
    }
}

function clearForm() {
    document.getElementById('customerEmail').value = '';
    document.getElementById('priority').value = '';
    document.getElementById('itemsContainer').innerHTML = '<div class="item-row"><input type="text" placeholder="SKU" class="item-sku"><input type="number" placeholder="Qty" class="item-qty" min="1"><button class="btn-outline" onclick="removeItem(this)" type="button"><i class="bi bi-trash"></i></button></div>';
    const resultDiv = document.getElementById('orderResult');
    resultDiv.textContent = '';
    resultDiv.style.color = '';
}

async function createOrder() {
    const customerEmail = document.getElementById('customerEmail');
    const priority = document.getElementById('priority');

    if (!customerEmail.value.trim()) {
        showToast('Please enter Customer Email', 'warning');
        return;
    }
    
    const items = [];
    let itemError = false;
    document.querySelectorAll('.item-row').forEach(row => {
        const sku = row.querySelector('.item-sku').value.trim();
        const qty = parseInt(row.querySelector('.item-qty').value);
        if (sku && qty > 0) items.push({ sku, qty });
        else if (sku || qty) itemError = true;
    });

    if (itemError) { showToast('Each item must have both SKU and Quantity > 0', 'warning'); return; }
    if (items.length === 0) { showToast('Please add at least one item', 'warning'); return; }

    const data = {
        customer_email: customerEmail.value,
        customer_id: `CUST-${Date.now()}`,
        priority: priority.value,
        items
    };

    const resultDiv = document.getElementById('orderResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Creating order...';

    try {
        const result = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!result.ok) {
            const errorText = await result.text();
            throw new Error(`HTTP ${result.status}: ${errorText}`);
        }
        
        const json = await result.json();
        showToast('Order created successfully', 'success');
        resultDiv.textContent = `Order ${json.order_id} has been created successfully. Validation is now in progress.`;
        resultDiv.style.color = 'green';
    } catch (error) {
        showToast('Failed to create order', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
        resultDiv.style.color = 'red';
        console.error('Create order error:', error);
    }
}

async function listOrders(forceRefresh = false) {
    const resultDiv = document.getElementById('ordersResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading orders...';

    try {
        const url = forceRefresh ? `${API_URL}/orders?refresh=true` : `${API_URL}/orders`;
        const result = await fetch(url);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Order ID</th><th>Customer Email</th><th>Priority</th><th>Status</th><th>Created</th></tr></thead><tbody>';
            json.records.forEach(record => {
                const fields = record.fields;
                table += `<tr>
                    <td>${record.id}</td>
                    <td>${fields.customer_email || 'N/A'}</td>
                    <td>${fields.priority || 'N/A'}</td>
                    <td>${fields.status || 'N/A'}</td>
                    <td>${fields.created_at ? new Date(fields.created_at).toLocaleString() : 'N/A'}</td>
                </tr>`;
            });
            table += '</tbody></table>';
            resultDiv.innerHTML = table;
        } else {
            resultDiv.textContent = 'No orders found';
        }
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('ordersResult')) listOrders();
});

function clearUpdateForm() {
    document.getElementById('updateOrderId').value = '';
    document.getElementById('updateStatus').value = '';
    document.getElementById('updateEta').value = '';
    const resultDiv = document.getElementById('updateOrderResult');
    resultDiv.textContent = '';
}

async function updateOrderStatus() {
    const orderId = document.getElementById('updateOrderId').value.trim();
    const status = document.getElementById('updateStatus').value;
    const eta = document.getElementById('updateEta').value;
    const etaRequiredStatuses = ['Picking', 'Ready', 'Shipped'];
    if (!orderId) { showToast('Please enter an Order ID', 'warning'); return; }
    if (!status) { showToast('Please select a Status', 'warning'); return; }
    if (etaRequiredStatuses.includes(status) && !eta) { showToast('ETA is required for ' + status, 'warning'); return; }

    const resultDiv = document.getElementById('updateOrderResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Updating status...';

    try {
        const body = { status };
        if (eta) body.eta = eta;
        const result = await fetch(`${API_URL}/orders/${orderId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const json = await result.json();
        if (!result.ok) {
            const errCode = json.detail ? (typeof json.detail === 'string' ? JSON.parse(json.detail)?.error : json.detail) : null;
            const errMsg = errCode === 'NOT_FOUND' ? `Order "${orderId}" not found. Please check the Order ID and try again.` : (errCode || 'Failed to update order status.');
            showToast(errMsg, 'error');
            resultDiv.style.color = 'red';
            resultDiv.textContent = errMsg;
            return;
        }
        showToast('Order status updated', 'success');
        resultDiv.style.color = 'green';
        const etaDisplay = json.eta ? new Date(json.eta).toLocaleString() : 'N/A';
        resultDiv.textContent = `Order ${json.order_id} has been updated to "${json.status}"${json.eta ? ` with ETA ${etaDisplay}` : ''}.`;
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}
