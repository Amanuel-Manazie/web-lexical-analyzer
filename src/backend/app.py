from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from lexer_engine import tokenize
from docx_parser import extract_text_from_docx

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

# ------------------- ROUTES -------------------

@app.route('/')
def serve_frontend():
    """Serve the main index.html"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/tokenize', methods=['POST'])
def handle_tokenize():
    """Receive code in JSON, return tokens"""
    data = request.get_json()
    source_code = data.get('code', '')

    if not source_code:
        return jsonify({'error': 'No code provided'}), 400

    # Call the REAL lexical engine
    tokens = tokenize(source_code)
    return jsonify({'tokens': tokens})

@app.route('/upload', methods=['POST'])
def handle_upload():
    """Receive a file, extract text, tokenize it"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename
    ext = filename.split('.')[-1].lower()

    try:
        # Extract raw text based on file type
        if ext in ['txt', 'py', 'cpp', 'c', 'java', 'js', 'html', 'css']:
            text = file.read().decode('utf-8')
        elif ext == 'docx':
            text = extract_text_from_docx(file)
        else:
            return jsonify({'error': f'Unsupported file type: .{ext}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500

    # Tokenize the extracted text
    tokens = tokenize(text)
    return jsonify({'tokens': tokens, 'source': text})

# ------------------- RUN -------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)