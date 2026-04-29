/* ── CONFIG ───────────────────────────── */
const API_CONFIG = {
  baseUrl: '/api',
  telegramId: null
};

/* ── TELEGRAM INIT ───────────────────── */
function initTelegram() {
  if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp;
    tg.ready();
    API_CONFIG.telegramId = tg.initDataUnsafe?.user?.id?.toString() || null;
    console.log('Telegram ID:', API_CONFIG.telegramId);
  } else {
    console.warn('Telegram WebApp not found. Using test ID.');
    API_CONFIG.telegramId = '123456789';
  }
}

/* ── API HEADERS ─────────────────────── */
function apiHeaders(extra = {}) {
  return {
    'Content-Type': 'application/json',
    'Telegram-Id': API_CONFIG.telegramId,
    ...extra
  };
}

/* ── NAV ACTIVE ──────────────────────── */
(function () {
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-item').forEach(el => {
    if (el.getAttribute('href') === page) el.classList.add('active');
  });
})();

/* ── CHAT BUBBLE ─────────────────────── */
function appendBubble(text, role) {
  const area = document.getElementById('chat-messages');
  if (!area) return null;
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble bubble-${role}`;
  bubble.textContent = text;
  area.appendChild(bubble);
  bubble.scrollIntoView({ behavior: 'smooth' });
  return bubble;
}

/* ── SEND MESSAGE ────────────────────── */
async function addMessage(text) {
  appendBubble(text, 'user');
  const loadingBubble = appendBubble('Анализирую...', 'ai');
  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/ai/sendmessage`, {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ text })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    loadingBubble.textContent = data.text;
  } catch (error) {
    console.error('Send message error:', error);
    loadingBubble.textContent = 'Ошибка соединения с сервером.';
  }
}

/* ── LOAD CHAT HISTORY ───────────────── */
async function loadChatHistory() {
  const area = document.getElementById('chat-messages');
  if (!area) return;
  try {
    const res = await fetch(`${API_CONFIG.baseUrl}/ai/chat/history?last_n_messages=20`, {
      headers: apiHeaders()
    });
    if (!res.ok) return;
    const messages = await res.json();
    if (messages.length > 0) {
      area.innerHTML = '';
      messages.forEach(msg => {
        const role = msg.role === 'user' ? 'user' : 'ai';
        appendBubble(msg.text, role);
      });
    }
  } catch (e) {
    console.warn('Could not load chat history:', e);
  }
}

/* ── SEND FROM INPUT ─────────────────── */
function sendMessage() {
  const input = document.getElementById('chat-input');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  addMessage(text);
}

