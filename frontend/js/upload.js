const LAMBDA_URL = 'https://v9dp2292j8.execute-api.ap-southeast-1.amazonaws.com/prod';

async function uploadCSV() {
    const file = document.getElementById('csvFile').files[0];
    const resultDiv = document.getElementById('uploadResult');

    if (!file) {
        showToast('Please select a CSV file', 'warning');
        return;
    }

    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Getting upload URL...';

    try {
        const presignResp = await fetch(`${LAMBDA_URL}/upload-url?filename=${encodeURIComponent(file.name)}`);
        const { url } = await presignResp.json();

        resultDiv.textContent = 'Uploading to S3...';
        const uploadResp = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'text/csv' },
            body: file
        });

        if (uploadResp.ok) {
            showToast(`Uploaded ${file.name} successfully`, 'success');
            resultDiv.textContent = `Uploaded ${file.name} - order processing triggered automatically.`;
            resultDiv.style.color = 'green';
        } else {
            throw new Error(`Upload failed: ${uploadResp.status}`);
        }
    } catch (error) {
        showToast('Upload failed', 'error');
        resultDiv.textContent = 'Error: ' + error.message;
        resultDiv.style.color = 'red';
    }
}

function downloadSample() {
    const csv = 'customer_email,customer_id,priority,sku,qty\njohn@example.com,CUST-001,Normal,SKU-001,5\njohn@example.com,CUST-001,Normal,SKU-002,3\njane@example.com,CUST-002,High,SKU-003,10';
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'sample_orders.csv';
    a.click();
}
