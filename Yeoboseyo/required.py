from flask import session, redirect
from functools import wraps


def login_required(f):
    @wraps(f)
    def required_function(*args, **kwargs):
        user = dict(session).get('profile', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        # return 'Logged in is required for you to access this page!'
        return redirect('/')
    return required_function