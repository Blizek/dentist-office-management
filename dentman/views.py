import os

from django.conf import settings
from django.http import FileResponse, HttpResponse


def get_file(request, file_path):
    file_full_path = os.path.join(settings.STORAGE_ROOT, file_path)

    if os.path.exists(file_full_path):
        return FileResponse(open(file_full_path, 'rb'))
    return HttpResponse(status=404)
