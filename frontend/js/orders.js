function addItem() {
    const container = document.getElementById('itemsContainer');
    const row = document.createElement('div');
    row.className = 'item-row';
    row.innerHTML = '<input type="text" placeholder="SKU" class="item-sku"><input type="number" placeholder="Quantity" class="item-qty" min="1"><button onclick="removeItem(this)" type="button">Remove</button>';
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
    document.getElementById('customerId').value = '';
    document.getElementById('priority').value = 'Normal';
    document.getElementById('itemsContainer').innerHTML = '<div class="item-row"><input type="text" placeholder="SKU" class="item-sku"><input type="number" placeholder="Quantity" class="item-qty" min="1"><button onclick="removeItem(this)" type="button">Remove</button></div>';
    document.getElementById('orderResult').style.display = 'none';
}

async function createOrder() {
    const customerEmail = document.getElementById('customerEmail');
    const customerId = document.getElementById('customerId');
    const priority = document.getElementById('priority');
    
    if (!customerEmail || !customerId || !priority) {
        alert('Form elements not found. Please refresh the page (Ctrl+Shift+R)');
        return;
    }
    
    if (!customerEmail.value.trim()) {
        alert('Please enter Customer Email');
        return;
    }
    
    if (!customerId.value.trim()) {
        alert('Please enter Customer ID');
        return;
    }
    
    const items = [];
    document.querySelectorAll('.item-row').forEach(row => {
        const sku = row.querySelector('.item-sku').value;
        const qty = parseInt(row.querySelector('.item-qty').value);
        if (sku && qty) items.push({ sku, qty });
    });
    
    if (items.length === 0) {
        alert('Please add at least one item with SKU and Quantity');
        return;
    }

    const data = {
        customer_email: customerEmail.value,
        customer_id: customerId.value,
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
        resultDiv.textContent = JSON.stringify(json, null, 2);
        resultDiv.style.color = 'green';
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
        resultDiv.style.color = 'red';
        console.error('Create order error:', error);
    }
}

async function listOrders() {
    const resultDiv = document.getElementById('ordersResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Loading orders...';

    try {
        const result = await fetch(`${API_URL}/orders`);
        const json = await result.json();
        
        if (json.records && json.records.length > 0) {
            let table = '<table><thead><tr><th>Record ID</th><th>Customer Email</th><th>Priority</th><th>Status</th><th>Created</th></tr></thead><tbody>';
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

async function updateOrderStatus() {
    const orderId = document.getElementById('updateOrderId').value;
    const status = document.getElementById('updateStatus').value;

    const resultDiv = document.getElementById('updateOrderResult');
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Updating status...';

    try {
        const result = await fetch(`${API_URL}/orders/${orderId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        const json = await result.json();
        resultDiv.textContent = JSON.stringify(json, null, 2);
    } catch (error) {
        resultDiv.textContent = 'Error: ' + error.message;
    }
}
