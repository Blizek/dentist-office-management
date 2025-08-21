from django.conf import settings
from django.http import HttpResponse, HttpResponseBase
from django.contrib.auth.decorators import login_not_required

from dentman.utils import return_file_in_response


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_not_required
def get_user_profile_photo(request, file_path: str) -> HttpResponseBase:
    return return_file_in_response(settings.STORAGE_ROOT / "users-prof-photo",file_path)