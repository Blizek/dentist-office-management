import re

def get_upload_path(instance, filename):
    instance_id = instance.id or 'temp'
    if isinstance(instance_id, int):
        d = "/".join(re.findall("..", f"{instance_id:04d}"))
    else:
        d = 'temp'
    return f"{instance.__class__.__name__}/{d}/{filename}"