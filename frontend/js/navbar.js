const NAV_LINKS = [
    { href: '/index', label: 'Home' },
    { href: '/orders', label: 'Orders' },
    { href: '/upload', label: 'Upload Orders' },
    { href: '/picklists', label: 'Picklists' },
    { href: '/stocks', label: 'Stocks' },
    { href: '/transfers', label: 'Transfers' },
    { href: '/reports', label: 'Reports' },
    { href: '/monitoring', label: 'Monitoring' },
];

const currentPage = '/' + location.pathname.split('/').pop().replace('.html', '');
const nav = document.createElement('nav');
nav.innerHTML = NAV_LINKS.map(({ href, label }) =>
    `<a href="${href}"${href === currentPage ? ' class="active"' : ''}>${label}</a>`
).join('');
document.currentScript.replaceWith(nav);
