import re

def get_upload_path(instance, filename):
    """Function to return a path in storage where file will be stored.

    It's based on if record has id (isn't a new record) or doesn't have id (isn't an existing record)

    If it's a new record then file it temporary stored in {class_name}/'temp' directory

    If it's existing record, then record has id and based on that a path is separated into two directories where first
    directory is named after first to numbers of id and second directory after two last numbers in id. Thanks to this
    we achieve nicely stored data with optimization of file return by the server"""
    instance_id = instance.id or 'temp'
    if isinstance(instance_id, int):
        d = "/".join(re.findall("..", f"{instance_id:04d}"))
    else:
        d = 'temp'
    return f"{instance.__class__.__name__}/{d}/{filename}"