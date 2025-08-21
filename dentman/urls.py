from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('app/', include('dentman.app.urls')),
    path('man/', include('dentman.man.urls')),
    path('admin/', admin.site.urls),
    path('storage/<path:file_path>', views.get_file, name="get_file"),
]
