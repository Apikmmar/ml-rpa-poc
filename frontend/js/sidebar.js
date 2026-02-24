const NAV_LINKS = [
    { href: '/index',                        label: 'Dashboard',            icon: 'bi-speedometer2' },
    { group: 'Orders' },
    { href: '/orders/list',                  label: 'All Orders',           icon: 'bi-bag' },
    { href: '/orders',                       label: 'Create Order',         icon: 'bi-plus-circle' },
    { href: '/upload',                       label: 'Upload Orders',           icon: 'bi-cloud-upload' },
    { href: '/orders/update',                label: 'Update Orders',        icon: 'bi-pencil' },
    { group: 'Stocks' },
    { href: '/stocks',                       label: 'All Stocks',           icon: 'bi-box-seam' },
    { href: '/stocks/receipt',               label: 'Goods Receipt',        icon: 'bi-box-arrow-in-down' },
    { href: '/stocks/history',               label: 'Receipt History',      icon: 'bi-clock-history' },
    { group: 'Picklists' },
    { href: '/picklists',                    label: 'All Picklists',        icon: 'bi-list-check' },
    { href: '/picklists/update',             label: 'Update Picklists',        icon: 'bi-pencil-square' },
    { href: '/picklists/route',              label: 'Optimize Route',       icon: 'bi-map' },
    { group: 'Transfers' },
    { href: '/transfers/list',               label: 'All Transfers',        icon: 'bi-list-ul' },
    { href: '/transfers',                    label: 'Create Transfer',      icon: 'bi-arrow-left-right' },
    { group: 'Reports' },
    { href: '/reports',                      label: 'All Reports',          icon: 'bi-bar-chart' },
    { href: '/reports/reconciliation',       label: 'Reconciliation',       icon: 'bi-file-earmark-bar-graph' },
    { href: '/reports/daily',                label: 'Daily Summary',        icon: 'bi-calendar-day' },
    { href: '/reports/weekly',               label: 'Weekly Summary',       icon: 'bi-calendar-week' },
    { group: 'Monitoring' },
    { href: '/monitoring',                   label: 'Metrics',              icon: 'bi-graph-up' },
    { href: '/monitoring/exceptions',        label: 'Exceptions',           icon: 'bi-exclamation-triangle' },
    { href: '/monitoring/audit',             label: 'Audit Logs',           icon: 'bi-journal-text' },
    { href: '/monitoring/backorders',        label: 'Backorders',           icon: 'bi-hourglass-split' },
    { href: '/monitoring/notifications',     label: 'Notifications',        icon: 'bi-bell' },
];

const parts = location.pathname.replace('.html', '').split('/').filter(Boolean);
const currentPage = parts.length >= 2 ? '/' + parts.slice(-2).join('/') : '/' + (parts[0] || 'index');
const nav = document.createElement('nav');
nav.className = 'sidebar-nav';
nav.innerHTML = NAV_LINKS.map(item => {
    if (item.group) return `<div class="sidebar-group">${item.group}</div>`;
    return `<a href="${item.href}" class="sidebar-link${item.href === currentPage ? ' active' : ''}">
        <i class="bi ${item.icon}"></i>
        <span class="sidebar-label">${item.label}</span>
    </a>`;
}).join('');

const sidebarHTML = `
<div id="sidebar">
  <div class="sidebar-brand">
    <i class="bi bi-robot"></i>
    <span class="sidebar-label">RPA System</span>
  </div>
  <div class="sidebar-scroll"></div>
  <button id="sidebarToggle" onclick="toggleSidebar()" title="Toggle sidebar">
    <i class="bi bi-chevron-left" id="toggleIcon"></i>
  </button>
</div>
<div id="mainContent">`;

document.write(sidebarHTML);

document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.sidebar-scroll').appendChild(nav);
});

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const icon = document.getElementById('toggleIcon');
    sidebar.classList.toggle('collapsed');
    icon.className = sidebar.classList.contains('collapsed') ? 'bi bi-chevron-right' : 'bi bi-chevron-left';
}
