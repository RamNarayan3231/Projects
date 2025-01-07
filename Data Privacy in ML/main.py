from flask import Flask, request, render_template
import re
from PyPDF2 import PdfReader

app = Flask(__name__)

# Regex patterns for detecting sensitive data
patterns = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    "phone": r'\b\d{10}\b',  # Simple pattern: 10 consecutive digits
}

def extract_text_from_pdf(file):
    """
    Extracts text from an uploaded PDF file.
    """
    try:
        reader = PdfReader(file)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text
            else:
                print(f"Warning: No text found on page {page_num + 1}")
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def detect_sensitive_data(text, selected_types):
    """
    Detects sensitive data in the text based on selected data types.
    """
    sensitive_data = {key: [] for key in patterns}
    for key, pattern in patterns.items():
        if key in selected_types:
            matches = re.findall(pattern, text)
            sensitive_data[key] = matches
    print("Detected Sensitive Data:", sensitive_data)  # Debug statement
    return sensitive_data

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template("result.html", error="No file part in the request.", sensitive_data={}, non_sensitive_data="")
        
        file = request.files["file"]
        
        # If user does not select file, browser may submit an empty part without filename
        if file.filename == '':
            return render_template("result.html", error="No selected file.", sensitive_data={}, non_sensitive_data="")
        
        if file:
            selected_types = request.form.getlist("data_type")
            print("Selected Data Types:", selected_types)  # Debug statement

            text = extract_text_from_pdf(file)
            if not text:
                return render_template("result.html", error="No text could be extracted from the PDF.", sensitive_data={}, non_sensitive_data="")
            
            sensitive_data = detect_sensitive_data(text, selected_types)
            
            # Redact sensitive data in the non-sensitive content
            non_sensitive_data = text
            for data_type, data_list in sensitive_data.items():
                for item in data_list:
                    non_sensitive_data = non_sensitive_data.replace(item, "[REDACTED]")
            
            print("Sensitive Data Passed to Template:", sensitive_data)  # Debug statement
            
            return render_template("result.html", sensitive_data=sensitive_data, non_sensitive_data=non_sensitive_data)
    
    return render_template("index.html")

if __name__ == "_main_":
    app.run(debug=True)