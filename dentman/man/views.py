from django.http import HttpResponseBase, HttpResponse
from django.conf import settings

from dentman.man.models import Worker, Employment, ManagementStaff
from dentman.utils import return_file_in_response


def show_contract_scan(request, file_path: str) -> HttpResponseBase:
    """
    Function to show contract scan of employment. There are 3 cases when we return file
    1) user is a superuser
    2) user is the new_employee in Employment model
    3) user is in management staff and is responsible for hr
    Due to login_required middleware every user is authenticated, and it isn't checked again
    If user doesn't match any of these cases return 404
    """
    storage_root =settings.STORAGE_ROOT / "contr"

    # Case 1). if user is superuser return file
    if request.user.is_superuser:
        return return_file_in_response(storage_root, file_path)

    # try to get worker
    try:
        worker = Worker.objects.get(user=request.user, is_active=True)
    except Worker.DoesNotExist:
        # if user isn't even worker don't show file
        return HttpResponse("Resource not found", status=404)

    # try to get employment from database
    url_parts = file_path.split('/')
    if len(url_parts) != 3:
        return HttpResponse("Resource not found", status=404) # wrong url format
    id_part1, id_part2, _ = url_parts
    try:
        element_id_str = id_part1 + id_part2
        element_id = int(element_id_str)
        employment = Employment.objects.get(id=element_id)
    except (ValueError, Employment.DoesNotExist):
        return HttpResponse("Resource not found", status=404) # wrong url format or such employment doesn't exist

    # Case 2) user is the employment's new employee
    if employment.new_employee == worker:
        return return_file_in_response(storage_root, file_path)

    # Case 3) user is the company representative
    # first try to get management staff
    try:
        _ = ManagementStaff.objects.get(worker=worker, is_hr=True)
        return return_file_in_response(storage_root, file_path)
    except ManagementStaff.DoesNotExist:
        # If the worker is not an HR rep, fall through to the final 404.
        pass

    return HttpResponse("Resource not found", status=404) # if user doesn't match any of cases, return 404
