from django.utils.deprecation import MiddlewareMixin
from kinde_sdk.core.framework.framework_context import FrameworkContext
import logging

logger = logging.getLogger(__name__)

class FrameworkMiddleware(MiddlewareMixin):
    """
    Middleware for handling Django-specific request/response processing.
    Sets the current request in the framework context so storage implementations
    can access it without needing to pass it through the entire call chain.
    """
    
    def process_request(self, request):
        """
        Process the request before it reaches the view.
        Sets up the framework context with the current request.
        
        Args:
            request: The Django HttpRequest object
        """
        FrameworkContext.set_request(request)
    
    def process_response(self, request, response):
        """
        Process the response after it leaves the view.
        Clears the framework context.
        
        Args:
            request: The Django HttpRequest object
            response: The Django HttpResponse object
            
        Returns:
            HttpResponse: The processed response
        """
        FrameworkContext.clear_request()
        return response


