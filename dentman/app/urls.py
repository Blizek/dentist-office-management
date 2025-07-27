from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(f"{settings.USERS_PROFILE_PHOTOS_URL}/<path:file_path>", views.get_user_profile_photo, name="get_user_profile_photo"),
]