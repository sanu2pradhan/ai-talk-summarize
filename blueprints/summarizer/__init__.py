from flask import Blueprint

# Create a Blueprint named 'summarizer'
summarizer_bp = Blueprint("summarizer", __name__, template_folder="templates")

# Import routes (ensures routes are registered when the Blueprint is loaded)
from . import routes
