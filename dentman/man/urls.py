from django.urls import path

from dentman.man import views

urlpatterns = [
    path('contract/<path:file_path>', views.show_contract_scan, name='show_contract_scan'),
]