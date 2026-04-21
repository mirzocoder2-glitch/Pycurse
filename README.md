# ПлатформаТЈ — Backend Setup

## 📁 Сохтори лоиҳа

```
platformtj/
├── app.py               ← Flask backend (API)
├── requirements.txt     ← Зарурияти Python
├── instance/
│   └── platform.db      ← SQLite база (худкор месозад)
└── static/              ← Фронтенд (HTML файлҳо)
    ├── index.html
    ├── login.html
    ├── admin.html
    ├── dashboard.html
    ├── pupil.html
    ├── test.html
    ├── zadacha.html
    ├── reyting.html
    ├── chat.html
    ├── jadval.html
    ├── sertifikat.html
    ├── interpretator.html
    ├── style.css
    ├── js/
    │   └── api.js       ← API клиент (localStorage ивазкунанда)
    └── uploads/
        └── videos/      ← Видеофайлҳо дар ин ҷо сабт мешаванд
```

---

## 🚀 Насб ва оғоз

### Қадам 1 — Python насб кунед
Python 3.9+ лозим аст.

### Қадам 2 — Китобхонаҳо насб кунед
```bash
pip install -r requirements.txt
```

### Қадам 3 — HTML файлҳоро кӯчонед
HTML файлҳои фронтендро ба папкаи `static/` кӯчонед:
```
static/index.html
static/login.html
static/admin.html
... ва ғайра
```

### Қадам 4 — api.js пайваст кунед
Дар ҳар HTML файл ин сатрро **пеш аз** `</body>` илова кунед:
```html
<script src="/js/api.js"></script>
```

### Қадам 5 — Серверро оғоз кунед
```bash
python app.py
```

### Қадам 6 — Браузер кушоед
```
http://localhost:5000
```

---

## 🔑 Маълумоти дохилшавӣ (пешфарз)

| Нақш         | Логин    | Парол    |
|--------------|----------|----------|
| Администратор | admin    | admin123 |
| Хонанда      | student1 | pass123  |

---

## 📡 API Endpoints

### Auth
| Метод | Роҳ | Тавсиф |
|-------|-----|--------|
| POST | `/api/auth/login` | Дохил шудан |
| POST | `/api/auth/logout` | Баромадан |
| GET  | `/api/auth/me` | Корбари ҷорӣ |

### Корбарон (Админ)
| Метод | Роҳ | Тавсиф |
|-------|-----|--------|
| GET  | `/api/users` | Рӯйхати корбарон |
| POST | `/api/users` | Корбар илова кардан |
| PUT  | `/api/users/<id>` | Корбар навсозӣ |
| DELETE | `/api/users/<id>` | Корбар ҳазф кардан |

### Курсҳо
| Метод | Роҳ | Тавсиф |
|-------|-----|--------|
| GET  | `/api/courses` | Ҳамаи курсҳо |
| POST | `/api/courses` | Курс илова (Админ) |
| PUT  | `/api/courses/<id>` | Курс навсозӣ (Админ) |
| DELETE | `/api/courses/<id>` | Курс ҳазф (Админ) |

### Мавзӯъ & Видео
| Метод | Роҳ | Тавсиф |
|-------|-----|--------|
| GET  | `/api/topics?course_id=1` | Мавзӯъҳо |
| POST | `/api/topics` | Мавзӯъ + видео (multipart) |
| PUT  | `/api/topics/<id>` | Навсозӣ |
| DELETE | `/api/topics/<id>` | Ҳазф |
| GET  | `/api/topics/<id>/video` | Видео стриминг |

### Тестҳо
| Метод | Роҳ | Тавсиф |
|-------|-----|--------|
| GET  | `/api/tests` | Тестҳо |
| POST | `/api/tests` | Тест илова (Админ) |
| POST | `/api/tests/<id>/submit` | Ҷавобҳо фиристодан |

### Чат
| Метод | Роҳ | Тавсиф |
|-------|-----|--------|
| GET  | `/api/chat/rooms` | Хонаҳои чат |
| GET  | `/api/chat/<room>/messages` | Паёмҳо |
| POST | `/api/chat/<room>/send` | Паём фиристодан |

### Аналитика (Админ)
| Метод | Роҳ | Тавсиф |
|-------|-----|--------|
| GET  | `/api/analytics` | Статистикаи умумӣ |
| GET  | `/api/leaderboard` | Рейтинг |

---

## 🔧 Тағйир додани конфигуратсия

Дар `app.py` ин параметрҳоро тағйир диҳед:

```python
app.secret_key = 'калиди-пинҳонии-худатон'   # Ҳатман тағйир диҳед!
MAX_VIDEO = 500 * 1024 * 1024                 # Андозаи ҳадди видео (500МБ)
```

---

## 🌐 Истеҳсол (Production)

Барои истеҳсол Gunicorn истифода кунед:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## ⚠️ Муҳим

1. **`app.secret_key`** — Дар истеҳсол ҳатман тағйир диҳед
2. **Видео** — Файлҳо дар `static/uploads/videos/` сабт мешаванд
3. **База** — `instance/platform.db` худкор месозад
4. **CORS** — Танҳо аз `localhost` кор мекунад (дар истеҳсол тағйир диҳед)
