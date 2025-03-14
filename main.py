from flask import Flask, render_template
from blueprints.summarizer import summarizer_bp
from blueprints.chatbot import chatbot_bp
app = Flask(__name__)

# Register blueprints with unique prefixes
app.register_blueprint(summarizer_bp, url_prefix="/summarizer")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot")

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
