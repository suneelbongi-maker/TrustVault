from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if current_user.role not in allowed_roles:
                abort(403)

            return function(*args, **kwargs)

        return wrapper
    return decorator
