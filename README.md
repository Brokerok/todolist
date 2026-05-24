# Todolist

A small project & task manager built with Django, HTMX, Alpine.js and Bootstrap 5.
It lets a signed-in user create TODO lists, add tasks with deadlines, mark them
as done and reorder them by priority.

> **Live demo:** <https://web-production-4905.up.railway.app/>


## Features

- Email + password authentication via `django-allauth`
- Per-user isolation — every project and every task is scoped to its owner
- CRUD for projects on a single page, powered by HTMX (no full reloads)
- CRUD for tasks with inline editing, quick-add input, deadline and done state
- HTML5 + server-side validation (whitespace-only names rejected, past deadlines refused)
- Responsive layout with Bootstrap Grid
- `ruff` linter + formatter wired into `pre-commit`
- Test suite on `pytest-django`


## Tech stack

| Layer       | Choice                                              |
|-------------|-----------------------------------------------------|
| Language    | Python 3.13                                         |
| Framework   | Django 5.2                                          |
| Database    | PostgreSQL 16                                       |
| Auth        | django-allauth (email login, no verification)       |
| Templates   | Django templates + Bootstrap 5 + HTMX 2 + Alpine 3 + hyperscript |
| Static      | WhiteNoise                                          |
| WSGI        | Gunicorn                                            |
| Tooling     | ruff, pre-commit, pytest, pytest-django, factory-boy|
| Deployment  | Docker, Railway                                     |


## Project layout

```
.
├── config/             Django project (settings, urls, wsgi, asgi)
├── users/              Custom User model and allauth form overrides
├── tasks/              Project & Task domain
│   ├── models.py       Project, Task and their QuerySets
│   ├── services.py     Business logic (create/update/toggle/delete)
│   ├── forms.py        ProjectForm, TaskForm, QuickTaskForm with validation
│   ├── views.py        Class-based views with HTMX-aware responses
│   └── urls.py         URL patterns
├── templates/          Page templates and HTMX partials
├── static/css/app.css  All custom styling on top of Bootstrap 5
├── Dockerfile          App image (Python 3.13 slim)
├── docker-compose.yml  Local stack (Postgres + Django dev server)
├── railway.json        Build & deploy config for Railway
├── Procfile            Backup definition for Heroku-style platforms
├── requirements.txt    Runtime dependencies
├── requirements-dev.txt Dev / test dependencies
├── pyproject.toml      ruff, pytest and coverage configuration
├── .pre-commit-config.yaml
└── SQL.md              Answers to the SQL exercise
```

Business logic lives in `tasks/services.py`; views stay thin and only handle
HTTP concerns (parsing the request, rendering the right template). The same
service functions can be reused from management commands, the admin or tests.


## Quick start with Docker

You need Docker and Docker Compose installed.

```bash
# 1. Clone and enter the project
git clone <your-fork-url> todolist && cd todolist

# 2. Copy the env template
cp .env.example .env

# 3. Bring everything up (Postgres + Django dev server with auto-migrate)
docker compose up --build

# 4. (in a second terminal) create a superuser if you want to use the admin
docker compose exec web python manage.py createsuperuser
```

Open <http://localhost:8000>. Sign up with an email + password and start
adding TODO lists.


## Local development without Docker

```bash
# Python 3.13 is required
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Point Django at any local Postgres you have running
cp .env.example .env
# edit .env if needed (DATABASE_URL defaults to postgres://todolist:todolist@db:5432/todolist)

# Run migrations and start the dev server
python manage.py migrate
python manage.py runserver
```

Install the pre-commit hook so `ruff` runs automatically on every commit:

```bash
pre-commit install
pre-commit run --all-files
```


## Environment variables

| Name                          | Required | Default                                            | Notes                                                |
|-------------------------------|----------|----------------------------------------------------|------------------------------------------------------|
| `DJANGO_SECRET_KEY`           | yes (prod) | `django-insecure-change-me`                      | Set a long random string in production               |
| `DJANGO_DEBUG`                | no       | `False`                                            | Set to `True` for local development                  |
| `DJANGO_ALLOWED_HOSTS`        | yes (prod) | `localhost,127.0.0.1`                            | Comma-separated list                                 |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | no       | (empty)                                            | Comma-separated list of `https://your-host` origins  |
| `DATABASE_URL`                | yes      | `postgres://todolist:todolist@db:5432/todolist`    | Standard Postgres URL                                |
| `DJANGO_EMAIL_BACKEND`        | no       | `django.core.mail.backends.console.EmailBackend`   | Allauth sends mail through this backend              |
| `RAILWAY_PUBLIC_DOMAIN`       | auto     | (set by Railway)                                   | Automatically added to allowed hosts / CSRF origins  |


## Running the tests

```bash
# inside the venv
pytest                 # quick run
pytest --cov           # with coverage report

# in Docker
docker compose exec web pytest --cov
```


## Deploying to Railway

Railway will build the image from the included `Dockerfile` and apply the
deploy command from `railway.json`.

1. **Push the repo to GitHub.**
2. On <https://railway.app> click **New Project → Deploy from GitHub repo** and
   pick this repository.
3. Add a **PostgreSQL** plugin (Railway → New → Database → Postgres). It
   exposes a `DATABASE_URL` automatically.
4. In **Variables**, set at minimum:
   ```
   DJANGO_SECRET_KEY        = <generate a long random string>
   DJANGO_DEBUG             = False
   DJANGO_ALLOWED_HOSTS     = ${{RAILWAY_PUBLIC_DOMAIN}}
   DJANGO_CSRF_TRUSTED_ORIGINS = https://${{RAILWAY_PUBLIC_DOMAIN}}
   ```
   `DATABASE_URL` is wired automatically; `RAILWAY_PUBLIC_DOMAIN` is also
   already provided. The settings file picks both of them up.
5. Trigger a deploy. The `startCommand` runs `python manage.py migrate`
   before `gunicorn`, so the database schema is always up to date.
6. Open the Railway URL to verify the app, then paste it into the
   **Live demo** line at the top of this README.

To create a superuser for `/admin/`, open the Railway shell:

```bash
railway run python manage.py createsuperuser
```


## Useful commands

| Command                             | What it does                                  |
|-------------------------------------|-----------------------------------------------|
| `ruff check .`                      | Lint                                          |
| `ruff format .`                     | Auto-format                                   |
| `pytest`                            | Run the test suite                            |
| `pytest --cov`                      | Run tests with coverage                       |
| `python manage.py makemigrations`   | Create migrations after a model change        |
| `python manage.py migrate`          | Apply migrations                              |
| `python manage.py collectstatic`    | Gather static files (production)              |
| `pre-commit run --all-files`        | Run all pre-commit hooks across the tree      |
