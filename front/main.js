(function () {
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-item').forEach(function (el) {
    if (el.getAttribute('href') === page) el.classList.add('active');
  });
})();

var aiReplies = {
  'Стоит ли докупить NVDA?':
    'NVIDIA показывает сильные фундаментальные показатели. Спрос на GPU для ИИ остаётся высоким. Текущий P/E 45x — выше среднего, но рост выручки +122% г/г оправдывает оценку. Можно рассмотреть при откатах к $840.',
  'Какие риски в моём портфеле?':
    'Основной риск — концентрация в tech-секторе (85%). Рекомендую диверсифицировать: добавить финансы или здравоохранение. Tesla создаёт волатильность — следите за новостями.',
  'Прогноз на неделю':
    'На этой неделе ожидаются данные по инфляции США. Возможна волатильность. Tech-сектор в целом в позитивном тренде. NVDA может достичь $900 при позитивных данных.',
  'Что происходит с Tesla?':
    'Tesla снижается из-за слабых данных по продажам в Европе −15% м/м и конкуренции со стороны BYD. Короткосрочно — давление. Долгосрочно — уровень $230 является поддержкой.'
};

function addMessage(text) {
  var area = document.getElementById('chat-messages');
  if (!area) return;

  var userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble bubble-user';
  userBubble.textContent = text;
  area.appendChild(userBubble);

  setTimeout(function () {
    var aiBubble = document.createElement('div');
    aiBubble.className = 'chat-bubble bubble-ai';
    aiBubble.textContent =
      aiReplies[text] ||
      'Анализирую данные... Это заглушка — ваш бэкенд подключит реального ИИ-аналитика.';
    area.appendChild(aiBubble);
    aiBubble.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, 700);
}

function sendMessage() {
  var input = document.getElementById('chat-input');
  if (!input) return;
  var text = input.value.trim();
  if (!text) return;
  input.value = '';
  addMessage(text);
}

document.addEventListener('DOMContentLoaded', function () {
  var chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') sendMessage();
    });
  }

  var loginBtn = document.getElementById('login-btn');
  if (loginBtn) {
    loginBtn.addEventListener('click', function () {
      window.location.href = 'index.html';
    });
  }

  var registerBtn = document.getElementById('register-btn');
  if (registerBtn) {
    registerBtn.addEventListener('click', function () {
      window.location.href = 'login.html';
    });
  }
});
