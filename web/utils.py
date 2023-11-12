from functools import wraps
from flask import session, redirect


def login_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if session.get("authenticated", False):
            return view_func(*args, **kwargs)
        else:
            return redirect("/login")

    return decorated_view
