# 🏥 Medical Report Extractor

An AI-powered system that extracts structured data from medical laboratory reports using OCR and pattern matching algorithms.

## 📋 Project Overview

This application automatically processes medical lab reports (images, PDFs, DOCX files) and extracts:
- Patient information (name, age, sex, UHID, etc.)
- Laboratory test results (test name, value, unit, reference range, status)
- Report metadata (dates, facility, doctor information)
- Clinical notes and interpretations

All extracted data is standardized into JSON format and stored in an Excel file for easy analysis.

## ✨ Features

- ✅ **Multi-Format Support**: Processes images (PNG, JPG), PDFs, and DOCX files
- ✅ **OCR Integration**: Uses Tesseract for text extraction from scanned reports
- ✅ **Universal Extraction**: Handles different report types (LFT, CBC, Coagulation, etc.)
- ✅ **Pattern Matching**: Intelligent regex-based extraction for high accuracy
- ✅ **Excel Export**: Cumulative storage of lab results from multiple patients
- ✅ **Web Interface**: User-friendly HTML frontend for easy interaction
- ✅ **REST API**: Flask-based backend with multiple endpoints

## 🛠️ Tech Stack

### Backend
- **Python 3.11**
- **Flask** - Web framework
- **Tesseract OCR** - Optical character recognition
- **Pillow** - Image processing
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX file handling
- **pandas** - Data manipulation
- **openpyxl** - Excel file operations

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript (Vanilla)**

## 📁 Project Structure
'''
Medical-Extracter/
├── Backend/
│ ├── model/
│ │ ├── init.py
│ │ ├── extract_text.py # Multi-format text extraction
│ │ ├── ner_extractor.py # Lab test extraction logic
│ │ └── excel_manager.py # Excel file management
│ ├── app.py # Flask API server
│ └── requirements.txt # Python dependencies
├── Frontend/
│ └── index.html # Web interface
├── .gitignore
└── README.md
'''

## 🚀 Installation

### Prerequisites

1. **Python 3.11+**
2. **Tesseract OCR**
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`

### Setup Steps

1. **Clone the repository**
git clone https://github.com/YOUR_USERNAME/Medical-Extracter.git
cd Medical-Extracter


2. **Install Python dependencies**
cd Backend
pip install -r requirements.txt


3. **Configure Tesseract path** (Windows only)
   - Open `Backend/app.py`
   - Uncomment and set the Tesseract path:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


4. **Run the backend server**
    python app.py

Server will start at `http://127.0.0.1:5000`

5. **Open the frontend**
   - Navigate to `Frontend/` folder
   - Open `index.html` in your browser
   - Or use Live Server in VS Code

## 📖 Usage

1. **Upload a Medical Report**
   - Click "Choose File" button
   - Select a medical report (image, PDF, or DOCX)

2. **Analyze Report**
   - Click "🚀 Analyze Report" button
   - Wait for OCR and extraction (3-5 seconds)

3. **View Results**
   - Patient information
   - Laboratory test results in table format
   - Standardized JSON output

4. **Download Excel**
   - Click "📥 Download Excel File"
   - Get consolidated Excel with all processed reports

## 🧪 Supported Report Types

- Liver Function Test (LFT)
- Complete Blood Count (CBC)
- Coagulation Panel (PT/INR/APTT)
- Kidney Function Test
- Lipid Profile
- Thyroid Function Test
- And more...

## 📊 API Endpoints

### Health Check
GET /health
Response: {"status": "OK", "message": "..."}


### Upload & Extract Text Only
POST /upload
Body: multipart/form-data (file)
Response: {"filename": "...", "extracted_text": "..."}


### Analyze Report (Full Extraction)
POST /analyze
Body: multipart/form-data (file)
Response: {
"patient_information": {...},
"order_information": {...},
"lab_tests": [...],
...
}


### Download Excel File
GET /download-excel
Response: Excel file download


### Get Excel Statistics
GET /excel-stats
Response: {"total_records": 150, "unique_patients": 12}


## 🎯 Accuracy

- **Patient Information Extraction**: ~95%
- **Lab Test Detection**: ~90-95% (structured reports)
- **Value Extraction**: ~98%
- **OCR Accuracy**: Depends on image quality (85-99%)

## 🔒 Privacy & Security

- ⚠️ **Do not upload real patient data to public repositories**
- Patient data is stored locally only
- No data is sent to external servers
- Use anonymized/synthetic data for demonstrations

## 🐛 Known Limitations

- Requires good quality images for accurate OCR
- Works best with structured tabular reports
- Handwritten reports not supported
- English language reports only

## 🔮 Future Enhancements

- [ ] Add BioBERT NER model for unstructured text
- [ ] Support for handwritten reports
- [ ] Multi-language support
- [ ] Database integration (MongoDB/PostgreSQL)
- [ ] User authentication system
- [ ] Batch processing for multiple files
- [ ] Export to JSON/CSV formats
- [ ] Advanced data visualization

## 👨‍💻 Author

**Carol Pinto**
- St Aloysius institute of management and information technology, Mangalore
- Software Technology Department
- Email: carolpintopintopinto@gmail.com
- GitHub: [@Carol21Pinto](https://github.com/Carol21Pinto)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Tesseract OCR by Google
- Flask framework
- Python community
- University College, Pune

## 📞 Contact

For questions or suggestions, please open an issue or contact [carolpintopintopinto@gmail.com](mailto:carolpintopintopinto@gmail.com)

---

**Note**: This is an academic project. For production use in healthcare, ensure compliance with HIPAA, GDPR, and local healthcare data regulations.
