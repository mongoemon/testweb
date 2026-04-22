const auth = {
  getUser()  { try { return JSON.parse(localStorage.getItem('user')); } catch { return null; } },
  getToken() { return localStorage.getItem('token'); },
  isLoggedIn() { return !!this.getToken(); },
  isAdmin()  { const u = this.getUser(); return u && u.is_admin; },

  save(data) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
  },

  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  requireLogin() {
    if (!this.isLoggedIn()) {
      window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
      return false;
    }
    return true;
  },

  requireAdmin() {
    if (!this.isLoggedIn() || !this.isAdmin()) {
      window.location.href = '/login.html';
      return false;
    }
    return true;
  },

  redirectIfLoggedIn(dest = '/') {
    if (this.isLoggedIn()) window.location.href = dest;
  },
};
