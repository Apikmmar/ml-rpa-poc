const API_URL = 'http://localhost:8000';

function showToast(message, type = 'success', duration = 3000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    const icons = { success: '\u2713', error: '\u2715', warning: '\u26a0' };
    toast.className = `rpa-toast rpa-toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}
