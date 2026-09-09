# Job Board Platform

A backend for a job board platform, built with **Django**, **Django REST Framework**, and **PostgreSQL**. Supports two account types — **employers** and **candidates** — with JWT authentication.

---

## Features

- Employer & candidate signup/login (JWT-based, email as login identifier)
- Employers can post, edit, and manage job listings
- Candidates can search jobs by title, location, job type, category, and salary
- Resume upload (candidates)
- Job applications with duplicate-prevention and status tracking
- Automatic notifications — employer notified on new application, candidate notified on status change
- Django admin panel for internal management

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.1 |
| API | Django REST Framework |
| Auth | djangorestframework-simplejwt (JWT) |
| Database | PostgreSQL |
| Images | Pillow |

---

## Setup

**1. Clone the repo and create a virtual environment**
```bash
git clone https://github.com/asmae-bel/jobboard
cd jobboard
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Copy `.env.example` to `.env` and fill in your real values:
```bash
cp .env.example .env
```

**4. Create a PostgreSQL database**

Create a database matching the name in your `.env` file.

**5. Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

**6. Create a superuser** (for the admin panel)
```bash
python manage.py createsuperuser
```

**7. Run the server**
```bash
python manage.py runserver
```

---

## API Endpoints

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/employers/signup/` | Register a new employer |
| `POST` | `/api/candidates/signup/` | Register a new candidate |
| `POST` | `/api/login/` | Login (email + password) |
| `POST` | `/api/login/refresh/` | Refresh access token |

### Job Listings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jobs/` | Search / list open jobs |
| `POST` | `/api/jobs/` | Post a job *(employer only)* |
| `GET` | `/api/jobs/<id>/` | View a specific job |
| `PUT` | `/api/jobs/<id>/` | Edit a job *(owner only)* |
| `DELETE` | `/api/jobs/<id>/` | Delete a job *(owner only)* |
| `GET` | `/api/jobs/mine/` | List jobs posted by the logged-in employer |

### Resumes

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/resumes/` | List the logged-in candidate's resumes |
| `POST` | `/api/resumes/` | Upload a resume *(candidate only)* |
| `DELETE` | `/api/resumes/<id>/` | Delete a resume |

### Applications

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/applications/apply/` | Apply to a job *(candidate only)* |
| `GET` | `/api/applications/mine/` | List the logged-in candidate's applications |
| `GET` | `/api/jobs/<id>/applications/` | List applications for a job *(employer only)* |
| `PATCH` | `/api/applications/<id>/status/` | Update an application's status *(employer only)* |

### Notifications

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/notifications/` | List the logged-in user's notifications |
| `POST` | `/api/notifications/<id>/read/` | Mark a notification as read |

---

## Project Structure

```
jobboard/
├── api/
│   ├── models.py        # Employer, Candidate, Resume, JobListing, Application, Notification
│   ├── serializers.py   # Signup, login, and model serializers
│   ├── views.py         # API views and permission logic
│   ├── urls.py           # Route definitions
│   └── admin.py          # Django admin registration
├── jobboard/
│   └── settings.py
├── manage.py
└── requirements.txt
```

---

## License

This project was built as a learning/portfolio project.
