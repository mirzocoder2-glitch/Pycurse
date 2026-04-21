/**
 * ПлатформаТЈ — API Client
 * Ҳамаи дархостҳо ба Flask backend мефиристад
 */

const API_BASE = 'http://localhost:5000/api';

const api = {
  // ===== HELPERS =====
  async _req(method, path, body, isForm) {
    const opts = {
      method,
      credentials: 'include',
      headers: isForm ? {} : { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = isForm ? body : JSON.stringify(body);
    const res = await fetch(API_BASE + path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Хато: ${res.status}`);
    return data;
  },
  get:    (path)        => api._req('GET',    path),
  post:   (path, body)  => api._req('POST',   path, body),
  put:    (path, body)  => api._req('PUT',    path, body),
  del:    (path)        => api._req('DELETE', path),
  upload: (path, form)  => api._req('POST',   path, form, true),
  uploadPut: (path, form) => api._req('PUT',  path, form, true),

  // ===== AUTH =====
  auth: {
    login:  (u, p) => api.post('/auth/login', { username: u, password: p }),
    logout: ()     => api.post('/auth/logout'),
    me:     ()     => api.get('/auth/me'),
  },

  // ===== USERS =====
  users: {
    list:   ()        => api.get('/users'),
    create: (d)       => api.post('/users', d),
    update: (id, d)   => api.put(`/users/${id}`, d),
    delete: (id)      => api.del(`/users/${id}`),
  },

  // ===== COURSES =====
  courses: {
    list:   ()        => api.get('/courses'),
    create: (d)       => api.post('/courses', d),
    update: (id, d)   => api.put(`/courses/${id}`, d),
    delete: (id)      => api.del(`/courses/${id}`),
  },

  // ===== TOPICS =====
  topics: {
    list:      (courseId) => api.get('/topics' + (courseId ? `?course_id=${courseId}` : '')),
    create:    (form)     => api.upload('/topics', form),
    update:    (id, form) => api.uploadPut(`/topics/${id}`, form),
    delete:    (id)       => api.del(`/topics/${id}`),
    videoUrl:  (id)       => `${API_BASE}/topics/${id}/video`,
  },

  // ===== TESTS =====
  tests: {
    list:   (courseId) => api.get('/tests' + (courseId ? `?course_id=${courseId}` : '')),
    create: (d)        => api.post('/tests', d),
    update: (id, d)    => api.put(`/tests/${id}`, d),
    delete: (id)       => api.del(`/tests/${id}`),
    submit: (id, ans)  => api.post(`/tests/${id}/submit`, { answers: ans }),
  },

  // ===== TASKS =====
  tasks: {
    list:   (courseId) => api.get('/tasks' + (courseId ? `?course_id=${courseId}` : '')),
    create: (d)        => api.post('/tasks', d),
    update: (id, d)    => api.put(`/tasks/${id}`, d),
    delete: (id)       => api.del(`/tasks/${id}`),
  },

  // ===== RESULTS =====
  results: {
    my:  ()     => api.get('/results'),
    all: ()     => api.get('/results/all'),
  },

  // ===== LEADERBOARD =====
  leaderboard: () => api.get('/leaderboard'),

  // ===== CHAT =====
  chat: {
    rooms:    ()            => api.get('/chat/rooms'),
    messages: (roomId, n)   => api.get(`/chat/${roomId}/messages?limit=${n||50}`),
    send:     (roomId, txt) => api.post(`/chat/${roomId}/send`, { text: txt }),
  },

  // ===== SCHEDULE =====
  schedule: {
    list:   ()    => api.get('/schedule'),
    create: (d)   => api.post('/schedule', d),
    delete: (id)  => api.del(`/schedule/${id}`),
  },

  // ===== NOTIFICATIONS =====
  notifications: {
    list:      ()    => api.get('/notifications'),
    markRead:  ()    => api.post('/notifications/read'),
    broadcast: (d)   => api.post('/notifications/broadcast', d),
  },

  // ===== ANALYTICS =====
  analytics: () => api.get('/analytics'),
};


// ===== SESSION MANAGER =====
const Session = {
  _user: null,

  async init() {
    try {
      this._user = await api.auth.me();
    } catch {
      this._user = null;
    }
    return this._user;
  },

  get user()    { return this._user; },
  get isAdmin() { return this._user?.role === 'admin'; },
  get isAuth()  { return !!this._user; },

  async login(username, password) {
    const res  = await api.auth.login(username, password);
    this._user = res.user;
    return res;
  },

  async logout() {
    await api.auth.logout();
    this._user = null;
    window.location.href = 'login.html';
  },

  requireAuth(role) {
    if (!this.isAuth) {
      window.location.href = 'login.html';
      return false;
    }
    if (role && this._user.role !== role) {
      window.location.href = 'index.html';
      return false;
    }
    return true;
  },
};


// ===== THEME =====
const Theme = {
  init() {
    if (localStorage.getItem('theme') === 'light') document.body.classList.add('light');
  },
  toggle() {
    document.body.classList.toggle('light');
    localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
  },
};


// ===== UTILS =====
const Utils = {
  escapeHtml(s) {
    return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  },
  formatDate(s) {
    if (!s) return '—';
    return new Date(s).toLocaleDateString('ru-RU');
  },
  timeAgo(s) {
    const d = (Date.now() - new Date(s)) / 1000;
    if (d < 60)   return 'Ҳозир';
    if (d < 3600) return `${Math.floor(d/60)} дақ`;
    if (d < 86400)return `${Math.floor(d/3600)} соат`;
    return new Date(s).toLocaleDateString('ru-RU');
  },
  levelBadge(l) {
    const m = { 'Ибтидоӣ':'badge-success','Миёна':'badge-warning','Мураккаб':'badge-danger' };
    return `<span class="badge ${m[l]||'badge-primary'}">${l}</span>`;
  },
  diffBadge(d) {
    const cm = { easy:'badge-success',medium:'badge-warning',hard:'badge-danger' };
    const lm = { easy:'Осон',medium:'Миёна',hard:'Мушкил' };
    return `<span class="badge ${cm[d]||'badge-primary'}">${lm[d]||d}</span>`;
  },
  showToast(msg, type='success') {
    const t = document.createElement('div');
    const colors = { success:'var(--success)', danger:'var(--danger)', info:'var(--primary)' };
    t.style.cssText = `position:fixed;bottom:24px;right:24px;z-index:9999;background:var(--card);border:1px solid ${colors[type]||colors.success};color:var(--text);padding:12px 20px;border-radius:10px;font-size:0.9rem;box-shadow:0 8px 24px rgba(0,0,0,0.3);animation:fadeUp 0.3s ease;max-width:320px`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  },
};


// ===== NOTIFICATION WIDGET =====
const NotifWidget = {
  async init(userId) {
    this.userId = userId;
    await this.update();
    setInterval(() => this.update(), 15000);
    document.addEventListener('click', e => {
      const bell = document.getElementById('notif-bell-wrap');
      if (bell && !bell.contains(e.target)) {
        document.getElementById('notif-dropdown')?.classList.remove('open');
      }
    });
  },

  async update() {
    try {
      const notifs = await api.notifications.list();
      const unread = notifs.filter(n => !n.is_read).length;
      const badge  = document.getElementById('notif-count');
      if (badge) { badge.textContent = unread; badge.style.display = unread ? '' : 'none'; }
    } catch {}
  },

  async toggle() {
    const dd = document.getElementById('notif-dropdown');
    if (!dd) return;
    dd.classList.toggle('open');
    if (dd.classList.contains('open')) await this.render();
  },

  async render() {
    const dd = document.getElementById('notif-dropdown');
    if (!dd) return;
    try {
      const notifs = await api.notifications.list();
      dd.innerHTML = `
        <div class="notif-header">
          <strong>🔔 Огоҳномаҳо</strong>
          <button onclick="NotifWidget.markAll()" style="background:none;border:none;color:var(--primary);cursor:pointer;font-size:0.8rem">Ҳама хонда</button>
        </div>
        ${notifs.length ? notifs.slice(0,15).map(n => `
          <div class="notif-item ${n.is_read?'read':'unread'}">
            <div class="notif-icon">${n.icon}</div>
            <div class="notif-text">
              <div>${Utils.escapeHtml(n.message)}</div>
              <div class="notif-time">${Utils.timeAgo(n.created_at)}</div>
            </div>
          </div>`).join('') : '<div class="notif-empty">Огоҳнома нест 🎉</div>'}`;
    } catch { dd.innerHTML = '<div class="notif-empty">Хато рӯй дод</div>'; }
  },

  async markAll() {
    await api.notifications.markAll?.() || api.notifications.markRead();
    await this.update();
    await this.render();
  },
};

// Auto-init theme
document.addEventListener('DOMContentLoaded', () => Theme.init());
