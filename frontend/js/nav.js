async function renderNav() {
  const user = auth.getUser();
  const isAdmin = user && user.is_admin;
  const path = window.location.pathname;

  let cartBadge = '';
  if (auth.isLoggedIn()) {
    try {
      const cart = await api.getCart();
      const count = cart.count || 0;
      if (count > 0) cartBadge = `<span data-testid="cart-count" class="absolute -top-1 -right-2 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">${count}</span>`;
      else cartBadge = `<span data-testid="cart-count" class="hidden">0</span>`;
    } catch { cartBadge = `<span data-testid="cart-count" class="hidden">0</span>`; }
  }

  const links = [
    { href: '/',              label: i18n.t('nav.home'),     testid: 'nav-home' },
    { href: '/products.html', label: i18n.t('nav.products'), testid: 'nav-products' },
  ];

  const linksHtml = links.map(l =>
    `<a href="${l.href}" data-testid="${l.testid}"
        class="transition-colors ${path === l.href ? 'nav-active' : ''}"
      >${l.label}</a>`
  ).join('');

  const authHtml = user
    ? `<a href="/cart.html" data-testid="nav-cart" class="relative transition-colors">
         🛒 ${i18n.t('nav.cart')}${cartBadge}
       </a>
       <a href="/orders.html" data-testid="nav-orders" class="transition-colors">📦 ${i18n.t('nav.orders')}</a>
       ${isAdmin ? `<a href="/admin/index.html" data-testid="nav-admin" class="transition-colors">⚙️ ${i18n.t('nav.admin')}</a>` : ''}
       <div class="relative" id="user-menu-wrap">
         <button onclick="_toggleUserMenu(event)" data-testid="nav-user-menu" class="transition-colors px-1">
           👤 ${user.username} ▾
         </button>
         <div id="user-menu" class="absolute right-0 top-full mt-1 bg-white text-gray-800 rounded shadow-lg py-1 min-w-max hidden z-50">
           <div class="px-4 py-2 text-sm text-gray-500 border-b">${user.email}</div>
           <a href="/profile.html" data-testid="nav-profile"
             class="block px-4 py-2 text-sm hover:bg-gray-100">👤 ${i18n.t('nav.profile')}</a>
           <button onclick="handleLogout()" data-testid="nav-logout"
             class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100">${i18n.t('nav.logout')}</button>
         </div>
       </div>`
    : `<a href="/login.html"    data-testid="nav-login"    class="transition-colors">${i18n.t('nav.login')}</a>
       <a href="/register.html" data-testid="nav-register" class="px-4 py-1.5 rounded-full font-semibold transition-colors">${i18n.t('nav.register')}</a>`;

  const nav = `
    <nav data-testid="navbar" class="shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <a href="/" data-testid="nav-logo" class="flex items-center gap-2 text-xl font-bold tracking-tight">
            👟 ShoesHub
          </a>
          <div class="hidden md:flex items-center gap-6 text-sm">${linksHtml}</div>
          <div class="flex items-center gap-4 text-sm">
            ${authHtml}
            ${i18n.renderSwitcher()}
            <button id="theme-toggle-btn" onclick="theme.toggle()" title="Switch theme"
                    class="text-base leading-none opacity-70 hover:opacity-100 transition-opacity">
            </button>
          </div>
          <button id="mobile-menu-btn" class="md:hidden" aria-label="Toggle menu">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        </div>
        <div id="mobile-menu" class="md:hidden hidden pb-3 flex flex-col gap-2 text-sm">
          ${linksHtml.replace(/class="/g, 'class="block py-1 ')}
        </div>
      </div>
    </nav>`;

  const existing = document.querySelector('[data-testid="navbar"]');
  if (existing) {
    existing.outerHTML = nav;
  } else {
    const placeholder = document.getElementById('nav-placeholder');
    if (placeholder) {
      placeholder.outerHTML = nav;
    } else {
      document.body.insertAdjacentHTML('afterbegin', nav);
    }
  }

  document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {
    document.getElementById('mobile-menu')?.classList.toggle('hidden');
  });

  // Set theme toggle icon after render
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) {
    const isOriginal = theme.current() === 'original';
    btn.textContent = isOriginal ? '🔵' : '🟡';
    btn.title = isOriginal ? 'Switch to Minimal' : 'Switch to Original';
  }
}

function _toggleLangMenu(e) {
  e.stopPropagation();
  document.getElementById('user-menu')?.classList.add('hidden');
  document.getElementById('lang-menu')?.classList.toggle('hidden');
}

function _toggleUserMenu(e) {
  e.stopPropagation();
  document.getElementById('lang-menu')?.classList.add('hidden');
  document.getElementById('user-menu')?.classList.toggle('hidden');
}

document.addEventListener('click', () => {
  document.getElementById('lang-menu')?.classList.add('hidden');
  document.getElementById('user-menu')?.classList.add('hidden');
});

function handleLogout() {
  auth.logout();
  window.location.href = '/';
}

function showToast(message, type = 'success') {
  const existing = document.getElementById('toast');
  if (existing) existing.remove();
  const colors = { success: 'bg-green-600', error: 'bg-red-600', info: 'bg-blue-600', warning: 'bg-yellow-500 text-gray-900' };
  const toast = document.createElement('div');
  toast.id = 'toast';
  toast.setAttribute('data-testid', 'toast');
  toast.setAttribute('data-type', type);
  toast.className = `fixed bottom-6 right-6 ${colors[type] || colors.info} text-white px-5 py-3 rounded-lg shadow-xl z-50 text-sm font-medium transition-all`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function formatPrice(price) {
  return '฿' + Number(price).toLocaleString('th-TH', { minimumFractionDigits: 0 });
}

function formatDate(dateStr) {
  const locale = i18n.current === 'en' ? 'en-US' : 'th-TH';
  return new Date(dateStr).toLocaleDateString(locale, { year: 'numeric', month: 'long', day: 'numeric' });
}

function getStatusLabel(status) {
  return i18n.t(`status.${status}`) || status;
}

function getStatusClass(status) {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800', confirmed: 'bg-blue-100 text-blue-800',
    processing: 'bg-purple-100 text-purple-800', shipped: 'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800', cancelled: 'bg-red-100 text-red-800',
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
}
