#!/usr/bin/env python3
"""
Enhanced Flask 1xf1 App with Whisper Integration
Combines text file storage with audio transcription using faster-whisper
"""

import os
import json
import tempfile
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'stored_files'
AUDIO_FOLDER = 'audio_uploads'
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg'}

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def transcribe_audio_faster_whisper(audio_path):
    """
    Transcribe audio using faster-whisper (matching your whisper_gui.py logic)
    """
    try:
        # Import faster-whisper (same as your GUI)
        from faster_whisper import WhisperModel
        
        # Load model (using small model like your GUI default)
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        # Transcribe (matching your GUI's transcription method)
        segments, info = model.transcribe(audio_path, language="en")
        
        # Collect transcription (same logic as your GUI)
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
        
        return transcription.strip()
        
    except ImportError:
        return "Error: faster-whisper not installed. Please install: pip install faster-whisper"
    except Exception as e:
        return f"Transcription error: {str(e)}"

# HTML Template - Enhanced with audio upload
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1xf1 File Storage + Whisper Transcription</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .section {
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9ff;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }

        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .textarea-container {
            position: relative;
            margin-bottom: 20px;
        }

        textarea {
            width: 100%;
            min-height: 150px;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s ease;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .file-input-container {
            margin-bottom: 20px;
        }

        .file-input {
            display: none;
        }

        .file-input-label {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s ease;
            font-weight: 500;
        }

        .file-input-label:hover {
            transform: translateY(-2px);
        }

        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }

        .button:active {
            transform: translateY(-1px);
        }

        .button.secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            font-weight: 500;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .status.info {
            background: #cce7ff;
            color: #004085;
            border: 1px solid #b8daff;
        }

        .file-list {
            margin-top: 30px;
        }

        .file-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
        }

        .file-info {
            flex: 1;
        }

        .file-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }

        .file-meta {
            font-size: 0.9rem;
            color: #666;
        }

        .file-actions {
            display: flex;
            gap: 10px;
        }

        .btn-small {
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 6px;
            text-decoration: none;
            color: white;
            background: #667eea;
            transition: background 0.2s ease;
        }

        .btn-small:hover {
            background: #5a6fd8;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .hotkey-info {
            background: #e8f4fd;
            border: 1px solid #b8daff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #004085;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗂️ 1xf1 Storage + 🎙️ Whisper</h1>
            <p>Store text instantly or transcribe audio to text files</p>
        </div>

        <div class="content">
            <!-- Hotkey Info -->
            <div class="hotkey-info">
                <strong>Local Hotkey Recording:</strong> For global hotkey recording (press ' to start, CapsLock to stop), 
                run the local script that will upload to this web app automatically.
            </div>

            <!-- Text Storage Section -->
            <div class="section">
                <h2>📝 Text File Storage (1xf1)</h2>
                <div class="textarea-container">
                    <textarea id="textContent" placeholder="Type your text here and click the 1xf1 button to store it instantly as a timestamped file..."></textarea>
                </div>
                <button class="button" onclick="storeText()">
                    🗂️ Store File (1xf1)
                </button>
            </div>

            <!-- Audio Transcription Section -->
            <div class="section">
                <h2>🎙️ Audio Transcription</h2>
                <div class="file-input-container">
                    <label for="audioFile" class="file-input-label">
                        📁 Choose Audio File
                    </label>
                    <input type="file" id="audioFile" class="file-input" accept=".wav,.mp3,.mp4,.m4a,.flac,.ogg" onchange="showSelectedFile()">
                </div>
                <div id="selectedFile" style="margin: 10px 0; font-style: italic; color: #666;"></div>
                <button class="button secondary" onclick="transcribeAudio()">
                    🎙️ Transcribe & Store
                </button>
                <div class="loading" id="transcriptionLoading">
                    <div class="spinner"></div>
                    <p>Transcribing audio with faster-whisper... This may take a moment.</p>
                </div>
            </div>

            <!-- Status Messages -->
            <div id="statusMessage"></div>

            <!-- File List Section -->
            <div class="section">
                <h2>📋 Stored Files</h2>
                <button class="button" onclick="refreshFiles()" style="margin-bottom: 20px;">
                    🔄 Refresh List
                </button>
                <div id="fileList" class="file-list">
                    <p>Loading files...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }

        function showSelectedFile() {
            const fileInput = document.getElementById('audioFile');
            const selectedFileDiv = document.getElementById('selectedFile');
            
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                selectedFileDiv.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            } else {
                selectedFileDiv.textContent = '';
            }
        }

        async function storeText() {
            const text = document.getElementById('textContent').value.trim();
            
            if (!text) {
                showStatus('Please enter some text first!', 'error');
                return;
            }

            try {
                const response = await fetch('/store-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content: text })
                });

                const result = await response.json();
                
                if (response.ok) {
                    showStatus(`✅ File stored successfully: ${result.filename}`, 'success');
                    document.getElementById('textContent').value = '';
                    refreshFiles();
                } else {
                    showStatus(`❌ Error: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        }

        async function transcribeAudio() {
            const fileInput = document.getElementById('audioFile');
            const loadingDiv = document.getElementById('transcriptionLoading');
            
            if (!fileInput.files.length) {
                showStatus('Please select an audio file first!', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('audio', fileInput.files[0]);

            try {
                loadingDiv.style.display = 'block';
                showStatus('🎙️ Starting transcription with faster-whisper...', 'info');

                const response = await fetch('/transcribe-audio', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                loadingDiv.style.display = 'none';
                
                if (response.ok) {
                    showStatus(`✅ Audio transcribed and stored: ${result.filename}`, 'success');
                    fileInput.value = '';
                    document.getElementById('selectedFile').textContent = '';
                    refreshFiles();
                } else {
                    showStatus(`❌ Transcription error: ${result.error}`, 'error');
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        }

        async function refreshFiles() {
            try {
                const response = await fetch('/list-files');
                const files = await response.json();
                
                const fileListDiv = document.getElementById('fileList');
                
                if (files.length === 0) {
                    fileListDiv.innerHTML = '<p style="text-align: center; color: #666;">No files stored yet. Create your first file!</p>';
                    return;
                }

                fileListDiv.innerHTML = files.map(file => `
                    <div class="file-item">
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-meta">Size: ${file.size} | Created: ${file.created}</div>
                        </div>
                        <div class="file-actions">
                            <a href="/download/${file.name}" class="btn-small">⬇️ Download</a>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById('fileList').innerHTML = '<p style="color: #721c24;">Error loading files.</p>';
            }
        }

        // Load files on page load
        document.addEventListener('DOMContentLoaded', refreshFiles);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/store-file', methods=['POST'])
def store_file():
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Generate timestamp-based filename (matching your 1xf1 pattern)
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%f')[:-3]
        filename = f'1xf1-{timestamp}.txt'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File stored successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio_endpoint():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_audio_file(audio_file.filename):
            return jsonify({'error': 'Invalid audio file type'}), 400
        
        # Save uploaded audio file temporarily
        file_id = str(uuid.uuid4())
        temp_filename = f"temp_audio_{file_id}_{audio_file.filename}"
        temp_path = os.path.join(AUDIO_FOLDER, temp_filename)
        audio_file.save(temp_path)
        
        try:
            # Transcribe using faster-whisper (matching your GUI logic)
            transcription = transcribe_audio_faster_whisper(temp_path)
            
            # Generate timestamp-based filename for transcription
            timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%f')[:-3]
            original_name = os.path.splitext(audio_file.filename)[0]
            filename = f'whisper-{original_name}-{timestamp}.txt'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save transcription as text file (matching your GUI format)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Audio Transcription (faster-whisper)\n")
                f.write(f"Original file: {audio_file.filename}\n")
                f.write(f"Transcribed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Model: small (faster-whisper)\n")
                f.write(f"---\n\n")
                f.write(transcription)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'transcription': transcription[:200] + '...' if len(transcription) > 200 else transcription,
                'message': 'Audio transcribed and stored successfully'
            })
            
        finally:
            # Clean up temporary audio file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-audio', methods=['POST'])
def upload_audio_for_hotkey():
    """
    Special endpoint for the local hotkey script to upload audio
    This will be used by the local Python script with global hotkeys
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Process the same way as the web interface
        file_id = str(uuid.uuid4())
        temp_filename = f"hotkey_audio_{file_id}.wav"  # Assume WAV from local recording
        temp_path = os.path.join(AUDIO_FOLDER, temp_filename)
        audio_file.save(temp_path)
        
        try:
            # Transcribe using faster-whisper
            transcription = transcribe_audio_faster_whisper(temp_path)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%f')[:-3]
            filename = f'hotkey-recording-{timestamp}.txt'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save transcription
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Hotkey Recording Transcription\n")
                f.write(f"Recorded via: Global hotkeys (' start, CapsLock stop)\n")
                f.write(f"Transcribed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Model: faster-whisper small\n")
                f.write(f"---\n\n")
                f.write(transcription)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'transcription': transcription,
                'message': 'Hotkey recording transcribed and stored'
            })
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list-files', methods=['GET'])
def list_files():
    try:
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'name': filename,
                        'size': f"{stat.st_size} bytes",
                        'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
