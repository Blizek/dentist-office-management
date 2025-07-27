import os

from django.conf import settings
from django.http import FileResponse, HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def get_user_profile_photo(request, file_path):
    file_full_path = os.path.join(settings.USERS_PROFILE_PHOTOS_ROOT, file_path)

    if os.path.exists(file_full_path):
        return FileResponse(open(file_full_path, 'rb'))
    return HttpResponse(status=404)