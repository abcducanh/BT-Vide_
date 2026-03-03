from flask import Blueprint

bp = Blueprint("submissions", __name__, url_prefix="/submissions")

from . import routes  # noqa
