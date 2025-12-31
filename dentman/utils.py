import re
import os
from datetime import date

from django.db.models.fields.files import FieldFile
from django.http.response import HttpResponseBase, FileResponse, HttpResponse
from django.db.models import Model

def get_upload_path(instance: Model, filename: str, with_class_name: bool=False) -> str:
    """
    Function to return a path in storage where file will be stored.

    It's based on if record has id (isn't a new record) or doesn't have id (isn't an existing record)

    If with_class_name is true the main directory in storage will be named after class name. Otherwise, it will be skipped
    and named as set in file's storage

    If it's a new record then file it temporary stored in {class_name}/'temp' directory

    If it's existing record, then record has id and based on that a path is separated into two directories where first
    directory is named after first to numbers of id and second directory after two last numbers in id. Thanks to this
    we achieve nicely stored data with optimization of file return by the server
    """
    instance_id = instance.id or 'temp'
    if isinstance(instance_id, int):
        d = "/".join(re.findall("..", f"{instance_id:04d}"))
    else:
        d = 'temp'
    if with_class_name:
        return f"{instance.__class__.__name__}/{d}/{filename}"
    return f"{d}/{filename}"

def get_upload_path_with_class(instance: Model, filename: str) -> str:
    """
    Calls get_upload_path with with_class_name=True to be used in model fields.
    This avoids using a lambda function which cannot be serialized by migrations.
    """
    return get_upload_path(instance, filename, with_class_name=True)


def delete_old_file(old_file: FieldFile) -> None:
    """
    Function to delete old file from storage.
    As argument gets file from FileField or image from ImageField

    If this file exists then we get storage in which is this file and delete it
    """
    if old_file.name != "":
        storage = old_file.storage
        file_path = str(storage.base_location) + f"/{old_file.name}"
        if os.path.exists(file_path):
            os.remove(file_path)


def return_file_in_response(storage_root: str, file_path: str) -> HttpResponseBase:
    """
    Function to only return in response file from storage

    All authentication to show or not file is should be done before executing this function in view's code
    """
    file_full_path = os.path.join(storage_root, file_path)
    if os.path.exists(file_full_path):
        return FileResponse(open(file_full_path, 'rb'))
    return HttpResponse(status=404)

def check_if_user_is_adult(user: Model) -> bool:
    """
    Function to check if user is an adult today
    """
    today = date.today()
    age = today.year - user.birth_date.year - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
    return age >= 18