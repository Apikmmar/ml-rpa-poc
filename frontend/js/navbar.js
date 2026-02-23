const NAV_LINKS = [
    { href: 'index.html', label: 'Home' },
    { href: 'orders.html', label: 'Orders' },
    { href: 'picklists.html', label: 'Picklists' },
    { href: 'stocks.html', label: 'Stocks' },
    { href: 'transfers.html', label: 'Transfers' },
    { href: 'reports.html', label: 'Reports' },
    { href: 'monitoring.html', label: 'Monitoring' },
    { href: 'upload.html', label: 'Upload CSV' },
];

const currentPage = location.pathname.split('/').pop();
const nav = document.createElement('nav');
nav.innerHTML = NAV_LINKS.map(({ href, label }) =>
    `<a href="${href}"${href === currentPage ? ' class="active"' : ''}>${label}</a>`
).join('');
document.currentScript.replaceWith(nav);
