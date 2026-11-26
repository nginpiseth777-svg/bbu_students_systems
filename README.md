# Student System

A Django project for managing students, courses, lecturers, and enrollments.
Requires Python 3.10 or newer.

## Local setup (Windows PowerShell)

Run these commands from the directory containing `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Generate a secret key and replace the example value in `.env`:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Initialize the database and start the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

## Routine checks

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

For deployment, set `DEBUG=False`, configure `SECRET_KEY` and `ALLOWED_HOSTS`
for the deployment environment, use HTTPS, and run:

```powershell
python manage.py check --deploy
python manage.py collectstatic
```

`SECURE_SSL_REDIRECT` defaults to enabled when `DEBUG=False`. Set
`SECURE_HSTS_SECONDS` only after confirming the site will remain HTTPS-only;
HSTS may be cached by browsers. If TLS terminates at a reverse proxy, configure
Django's trusted proxy HTTPS handling for that deployment before enabling
redirects.
