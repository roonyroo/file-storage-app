"""
Flask 1xf1 File Storage App - Production Ready
Single file deployment with embedded HTML template
"""

from flask import Flask, request, jsonify, send_file, abort
import os
import datetime
from pathlib import Path

app = Flask(__name__)

# Create directories
UPLOAD_DIR = Path("stored_files")
UPLOAD_DIR.mkdir(exist_ok=True)

# HTML template embedded as string
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask 1xf1 File Storage</title>
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }

        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            font-family: 'Courier New', monospace;
            resize: vertical;
            min-height: 150px;
            transition: border-color 0.3s ease;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn-1xf1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-bottom: 20px;
        }

        .btn-1xf1:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .btn-1xf1:active {
            transform: translateY(0);
        }

        .btn-1xf1:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .status {
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-weight: 500;
            text-align: center;
            transition: all 0.3s ease;
            display: none;
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

        .files-section {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #e1e5e9;
        }

        .files-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .files-header h3 {
            color: #333;
            font-size: 1.5em;
        }

        .refresh-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }

        .refresh-btn:hover {
            background: #218838;
        }

        .file-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .file-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            font-size: 12px;
            color: #666;
        }

        .download-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            text-decoration: none;
            display: inline-block;
        }

        .download-btn:hover {
            background: #0056b3;
        }

        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }

        @media (max-width: 600px) {
            .container {
                margin: 10px;
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗂️ Flask 1xf1 Storage</h1>
            <p>Store text files with the click of a button</p>
        </div>

        <form id="fileForm">
            <div class="form-group">
                <label for="textContent">Enter your text content:</label>
                <textarea 
                    id="textContent" 
                    name="textContent" 
                    placeholder="Type your text here..."
                    required
                ></textarea>
            </div>

            <button type="submit" class="btn-1xf1" id="storeBtn">
                🗂️ Store File (1xf1)
            </button>
        </form>

        <div id="status" class="status"></div>

        <div class="files-section">
            <div class="files-header">
                <h3>📋 Stored Files</h3>
                <button class="refresh-btn" onclick="loadFiles()">🔄 Refresh</button>
            </div>
            <div id="filesList" class="file-list">
                <div class="loading">Loading files...</div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            loadFiles();
        });

        document.getElementById('fileForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const textContent = document.getElementById('textContent').value;
            const storeBtn = document.getElementById('storeBtn');
            const statusDiv = document.getElementById('status');
            
            if (!textContent.trim()) {
                showStatus('Please enter some text content', 'error');
                return;
            }

            // Disable button and show loading
            storeBtn.disabled = true;
            storeBtn.textContent = '⏳ Storing...';
            
            try {
                const response = await fetch('/store-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content: textContent })
                });

                const result = await response.json();

                if (response.ok) {
                    showStatus(`✅ File stored successfully as: ${result.filename}`, 'success');
                    document.getElementById('textContent').value = '';
                    loadFiles(); // Refresh file list
                } else {
                    showStatus(`❌ Error: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            } finally {
                // Re-enable button
                storeBtn.disabled = false;
                storeBtn.textContent = '🗂️ Store File (1xf1)';
            }
        });

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }

        async function loadFiles() {
            const filesList = document.getElementById('filesList');
            filesList.innerHTML = '<div class="loading">Loading files...</div>';
            
            try {
                const response = await fetch('/files');
                const result = await response.json();
                
                if (response.ok && result.files.length > 0) {
                    filesList.innerHTML = result.files.map(file => `
                        <div class="file-item">
                            <div class="file-info">
                                <div class="file-name">${file.filename}</div>
                                <div class="file-meta">
                                    Size: ${formatBytes(file.size)} | 
                                    Created: ${new Date(file.created).toLocaleString()}
                                </div>
                            </div>
                            <a href="/download/${file.filename}" class="download-btn" download>
                                ⬇️ Download
                            </a>
                        </div>
                    `).join('');
                } else {
                    filesList.innerHTML = '<div class="loading">No files stored yet</div>';
                }
            } catch (error) {
                filesList.innerHTML = '<div class="loading">Error loading files</div>';
                console.error('Error loading files:', error);
            }
        }

        function formatBytes(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/store-file', methods=['POST'])
def store_file():
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3]
        filename = f"1xf1-{timestamp}.txt"
        filepath = UPLOAD_DIR / filename
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'message': 'File stored successfully',
            'filename': filename,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files')
def list_files():
    try:
        files = []
        for filepath in UPLOAD_DIR.glob("*.txt"):
            stat = filepath.stat()
            files.append({
                'filename': filepath.name,
                'size': stat.st_size,
                'created': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'files': files})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = UPLOAD_DIR / filename
        if not filepath.exists():
            abort(404)
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        abort(500)

@app.route('/health')
def health():
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🗂️ Flask 1xf1 File Storage App")
    print("=" * 50)
    print("Setup Instructions:")
    print("1. pip install flask")
    print("2. python app.py")
    print("3. Visit: http://localhost:5000")
    print("4. Click the 1xf1 button!")
    print("=" * 50)
    
    # Production-ready settings
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)