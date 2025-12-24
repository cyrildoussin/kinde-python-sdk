"""
Django Example Application for Kinde Authentication

This example demonstrates how to use Kinde authentication in a Django application.

Setup Instructions:
1. Install dependencies:
   pip install django kinde-django python-dotenv

2. Create a Django project:
   django-admin startproject myproject
   cd myproject

3. Create a .env file with your Kinde credentials:
   KINDE_DOMAIN=your-domain.kinde.com
   KINDE_CLIENT_ID=your-client-id
   KINDE_CLIENT_SECRET=your-client-secret
   KINDE_REDIRECT_URI=http://localhost:8000/kinde/callback
   SECRET_KEY=your-django-secret-key

4. Update settings.py:
   - Add 'kinde_django.middleware.FrameworkMiddleware' to MIDDLEWARE
   - Add 'django.contrib.sessions.middleware.SessionMiddleware' if not present
   - Configure SESSION_ENGINE (default is fine)
   - Set SECRET_KEY from environment

5. Update urls.py to include Kinde URLs (see example below)

6. Run migrations and start server:
   python manage.py migrate
   python manage.py runserver
"""

# Example settings.py additions:
"""
import os
from dotenv import load_dotenv

load_dotenv()

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'kinde_django.middleware.FrameworkMiddleware',  # Add this
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # or 'file' or 'cache'
"""

# Example urls.py:
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from dotenv import load_dotenv
import os

from kinde_sdk.auth.oauth import OAuth
import kinde_django

load_dotenv()

# Initialize Kinde OAuth with Django framework
kinde_oauth = OAuth(
    framework="django"
)

# Get URL patterns from the framework
django_framework = kinde_django.DjangoFramework()
django_framework.set_oauth(kinde_oauth)
django_framework.start()
kinde_urlpatterns = django_framework.get_urlpatterns()

# Example home view
def home(request):
    if kinde_oauth.is_authenticated():
        user = kinde_oauth.get_user_info()
        return HttpResponse(f'''
            <html>
                <body>
                    <h1>Welcome, {user.get("email", "User")}!</h1>
                    <p>You are logged in.</p>
                    <a href="/kinde/logout">Logout</a>
                </body>
            </html>
        ''')
    return HttpResponse('''
        <html>
            <body>
                <h1>Welcome to the Example App</h1>
                <p>You are not logged in.</p>
                <a href="/kinde/login">Login</a>
            </body>
        </html>
    ''')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('kinde/', include((kinde_urlpatterns, 'kinde'), namespace='kinde')),
    path('', home, name='home'),
]
"""

# Alternative: Using the urls.py helper module
"""
from django.urls import path, include
from kinde_django import urls as kinde_urls

urlpatterns = [
    path('kinde/', include(kinde_urls)),
    # ... other patterns
]
"""


