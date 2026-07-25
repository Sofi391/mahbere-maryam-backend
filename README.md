# 🕊️ Mahbere Maryam — Backend API

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-a30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?logo=postgresql&logoColor=white)](https://neon.tech/)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)](https://your-backend.onrender.com)
[![Swagger](https://img.shields.io/badge/Swagger-UI-85EA2D?logo=swagger&logoColor=black)](https://your-backend.onrender.com/api/docs/)
[![ReDoc](https://img.shields.io/badge/ReDoc-Docs-8A2BE2?logo=readthedocs&logoColor=white)](https://your-backend.onrender.com/api/redoc/)

> 🌐 **Live API** — [your-backend.onrender.com](https://your-backend.onrender.com) 

> 📚 **Swagger UI** — [/api/docs/](https://your-backend.onrender.com/api/docs/) 

> 📄 **ReDoc** — [/api/redoc/](https://your-backend.onrender.com/api/redoc/)

> A production-ready REST API for managing the **Mahbere Maryam** religious association — members, meetings, attendance, contributions, penalties, expenses, and financial reports.

---

## ✨ Key Highlights

- 🔐 JWT authentication with staff-only admin endpoints
- 👥 Member management with active/inactive lifecycle
- 📅 Meeting-based attendance tracking with auto-penalty generation via Django signals
- 💰 Contribution, penalty, expense, and manual payment tracking
- 📊 Monthly and yearly financial reports with balance calculations
- 🗂️ DB-level indexes on all frequently filtered fields
- 🚫 N+1 query prevention with `select_related` and DB-level aggregations
- 📝 Centralized rotating file logging (app, errors, security, DB)
- 🛡️ Full production security headers (HSTS, secure cookies, X-Frame-Options, nosniff)
- 📚 Interactive API docs — Swagger UI & ReDoc via drf-spectacular
- ☁️ Deployed on Render with Neon PostgreSQL

---

## 🧠 System Design

- Layered architecture: Views → Services → Models
- Django signals for auto-penalty creation on attendance save
- All business logic isolated in `services/` — views stay thin
- Environment-driven config — `DEBUG`, `ALLOWED_HOSTS`, `CORS`, `CSRF` all from `.env`
- Rotating log files under `logs/` — never fills disk

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2 + Django REST Framework 3.16 |
| Auth | djangorestframework-simplejwt |
| Database | PostgreSQL via Neon (dj-database-url) |
| CORS | django-cors-headers |
| Static files | WhiteNoise |
| API Docs | drf-spectacular (Swagger + ReDoc) |
| Server | Gunicorn |
| Hosting | Render |

---

## 📁 Project Structure

```
backend/
├── mahber/               # Django project settings, urls, wsgi
│   ├── settings.py
│   └── urls.py
├── mahberapp/            # Main app
│   ├── services/         # Business logic layer
│   │   ├── attendance_service.py
│   │   ├── contribution_service.py
│   │   ├── member_service.py
│   │   ├── penalty_service.py
│   │   └── report_service.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── signals.py
│   ├── permissions.py
│   ├── urls.py
│   └── admin.py
├── logs/                 # Rotating log files (gitignored)
├── .env                  # Local environment variables (gitignored)
├── .env.example          # Template for environment variables
├── requirements.txt
└── manage.py
```

---

## 🔑 Core Models

| Model | Description |
|---|---|
| `Member` | Association member with active/inactive status |
| `Meeting` | Monthly Mahber cycle (Ethiopian calendar) |
| `Attendance` | Per-member attendance per meeting (present/late/absent/excused) |
| `Contribution` | Monthly payment record per member per meeting |
| `Penalty` | Auto-generated or manual penalty per member |
| `PenaltyRule` | Configurable penalty amounts (admin-managed) |
| `Expense` | Spending tied to a meeting or standalone |
| `ManualPayment` | Extra income optionally linked to a meeting |
| `Announcement` | Public committee announcements |

---

## 📚 API Docs

| Format | URL |
|---|---|
| Swagger UI | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| OpenAPI Schema | `/api/schema/` |

---

## 🔌 API Endpoints

| Resource | Base URL |
|---|---|
| Auth | `POST /api/auth/login/`, `POST /api/auth/refresh/` |
| Members | `/api/members/` |
| Meetings | `/api/meetings/` |
| Attendance | `/api/attendance/` |
| Contributions | `/api/contributions/` |
| Penalties | `/api/penalties/` |
| Penalty Rules | `/api/penalty-rules/` |
| Expenses | `/api/expenses/` |
| Announcements | `/api/announcements/` |
| Manual Payments | `/api/manual-payments/` |
| Monthly Report | `GET /api/reports/monthly/<meeting_id>/` |
| Yearly Report | `GET /api/reports/yearly/<ethiopian_year>/` |
| Dashboard | `GET /api/dashboard/` |

---

## ▶️ Run Locally

**1. Clone and enter the backend folder**
```bash
git clone <repo-url>
cd backend
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, DATABASE_URL, DEBUG=True
```

**5. Run migrations and start**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🚀 Deploy on Render

1. Push this `backend/` folder as its own repo (or use a monorepo with root dir set)
2. Create a new **Web Service** on Render
3. Set **Build Command**: `pip install -r requirements.txt && python manage.py migrate`
4. Set **Start Command**: `gunicorn mahber.wsgi:application`
5. Add all environment variables from `.env.example` in the Render dashboard:

```
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=<your-neon-url>
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
```

---

## 📝 Logging

Logs are written to `backend/logs/` with automatic rotation (5 MB max, 5 backups):

| File | Contents |
|---|---|
| `app.log` | All app-level INFO and above |
| `errors.log` | ERROR and CRITICAL only |
| `security.log` | Django security warnings |
| `db.log` | SQL queries (dev/DEBUG only) |

---

## 🔒 Security (Production)

- `SECURE_SSL_REDIRECT = True`
- `SECURE_HSTS_SECONDS = 31536000` with subdomains + preload
- `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE = True`
- `X_FRAME_OPTIONS = 'DENY'`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- All secrets loaded from environment — never hardcoded

---

---

## 👨‍💻 About the Developer

Hi! I'm **Sofonias** — a Backend Developer and Software Engineering student passionate about building clean, production-ready systems.

This project was built to digitize and streamline the operations of the **Mahbere Maryam** religious association — replacing manual record-keeping with a structured, secure, and accessible web system.

I specialize in:
- **Backend Architecture** — Django REST Framework, layered service design, signal-driven automation
- **Database Design** — relational modeling, query optimization, indexing strategies
- **Security** — JWT auth, production security headers, environment-driven secrets
- **API Design** — RESTful endpoints with full OpenAPI documentation

### 🤝 Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/your-profile)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/your-username)

---

*Built with ❤️ for the Mahbere Maryam community*
