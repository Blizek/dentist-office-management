from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class CustomFileSystemStorage(FileSystemStorage):
    """Creating own storage basing on the FileSystemStorage from Django, but replacing location, where files will be
    stored and base_url to show them via view"""
    def __init__(self, **kwargs):
        kwargs.update({
            'location': settings.STORAGE_ROOT, # setting custom location
            'base_url': settings.STORAGE_URL, # setting base_url for files stored there
        })
        super(CustomFileSystemStorage, self).__init__(**kwargs)