"""
URL configuration helper for Kinde Django integration.

Note: This module provides a convenience function to get URL patterns.
You must initialize the OAuth instance first before using these URLs.

Example usage in your Django project's urls.py:

    from django.urls import include, path
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

This will make the Kinde routes available at:
- /kinde/login
- /kinde/callback
- /kinde/logout
- /kinde/register
- /kinde/user
"""

def get_kinde_urlpatterns(oauth_instance):
    """
    Get URL patterns for Kinde routes.
    
    Args:
        oauth_instance: The initialized OAuth instance
        
    Returns:
        list: URL patterns that can be included in Django's urlpatterns
    """
    from .framework.django_framework import DjangoFramework
    
    framework = DjangoFramework()
    framework.set_oauth(oauth_instance)
    framework.start()
    return framework.get_urlpatterns()

# For backward compatibility, export an empty list
# Users should use get_kinde_urlpatterns() function instead
urlpatterns = []

