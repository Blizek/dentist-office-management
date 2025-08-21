from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(f"profile-photos/<path:file_path>", views.get_user_profile_photo, name="get_user_profile_photo"),
]