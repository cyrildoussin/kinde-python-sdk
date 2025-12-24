from typing import Optional, TYPE_CHECKING, Any
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpRequest
from django.urls import path
from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login, get_user_model
from kinde_sdk.core.framework.framework_interface import FrameworkInterface
from kinde_sdk.auth.oauth import OAuth
import os
import uuid
import asyncio
import base64
import json
import logging
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)

class DjangoFramework(FrameworkInterface):
    """
    Django framework implementation.
    This class provides Django-specific functionality and integration.
    """
    
    def __init__(self, app: Optional[Any] = None):
        """
        Initialize the Django framework.
        
        Args:
            app (Optional[Any]): The Django application instance (optional).
                Django doesn't require explicit app instance like Flask/FastAPI.
        """
        self.app = app
        self._initialized = False
        self._oauth = None
        self._urlpatterns = []
        self._logger = logging.getLogger(__name__)
    
    def get_name(self) -> str:
        """
        Get the name of the framework.
        
        Returns:
            str: The name of the framework
        """
        return "django"
    
    def get_description(self) -> str:
        """
        Get a description of the framework.
        
        Returns:
            str: A description of the framework
        """
        return "Django framework implementation for Kinde authentication"
    
    def start(self) -> None:
        """
        Start the framework.
        This method initializes any necessary Django components and registers Kinde routes.
        Note: In Django, middleware and URLs are typically configured in settings.py,
        but this method can be used to prepare URL patterns.
        """
        if not self._initialized:
            # Register Kinde routes
            self._register_kinde_routes()
            self._initialized = True
    
    def stop(self) -> None:
        """
        Stop the framework.
        This method cleans up any Django resources.
        """
        if self._initialized:
            self._initialized = False
    
    def get_app(self) -> Any:
        """
        Get the Django application instance.
        
        Returns:
            Any: The Django app instance or None
        """
        return self.app
    
    def get_request(self) -> Optional['HttpRequest']:
        """
        Get the current request object.
        
        Returns:
            Optional[HttpRequest]: The current Django request object, if available
        """
        from kinde_sdk.core.framework.framework_context import FrameworkContext
        return FrameworkContext.get_request()
    
    def get_user_id(self) -> Optional[str]:
        """
        Get the user ID from the current request.
        
        Returns:
            Optional[str]: The user ID, or None if not available
        """
        request = self.get_request()
        if not request:
            return None
        return request.session.get('user_id')
    
    def set_oauth(self, oauth: OAuth) -> None:
        """
        Set the OAuth instance for this framework.
        
        Args:
            oauth (OAuth): The OAuth instance
        """
        self._oauth = oauth
    
    def get_urlpatterns(self):
        """
        Get the URL patterns for Kinde routes.
        These can be included in the project's main urls.py.
        
        Returns:
            list: List of URL patterns
        """
        return self._urlpatterns
    
    def _register_kinde_routes(self) -> None:
        """
        Register all Kinde-specific routes with Django URL patterns.
        """
        # Login view - can be sync or async
        def login_view(request: HttpRequest):
            """Redirect to Kinde login page."""
            try:
                # Handle async OAuth call
                if asyncio.iscoroutinefunction(self._oauth.login):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        login_url = loop.run_until_complete(self._oauth.login())
                        return HttpResponseRedirect(login_url)
                    finally:
                        loop.close()
                else:
                    login_url = self._oauth.login()
                    return HttpResponseRedirect(login_url)
            except Exception as e:
                self._logger.error(f"Login error: {e}")
                return HttpResponse(f"Login failed: {str(e)}", status=400)
        
        # Callback view
        def callback_view(request: HttpRequest):
            """Handle the OAuth callback from Kinde."""
            error = request.GET.get('error')
            if error and error.lower() == 'login_link_expired':
                reauth_state = request.GET.get('reauth_state')
                if reauth_state:
                    try:
                        decoded_auth_state = base64.b64decode(reauth_state).decode('utf-8')
                        reauth_dict = json.loads(decoded_auth_state)

                        # Get the redirect URL from config
                        redirect_url = os.getenv("KINDE_REDIRECT_URI")
                        base_url = redirect_url.replace("/callback", "")

                        # Build the login route URL
                        login_route_url = f"{base_url}/login"

                        # Parse and add parameters properly
                        parsed = urlparse(login_route_url)
                        query_dict = parse_qs(parsed.query)

                        # Add reauth parameters
                        for key, value in reauth_dict.items():
                            query_dict[key] = [value]

                        # Build final URL
                        new_query = urlencode(query_dict, doseq=True)
                        login_url = urlunparse((
                            parsed.scheme,
                            parsed.netloc,
                            parsed.path,
                            parsed.params,
                            new_query,
                            parsed.fragment
                        ))

                        return HttpResponseRedirect(login_url)
                    except Exception as ex:
                        return HttpResponse(f"Error parsing reauth state: {str(ex)}", status=400)

            post_login_redirect = request.session.pop('post_login_redirect_url', dict(url=settings.LOGIN_REDIRECT_URL))
            if post_login_redirect:
                post_login_redirect = post_login_redirect.get('url', '/')
            else:
                post_login_redirect = '/'

            code = request.GET.get('code')
            state = request.GET.get('state')
            
            # Validate required code parameter
            if not code:
                return HttpResponse("Authentication failed: Missing authorization code", status=400)

            # Get or generate user_id
            user_id = request.session.get('user_id', str(uuid.uuid4()))
            request.session['user_id'] = user_id
            
            # Handle async call to handle_redirect
            if not self._oauth:
                return HttpResponse("OAuth not initialized", status=500)
            try:
                if asyncio.iscoroutinefunction(self._oauth.handle_redirect):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(self._oauth.handle_redirect(code, user_id, state))
                    finally:
                        loop.close()
                else:
                    result = self._oauth.handle_redirect(code, user_id, state)
            except Exception as e:
                return HttpResponse(f"Authentication failed: {str(e)}", status=400)
            
            pre_existing_user_data = request.session.get(user_id, None)
            email = result['user'].get('email')
            User = get_user_model()
            user, created = User.objects.get_or_create(email=email, defaults={'username': email})
            django_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            if pre_existing_user_data:
                request.session[user_id] = pre_existing_user_data
            request.session['user_info'] = result['user']
            request.session['tokens'] = result['tokens']
            request.session['blah'] = "blah"

            # Build redirect URL
            if not post_login_redirect.startswith('http'):
                # Use request.build_absolute_uri for Django
                scheme = request.scheme
                host = request.get_host()
                post_login_redirect = f"{scheme}://{host}{post_login_redirect}"

            # Add state to redirect URL if present
            parsed = urlparse(post_login_redirect)
            if state:
                query_dict = parse_qs(parsed.query)
                query_dict['state'] = [state]
                new_query = urlencode(query_dict, doseq=True)
                redirect_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment
                ))
            else:
                redirect_url = post_login_redirect

            return HttpResponseRedirect(redirect_url)
        
        # Logout view
        def logout_view(request: HttpRequest):
            """Logout the user and redirect to Kinde logout page."""
            if not self._oauth:
                return HttpResponse("OAuth not initialized", status=500)
            user_id = request.session.get('user_id')
            request.session.clear()
            django_logout(request)
            try:
                if asyncio.iscoroutinefunction(self._oauth.logout):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        logout_url = loop.run_until_complete(self._oauth.logout(user_id))
                        return HttpResponseRedirect(logout_url)
                    finally:
                        loop.close()
                else:
                    logout_url = self._oauth.logout(user_id)
                    return HttpResponseRedirect(logout_url)
            except Exception as e:
                self._logger.error(f"Logout error: {e}")
                return HttpResponse(f"Logout failed: {str(e)}", status=400)
        
        # Register view
        def register_view(request: HttpRequest):
            """Redirect to Kinde registration page."""
            if not self._oauth:
                return HttpResponse("OAuth not initialized", status=500)
            try:
                if asyncio.iscoroutinefunction(self._oauth.register):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        register_url = loop.run_until_complete(self._oauth.register())
                        return HttpResponseRedirect(register_url)
                    finally:
                        loop.close()
                else:
                    register_url = self._oauth.register()
                    return HttpResponseRedirect(register_url)
            except Exception as e:
                self._logger.error(f"Register error: {e}")
                return HttpResponse(f"Registration failed: {str(e)}", status=400)
        
        # User info view
        def get_user_view(request: HttpRequest):
            """Get the current user's information."""
            if not self._oauth:
                return HttpResponse("OAuth not initialized", status=500)
            try:
                if not self._oauth.is_authenticated():
                    if asyncio.iscoroutinefunction(self._oauth.login):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            login_url = loop.run_until_complete(self._oauth.login())
                            return HttpResponseRedirect(login_url)
                        finally:
                            loop.close()
                    else:
                        login_url = self._oauth.login()
                        return HttpResponseRedirect(login_url)
                
                user_info = self._oauth.get_user_info()
                return JsonResponse(user_info)
            except Exception as e:
                self._logger.error(f"Get user error: {e}")
                return HttpResponse(f"Failed to get user info: {str(e)}", status=400)
        
        # Create URL patterns
        self._urlpatterns = [
            path('login', login_view, name='kinde_login'),
            path('callback', callback_view, name='kinde_callback'),
            path('logout', logout_view, name='kinde_logout'),
            path('register', register_view, name='kinde_register'),
            path('user', get_user_view, name='kinde_user'),
        ]
    
    def can_auto_detect(self) -> bool:
        """
        Check if this framework can be auto-detected.
        
        Returns:
            bool: True if Django is installed and available
        """
        try:
            import django
            _ = django  # Import check only
            return True
        except ImportError:
            return False

