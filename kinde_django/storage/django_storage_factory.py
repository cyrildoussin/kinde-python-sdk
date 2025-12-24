from typing import Optional, Dict, Any
from kinde_sdk.core.storage.storage_factory import StorageFactory
from kinde_sdk.core.storage.framework_aware_storage import FrameworkAwareStorage
from .django_storage import DjangoStorage
import logging

logger = logging.getLogger(__name__)

class DjangoStorageFactory(StorageFactory):
    """
    Factory for creating Django-specific storage instances.
    """
    
    @staticmethod
    def create_storage(config: Optional[Dict[str, Any]] = None) -> DjangoStorage:
        """
        Create a Django storage instance.
        
        Args:
            config (Optional[Dict[str, Any]]): Configuration options.
                Not used in Django implementation as it uses Django's session.
                
        Returns:
            DjangoStorage: A Django storage instance.
        """
        return DjangoStorage()


