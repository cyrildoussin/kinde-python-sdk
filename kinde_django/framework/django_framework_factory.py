from typing import Optional, Dict, Any
from kinde_sdk.core.framework.framework_factory import FrameworkFactory
from .django_framework import DjangoFramework

class DjangoFrameworkFactory:
    """
    Factory class for creating Django framework instances.
    This factory is responsible for creating and registering Django framework instances.
    """
    
    @staticmethod
    def create_framework(app: Optional[Any] = None) -> DjangoFramework:
        """
        Create a Django framework instance.
        
        Args:
            app (Optional[Any]): The Django application instance (optional).
                Django doesn't require explicit app instance like Flask/FastAPI.
                
        Returns:
            DjangoFramework: A Django framework instance
        """
        return DjangoFramework(app)


