import subprocess
import io
from flask import render_template, request, send_file, jsonify
from . import summarizer_bp
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Function to summarize text using LLaMA 3.2 via Ollama
def generate_response(user_message):
    try:
        # Define the pre-prompt
        pre_prompt = (
            "You are a text summarization assistant. Your task is to summarize the given text "
            "in a clear and concise manner while retaining the key information.\n\n"
            "User Input:\n"
        )

        # Combine the pre-prompt with the user's message
        formatted_message = pre_prompt + user_message

        # Run Ollama with UTF-8 encoding
        result = subprocess.run(
            ["ollama", "run", "llama3.2", formatted_message],
            capture_output=True,
            text=True,
            encoding="utf-8"  # ✅ Ensure UTF-8 encoding
        )

        # Check if command was successful
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Error: Failed to generate a response from the model."

    except UnicodeDecodeError as e:
        return f"Error: Unicode decoding issue - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


@summarizer_bp.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        input_text = request.form["input_text"]
        if input_text.strip():
            summary = generate_response(input_text)

    return render_template("summarizer.html", summary=summary)

# Function to generate a PDF report
def generate_pdf(original_text, summary):
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    page_width, page_height = letter
    margin = 50
    line_height = 20
    y_position = page_height - margin

    def add_page():
        nonlocal y_position
        pdf.showPage()
        pdf.setFont("Helvetica", 12)
        y_position = page_height - margin

    def draw_wrapped_text(text, y_pos):
        words = text.split()
        line = ""
        for word in words:
            if pdf.stringWidth(line + " " + word, "Helvetica", 12) < (page_width - 2 * margin):
                line += " " + word
            else:
                if y_pos < margin:
                    add_page()
                    y_pos = page_height - margin
                pdf.drawString(margin, y_pos, line.strip())
                y_pos -= line_height
                line = word
        if line:
            if y_pos < margin:
                add_page()
                y_pos = page_height - margin
            pdf.drawString(margin, y_pos, line.strip())
            y_pos -= line_height
        return y_pos

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin, y_position, "Text Summarization Report")
    y_position -= 2 * line_height

    pdf.setFont("Helvetica", 12)
    pdf.drawString(margin, y_position, "Original Text:")
    y_position -= line_height
    y_position = draw_wrapped_text(original_text, y_position - line_height)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y_position - line_height, "Summarized Text:")
    y_position -= 2 * line_height
    pdf.setFont("Helvetica", 12)
    draw_wrapped_text(summary, y_position)

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer

@summarizer_bp.route("/download_pdf", methods=["POST"])
def download_pdf():
    original_text = request.form["input_text"]
    summary = request.form["summary"]

    pdf_buffer = generate_pdf(original_text, summary)
    return send_file(pdf_buffer, as_attachment=True, download_name="summary.pdf", mimetype="application/pdf")
