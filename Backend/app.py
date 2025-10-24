from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from model.extract_text import extract_text
import pytesseract
from model.ner_extractor import extract_all
from model.excel_manager import append_lab_results_to_excel, get_excel_stats, EXCEL_FILE_PATH

# If Tesseract is not in PATH (Windows), uncomment and set the path
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app)  # Allow all origins

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Health check route
@app.route("/health", methods=["GET"])
def health():
    excel_stats = get_excel_stats()
    return jsonify({
        "status": "OK",
        "message": "Medical Extractor API is running",
        "excel_stats": excel_stats
    })

# File upload & extract route (text only)
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Extract text using updated extract_text function
    try:
        extracted_text = extract_text(file_path)
    except Exception as e:
        return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500

    # Return JSON with extracted text
    response = {
        "filename": file.filename,
        "extracted_text": extracted_text if extracted_text else "No text extracted"
    }

    return jsonify(response), 200

# Analyze route - full NER extraction + Excel export
@app.route("/analyze", methods=["POST"])
def analyze_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        # Extract raw text
        text = extract_text(file_path)
        
        if not text or len(text.strip()) < 50:
            return jsonify({"error": "Insufficient text extracted from document"}), 400

        # NER extraction with standardized format
        result = extract_all(text)
        
        # Append lab results to Excel file
        rows_added = append_lab_results_to_excel(result)
        
        # Add Excel info to response
        result['excel_export'] = {
            'success': rows_added > 0,
            'rows_added': rows_added,
            'message': f"Added {rows_added} lab test records to Excel file"
        }
        
        # Get updated stats
        excel_stats = get_excel_stats()
        result['excel_stats'] = excel_stats

        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# Download Excel file
@app.route("/download-excel", methods=["GET"])
def download_excel():
    """
    Download the consolidated Excel file containing all lab results
    """
    if not os.path.exists(EXCEL_FILE_PATH):
        return jsonify({"error": "Excel file not found. Process at least one report first."}), 404
    
    try:
        return send_file(
            EXCEL_FILE_PATH,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='lab_results.xlsx'
        )
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

# Get Excel statistics
@app.route("/excel-stats", methods=["GET"])
def excel_statistics():
    """
    Get statistics about the Excel file
    """
    stats = get_excel_stats()
    return jsonify(stats), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
