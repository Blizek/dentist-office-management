from django.core.files.storage import Storage
from django.core.files.base import ContentFile

class InMemoryStorage(Storage):

    def __init__(self):
        self._files = {}
        self.base_location = ""   
        self.base_url = "/media/"

    def _open(self, name, mode='rb'):
        return ContentFile(self._files[name])

    def _save(self, name, content):
        self._files[name] = content.read()
        return name

    def exists(self, name):
        return name in self._files

    def delete(self, name):
        self._files.pop(name, None)

    def url(self, name):
        return f"/test/{name}"
