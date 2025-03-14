import ollama
from flask import render_template, request, jsonify
from . import chatbot_bp  # Import the chatbot Blueprint

# Function to call LLaMA 3.2 using Ollama API
def generate_response(user_message):
    try:
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": user_message}])
        return response.get("message", {}).get("content", "Error: No response generated.")
    except Exception as e:
        return f"Error: {str(e)}"

@chatbot_bp.route("/")
def chatbot_home():
    return render_template("chatbot.html")

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    # Generate response using Ollama API
    response = generate_response(user_message)

    return jsonify({"response": response})
