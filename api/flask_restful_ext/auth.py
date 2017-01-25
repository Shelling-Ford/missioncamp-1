from functools import wraps

from flask import request
from flask_restful import abort


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            abort(401)

        if auth.username == 'master' and auth.password == 'historymakers':
            return f(*args, **kwargs)
    return decorated



