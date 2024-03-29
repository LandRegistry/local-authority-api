from flask import Flask, g, request, url_for
import uuid
import requests
from jwt_validation.validate import validate
from local_authority_api.exceptions import ApplicationError
from jwt_validation.exceptions import ValidationFailure


app = Flask(__name__)

app.config.from_pyfile("config.py")


class RequestsSessionTimeout(requests.Session):
    """Custom requests session class to set some defaults on g.requests"""

    def request(self, *args, **kwargs):
        # Set a default timeout for the request.
        # Can be overridden in the same way that you would normally set a timeout
        # i.e. g.requests.get(timeout=5)
        if not kwargs.get("timeout"):
            kwargs["timeout"] = app.config["DEFAULT_TIMEOUT"]

        return super(RequestsSessionTimeout, self).request(*args, **kwargs)


@app.before_request
def before_request():
    # Sets the transaction trace id into the global object if it has been provided in the HTTP header from the caller.
    # Generate a new one if it has not. We will use this in log messages.
    g.trace_id = request.headers.get('X-Trace-ID', uuid.uuid4().hex)
    # We also create a session-level requests object for the app to use with the header pre-set, so other APIs will
    # receive it. These lines can be removed if the app will not make requests to other LR APIs!
    g.requests = RequestsSessionTimeout()
    g.requests.headers.update({'X-Trace-ID': g.trace_id})

    # Don't check for a JWT on health endpoints
    if '/health' in request.path or request.path == url_for("organisations.get_organisations"):
        return

    if 'Authorization' not in request.headers:
        raise ApplicationError("Missing Authorization header", "AUTH1", 401)

    try:
        validate(app.config['AUTHENTICATION_API_URL'] + '/authentication/validate',
                 request.headers['Authorization'], g.requests).principle
    except ValidationFailure as fail:
        raise ApplicationError(fail.message, "AUTH1", 401)


@app.after_request
def after_request(response):
    # Add the API version (as in the interface spec, not the app) to the header. Semantic versioning applies - see the
    # API manual. A major version update will need to go in the URL. All changes should be documented though, for
    # reusing teams to take advantage of.
    response.headers["X-API-Version"] = "1.0.0"
    return response
