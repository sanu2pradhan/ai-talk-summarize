from flask import Blueprint

chatbot_bp = Blueprint("chatbot", __name__, template_folder="templates", static_folder="static")

from . import routes  # Import routes