from typing import Dict, Optional, Any
from kinde_sdk.core.storage.framework_aware_storage import FrameworkAwareStorage
from kinde_sdk.core.framework.framework_context import FrameworkContext
import logging

logger = logging.getLogger(__name__)

class DjangoStorage(FrameworkAwareStorage):
    """
    Django-specific storage implementation using Django's session.
    Django sessions automatically persist changes, so no explicit modification flag is needed.
    """
    
    def __init__(self):
        """Initialize the Django storage."""
        super().__init__()
        
    def _get_session(self) -> Optional[Any]:
        """
        Get the current session from Django's request.
        
        Returns:
            Optional[Any]: The current Django session object, or None if not available
        """
        request = FrameworkContext.get_request()
        if not request:
            logger.warning("No request found in context")
            return None
            
        # Django request has a session attribute
        if hasattr(request, 'session'):
            logger.debug("Django session found")
            return request.session
            
        logger.warning("No Django session found")
        return None

    def get(self, key: str) -> Optional[Dict]:
        """
        Get a value from Django's session.
        
        Args:
            key (str): The key to retrieve.
            
        Returns:
            Optional[Dict]: The value if found, None otherwise.
        """
        session = self._get_session()
        if session is not None:
            value = session.get(key)
            logger.debug(f"Getting key '{key}' from session: {value}")
            return value
        return None
        
    def set(self, key: str, value: Dict) -> None:
        """
        Set a value in Django's session.
        Django sessions automatically persist changes, so no explicit save is needed.
        
        Args:
            key (str): The key to set.
            value (Dict): The value to store.
        """
        session = self._get_session()
        if session is not None:
            session[key] = value
            logger.debug(f"Setting key '{key}' in session with value: {value}")
        
    def delete(self, key: str) -> None:
        """
        Delete a value from Django's session.
        
        Args:
            key (str): The key to delete.
        """
        session = self._get_session()
        if session and key in session:
            del session[key]
            logger.debug(f"Deleting key '{key}' from session")
    
    def set_flat(self, value: str) -> None:
        """
        Store flat data in the session.
        
        Args:
            value (str): The data to store.
        """
        session = self._get_session()
        if session is not None:
            session["_flat_data"] = value
            logger.debug(f"Setting flat data in session: {value}")

