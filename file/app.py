from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transformers import T5Tokenizer, T5ForConditionalGeneration
from deep_translator import GoogleTranslator
from pymongo import MongoClient
from bson.objectid import ObjectId
from PyPDF2 import PdfReader
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from langdetect import detect

app = Flask(__name__)
CORS(app)

# ------------------ MongoDB setup ------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["summary_app"]
collection = db["history"]

# ------------------ Load T5 ------------------
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# ------------------ File text extraction ------------------
def extract_text(file):
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif filename.endswith(".docx"):
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

# ------------------ Summarize exact word count ------------------
def generate_summary_exact(text, word_limit):
    input_lang = detect(text)
    # Translate to English if needed
    text_en = GoogleTranslator(source=input_lang, target="en").translate(text) if input_lang != "en" else text

    # Rough summary using T5
    input_text = "summarize: " + text_en
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    rough = model.generate(inputs, max_length=300, min_length=60, num_beams=5, length_penalty=1.5, early_stopping=True)
    rough_summary = tokenizer.decode(rough[0], skip_special_tokens=True)

    # Enforce word limit
    words = rough_summary.split()
    if len(words) >= word_limit:
        english_final = " ".join(words[:word_limit])
    else:
        # Continue generating if not enough words
        while len(words) < word_limit:
            extra = model.generate(tokenizer.encode("continue: " + rough_summary, return_tensors="pt", max_length=256, truncation=True), max_length=120, num_beams=4, early_stopping=True)
            extra_text = tokenizer.decode(extra[0], skip_special_tokens=True)
            words.extend(extra_text.split())
            rough_summary += " " + extra_text
        english_final = " ".join(words[:word_limit])

    # Translate back to original language
    final_output = GoogleTranslator(source="en", target=input_lang).translate(english_final) if input_lang != "en" else english_final
    return final_output

# ------------------ Summarize API ------------------
@app.route("/summarize", methods=["POST"])
def summarize_api():
    text = request.form.get("text", "")
    word_limit = int(request.form.get("summary_length", 100))
    preferred_lang = request.form.get("lang", None)

    # If file uploaded
    if "file" in request.files:
        text_file = extract_text(request.files["file"])
        text += "\n" + text_file

    if not text.strip():
        return jsonify({"error": "No valid text found"}), 400

    summary = generate_summary_exact(text, word_limit)

    # Translate to preferred language if requested
    if preferred_lang:
        summary = GoogleTranslator(source="auto", target=preferred_lang).translate(summary)

    # Save to MongoDB
    result = collection.insert_one({
        "text": text,
        "summary": summary,
        "summary_length": word_limit,
        "target_lang": preferred_lang,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({"summary": summary, "_id": str(result.inserted_id)})

# ------------------ Download PDF ------------------
@app.route("/download", methods=["POST"])
def download_pdf():
    text = request.json.get("text", "")
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin
    max_chars_per_line = 90

    # Split text into lines for proper wrapping
    for paragraph in text.split("\n"):
        for i in range(0, len(paragraph), max_chars_per_line):
            line = paragraph[i:i+max_chars_per_line]
            pdf.drawString(margin, y, line)
            y -= 15
            if y < margin:
                pdf.showPage()
                y = height - margin

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="summary.pdf", mimetype="application/pdf")

# ------------------ History APIs ------------------
@app.route("/history", methods=["GET"])
def get_history():
    data = list(collection.find().sort("timestamp", -1))
    for item in data:
        item["_id"] = str(item["_id"])
    return jsonify(data)

@app.route("/history/<id>", methods=["DELETE"])
def delete_history_item(id):
    collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"status":"deleted"})

@app.route("/history", methods=["DELETE"])
def clear_history():
    collection.delete_many({})
    return jsonify({"status":"cleared"})

# ------------------ Run ------------------
if __name__ == "__main__":
    app.run(debug=True, port=8000)