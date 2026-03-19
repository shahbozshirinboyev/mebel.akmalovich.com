# Production deployment

## 1. Environment

Create `.env` from `.env.example` and set real production values:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- PostgreSQL connection values

## 2. Install dependencies

```powershell
pip install pipenv
pipenv install --deploy
```

Or use `requirements.txt`:

```powershell
pip install -r requirements.txt
```

## 3. Prepare database and static files

```powershell
pipenv run python manage.py migrate
pipenv run python manage.py collectstatic --noinput
pipenv run python manage.py check --deploy
```

## 4. Run application

Windows / Waitress:

```powershell
pipenv run waitress-serve --host=0.0.0.0 --port=8000 config.wsgi:application
```

Put Nginx or another reverse proxy in front of the app and forward HTTPS headers.

## 5. Reverse proxy requirements

- Proxy `Host` header unchanged.
- Send `X-Forwarded-Proto: https`.
- Serve `/static/` from Django/WhiteNoise or directly from the reverse proxy.
