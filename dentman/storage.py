from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class CustomFileSystemStorage(FileSystemStorage):
    def __init__(self, **kwargs):
        kwargs.update({
            'location': settings.STORAGE_ROOT,
            'base_url': settings.STORAGE_URL,
        })
        super(CustomFileSystemStorage, self).__init__(**kwargs)