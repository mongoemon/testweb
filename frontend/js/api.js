const API_BASE = '/api';

const api = {
  async request(method, endpoint, data = null, requireAuth = true) {
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('token');
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const opts = { method, headers };
    if (data !== null) opts.body = JSON.stringify(data);

    const res = await fetch(`${API_BASE}${endpoint}`, opts);

    if (res.status === 401 && requireAuth) {
      auth.logout();
      window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
      return null;
    }

    const body = await res.json().catch(() => ({ detail: 'Unknown error' }));
    if (!res.ok) throw { status: res.status, detail: body.detail || 'Request failed' };
    return body;
  },

  get:    (ep, auth = true)       => api.request('GET',    ep, null, auth),
  post:   (ep, data, auth = true) => api.request('POST',   ep, data, auth),
  put:    (ep, data, auth = true) => api.request('PUT',    ep, data, auth),
  delete: (ep, auth = true)       => api.request('DELETE', ep, null, auth),

  // Auth
  login:          (d) => api.post('/auth/login',    d, false),
  register:       (d) => api.post('/auth/register', d, false),
  me:             ()  => api.get('/auth/me'),
  updateProfile:  (d) => api.put('/auth/profile',  d),
  updatePassword: (d) => api.put('/auth/password',  d),
  updateAddress:  (d) => api.put('/auth/address',   d),

  // Products
  getProducts: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '' && v != null))
    ).toString();
    return api.get(`/products${qs ? '?' + qs : ''}`, false);
  },
  getProduct:    (id)       => api.get(`/products/${id}`, false),
  createProduct: (d)        => api.post('/products', d),
  updateProduct: (id, d)    => api.put(`/products/${id}`, d),
  deleteProduct: (id)       => api.delete(`/products/${id}`),
  getCategories: ()         => api.get('/categories', false),

  // Cart
  getCart:        ()       => api.get('/cart'),
  addToCart:      (d)      => api.post('/cart', d),
  updateCartItem: (id, d)  => api.put(`/cart/${id}`, d),
  removeCartItem: (id)     => api.delete(`/cart/${id}`),
  clearCart:      ()       => api.delete('/cart/clear'),

  // Orders
  getOrders:  ()       => api.get('/orders'),
  getOrder:   (id)     => api.get(`/orders/${id}`),
  placeOrder: (d)      => api.post('/orders', d),

  // Admin
  getAdminStats:       ()       => api.get('/admin/stats'),
  getAdminOrders:      (status) => api.get(`/admin/orders${status ? '?status=' + status : ''}`),
  updateOrderStatus:   (id, s)  => api.put(`/admin/orders/${id}/status`, { status: s }),
  getAdminUsers:       ()       => api.get('/admin/users'),

  // Discount codes
  validateDiscount:         (code)     => api.post('/discount-codes/validate', { code }),
  getAdminDiscountCodes:    ()         => api.get('/admin/discount-codes'),
  createAdminDiscountCode:  (d)        => api.post('/admin/discount-codes', d),
  updateAdminDiscountCode:  (id, d)    => api.put(`/admin/discount-codes/${id}`, d),
  deleteAdminDiscountCode:  (id)       => api.delete(`/admin/discount-codes/${id}`),
};
