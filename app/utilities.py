import functools
from flask import session, abort
from app.config import ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def role_required(required_role):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_function(*args, **kwargs):
            user_role = session.get('role')
            if user_role != required_role:
                abort(403)
            return f(*args, **kwargs)
        return wrapped_function
    return decorator
