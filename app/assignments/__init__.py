from flask import Blueprint

bp = Blueprint("assignments", __name__, url_prefix="/assignments")

from . import routes  # noqa
