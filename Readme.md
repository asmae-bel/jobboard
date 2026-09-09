# Job Board Platform

A backend for a job board platform, built with **Django**, **Django REST Framework**, and **PostgreSQL**. Supports two account types — employers and candidates — with JWT authentication.

---

## Features

- Employer & candidate signup/login (JWT-based, email as login identifier)
- Employers can post, edit, and manage job listings
- Candidates can search jobs by title, location, job type, category, and salary
- Resume upload (candidates)
- Job applications with duplicate-prevention and status tracking
- Automatic notifications (employer notified on new application, candidate notified on status change)
- Django admin panel for internal management

---

## Tech Stack

- Django 6.1
- Django REST Framework
- djangorestframework-simplejwt (JWT auth)
- PostgreSQL
- Pillow (image handling)

---

## Setup

1. Clone the repo and create a virtual environment:

```bash
git clone https://github.com/asmae_bel/jobboard.git
cd jobboard
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a PostgreSQL database and update `jobboard/settings.py` with your credentials.

4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (for the admin panel):

```bash
python manage.py createsuperuser
```

6. Run the server:

```bash
python manage.py runserver
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/employers/signup/` | Register a new employer |
| POST | `/api/candidates/signup/` | Register a new candidate |
| POST | `/api/login/` | Login (email + password) |
| POST | `/api/login/refresh/` | Refresh access token |
| GET/POST | `/api/jobs/` | Search jobs / post a job (employer only) |
| GET/PUT/DELETE | `/api/jobs/<id>/` | View / edit / delete a specific job |
| GET | `/api/jobs/mine/` | List jobs posted by the logged-in employer |
| GET/POST | `/api/resumes/` | List / upload resumes (candidate only) |
| DELETE | `/api/resumes/<id>/` | Delete a resume |
| POST | `/api/applications/apply/` | Apply to a job (candidate only) |
| GET | `/api/applications/mine/` | List the logged-in candidate's applications |
| GET | `/api/jobs/<id>/applications/` | List applications for a job (employer only) |
| PATCH | `/api/applications/<id>/status/` | Update an application's status (employer only) |
| GET | `/api/notifications/` | List the logged-in user's notifications |
| POST | `/api/notifications/<id>/read/` | Mark a notification as read |

