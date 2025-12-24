# Django Example Application

This directory contains examples demonstrating how to use Kinde authentication with Django.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install django kinde-django python-dotenv
   ```

2. **Create a Django project:**
   ```bash
   django-admin startproject myproject
   cd myproject
   ```

3. **Create a `.env` file** with your Kinde credentials:
   ```env
   KINDE_DOMAIN=your-domain.kinde.com
   KINDE_CLIENT_ID=your-client-id
   KINDE_CLIENT_SECRET=your-client-secret
   KINDE_REDIRECT_URI=http://localhost:8000/kinde/callback
   SECRET_KEY=your-django-secret-key
   ```

4. **Update `settings.py`:**
   - Add `'kinde_django.middleware.FrameworkMiddleware'` to `MIDDLEWARE`
   - Ensure `'django.contrib.sessions.middleware.SessionMiddleware'` is present
   - Set `SECRET_KEY` from environment variable
   - Configure `SESSION_ENGINE` (default database backend is fine)

5. **Update `urls.py`** to include Kinde URLs (see `example_app.py` for details)

6. **Run migrations and start server:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Example Code

See `example_app.py` for complete code examples showing:
- How to configure Django settings
- How to initialize Kinde OAuth
- How to set up URL patterns
- How to check authentication status in views

## Middleware Configuration

The `FrameworkMiddleware` must be added to your `MIDDLEWARE` setting in `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'kinde_django.middleware.FrameworkMiddleware',  # Add this
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]
```

**Important:** The `FrameworkMiddleware` should be placed after `SessionMiddleware` to ensure sessions are available.

## URL Configuration

You can include Kinde URLs in your project's `urls.py`:

```python
from django.urls import path, include
from kinde_sdk.auth.oauth import OAuth
import kinde_django

# Initialize OAuth
kinde_oauth = OAuth(framework="django")

# Get framework instance and set OAuth
django_framework = kinde_django.DjangoFramework()
django_framework.set_oauth(kinde_oauth)
django_framework.start()

# Get URL patterns
kinde_urlpatterns = django_framework.get_urlpatterns()

urlpatterns = [
    path('kinde/', include((kinde_urlpatterns, 'kinde'), namespace='kinde')),
    # ... other URL patterns
]
```

This will make the following routes available:
- `/kinde/login` - Redirects to Kinde login page
- `/kinde/callback` - Handles OAuth callback
- `/kinde/logout` - Logs out user
- `/kinde/register` - Redirects to Kinde registration page
- `/kinde/user` - Returns current user information (JSON)

## Session Configuration

Django sessions are used to store authentication state. Make sure you have:

1. `SessionMiddleware` in your `MIDDLEWARE` setting
2. `django.contrib.sessions` in your `INSTALLED_APPS`
3. Run migrations: `python manage.py migrate`

The session backend can be configured in `settings.py`:
- `django.contrib.sessions.backends.db` (default, requires database)
- `django.contrib.sessions.backends.file` (file-based)
- `django.contrib.sessions.backends.cache` (cache-based)