/* ── FETCH STOCK PRICE ───────────────── */
async function fetchStockPrice(ticker) {
  try {
    const res = await fetch(`${API_CONFIG.baseUrl}/stocks/${ticker}/price`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.warn(`Price fetch failed for ${ticker}:`, e);
    return null;
  }
}

/* ── FORMAT PRICE ────────────────────── */
function formatPrice(val) {
  if (val == null) return '—';
  return '$' + parseFloat(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatChange(pct) {
  if (pct == null) return '';
  const sign = pct >= 0 ? '+' : '';
  return sign + pct.toFixed(2) + '%';
}

/* ── UPDATE STOCK ELEMENTS ON PAGE ────── */
async function updateStockElements() {
  const tickers = new Set();
  document.querySelectorAll('[data-ticker]').forEach(el => tickers.add(el.dataset.ticker));

  for (const ticker of tickers) {
    const data = await fetchStockPrice(ticker);
    if (!data) continue;

    document.querySelectorAll(`[data-ticker="${ticker}"]`).forEach(el => {
      const priceEl = el.querySelector('.stock-price, .trending-price');
      const changeEl = el.querySelector('.stock-change');
      const badgeEl = el.querySelector('.badge');
      const pct = data.change_percent;

      if (priceEl) priceEl.textContent = formatPrice(data.current_price);

      if (changeEl) {
        changeEl.textContent = formatChange(pct);
        changeEl.className = 'stock-change ' + (pct >= 0 ? 'up' : 'down');
      }

      if (badgeEl) {
        badgeEl.textContent = formatChange(pct);
        badgeEl.className = 'badge ' + (pct >= 0 ? 'badge-green' : 'badge-red');
      }
    });
  }
}

/* ── UPDATE STOCK DETAIL HERO ─────────── */
async function updateStockDetail(ticker) {
  const data = await fetchStockPrice(ticker);
  if (!data) return;

  const priceEl = document.querySelector('.stock-hero-price');
  const changeEl = document.querySelector('.stock-hero-change');

  if (priceEl) priceEl.textContent = formatPrice(data.current_price);

  if (changeEl) {
    const pct = data.change_percent;
    const chg = data.change;
    const arrow = pct >= 0 ? '▲ +' : '▼ ';
    changeEl.textContent = `${arrow}${Math.abs(pct).toFixed(2)}% (${chg >= 0 ? '+' : ''}${formatPrice(chg)}) сегодня`;
    changeEl.className = 'stock-hero-change ' + (pct >= 0 ? 'up' : 'down');
  }

  // Update live market data fields
  const fields = { high: data.high, low: data.low, open: data.open, prev_close: data.prev_close };
  for (const [field, val] of Object.entries(fields)) {
    const el = document.querySelector(`[data-field="${field}"]`);
    if (el) el.textContent = formatPrice(val);
  }
  const volEl = document.querySelector('[data-field="volume"]');
  if (volEl && data.volume) volEl.textContent = parseInt(data.volume).toLocaleString('en-US');
}

/* ── TOGGLES ─────────────────────────── */
function initToggles() {
  document.querySelectorAll('.toggle').forEach(btn => {
    btn.addEventListener('click', () => btn.classList.toggle('on'));
  });
}

/* ── STRATEGIES ──────────────────────── */
function initStrategies() {
  document.querySelectorAll('.strategy-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.strategy-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
  });
}

/* ── FORMAT DATE ─────────────────────── */
function formatDate(unix) {
  if (!unix) return '';
  return new Date(unix * 1000).toLocaleString('ru-RU', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
  });
}

/* ── ESCAPE HTML ─────────────────────── */
function escapeHtml(str) {
  return String(str)
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;').replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

/* ── LOAD NEWS (full page) ───────────── */
async function loadNews(ticker = 'all') {
  const container = document.getElementById('news-container');
  if (!container) return;

  container.innerHTML = '<div style="padding:20px;color:var(--text3);text-align:center">Загрузка...</div>';

  try {
    const res = await fetch(`${API_CONFIG.baseUrl}/stocks/${ticker}/news?last_n=30`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const newsList = await res.json();

    if (!newsList.length) {
      container.innerHTML = '<div style="padding:20px;color:var(--text3);text-align:center">Новостей нет</div>';
      return;
    }

    container.innerHTML = newsList.map(news => `
      <a class="news-full-card" href="${escapeHtml(news.url || '#')}" target="_blank" rel="noopener">
        <div class="news-full-top">
          <div>
            <div class="news-tag">${escapeHtml(news.ticker || news.related || 'Рынок')}</div>
            <div class="news-full-title">${escapeHtml(news.headline)}</div>
          </div>
          ${news.image ? `<img src="${escapeHtml(news.image)}" style="width:56px;height:56px;object-fit:cover;border-radius:8px;flex-shrink:0;margin-left:10px" onerror="this.style.display='none'">` : ''}
        </div>
        ${news.summary ? `<div class="news-full-body">${escapeHtml(news.summary)}</div>` : ''}
        <div class="news-full-meta">
          ${formatDate(news.datetime_unix)}${news.source ? ' · ' + escapeHtml(news.source) : ''}${news.related ? ' · ' + escapeHtml(news.related) : ''}
        </div>
      </a>
    `).join('');
  } catch (error) {
    console.error(error);
    container.innerHTML = '<div style="padding:20px;color:var(--red);text-align:center">Ошибка загрузки новостей</div>';
  }
}

/* ── LOAD HOME NEWS ──────────────────── */
async function loadHomeNews() {
  const container = document.getElementById('home-news-container');
  if (!container) return;
  try {
    const res = await fetch(`${API_CONFIG.baseUrl}/stocks/all/news?last_n=6`);
    if (!res.ok) return;
    const newsList = await res.json();
    if (!newsList.length) return;

    container.innerHTML = newsList.slice(0, 6).map(news => `
      <a class="news-card" href="${escapeHtml(news.url || '#')}" target="_blank" rel="noopener">
        <div class="news-tag">${escapeHtml(news.ticker || 'Рынок')}</div>
        <div class="news-title">${escapeHtml(news.headline)}</div>
        <div class="news-meta">${formatDate(news.datetime_unix)}${news.source ? ' · ' + escapeHtml(news.source) : ''}</div>
      </a>
    `).join('');
  } catch (e) {
    console.warn('Home news load failed:', e);
  }
}

/* ── NEWS TABS ───────────────────────── */
function initNewsTabs() {
  document.querySelectorAll('.filter-tab[data-ticker]').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.filter-tab[data-ticker]').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      loadNews(tab.dataset.ticker);
    });
  });
}

/* ── DOM READY ───────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initTelegram();

  // Chat input
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') sendMessage(); });
  }

  // News page
  if (document.getElementById('news-container')) {
    initNewsTabs();
    loadNews('all');
  }

  // Home page news
  if (document.getElementById('home-news-container')) {
    loadHomeNews();
  }

  // AI chat page
  if (document.getElementById('chat-messages')) {
    loadChatHistory();
    const params = new URLSearchParams(window.location.search);
    const stock = params.get('stock');
    if (stock) setTimeout(() => addMessage(`Расскажи подробнее про ${stock}`), 800);
  }

  // Live prices on listing pages
  if (document.querySelector('[data-ticker]')) {
    updateStockElements();
  }

  // Stock detail page
  const titleMatch = document.title.match(/^([A-Z]+)\s*[—-]/);
  if (titleMatch && document.querySelector('.stock-hero-price')) {
    updateStockDetail(titleMatch[1]);
  }

  // Auth
  document.getElementById('login-btn')?.addEventListener('click', () => { window.location.href = 'index.html'; });
  document.getElementById('register-btn')?.addEventListener('click', () => { window.location.href = 'login.html'; });

  initToggles();
  initStrategies();
});