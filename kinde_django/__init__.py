from .framework.django_framework import DjangoFramework
from kinde_sdk.core.framework.framework_factory import FrameworkFactory
from kinde_sdk.core.storage.storage_factory import StorageFactory
from .storage.django_storage_factory import DjangoStorageFactory

# Register the Django framework
FrameworkFactory.register_framework("django", DjangoFramework)
StorageFactory.register_framework_factory("django", DjangoStorageFactory)

__all__ = ['DjangoFramework']


