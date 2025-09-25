from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'Payload Test API',
        'max_content_length': 100 * 1024,  # 100KB
        'note': 'Testing very small payload limits'
    })

@app.route('/test', methods=['POST'])
def test_payload():
    """Test with extreme payload restrictions."""
    try:
        content_length = request.content_length or 0
        
        # Reject anything over 100KB immediately
        if content_length > 100 * 1024:
            return jsonify({
                'error': 'Too large',
                'content_length': content_length,
                'limit': 100 * 1024
            }), 413
        
        # Get basic request info
        result = {
            'content_length': content_length,
            'method': request.method,
            'has_files': bool(request.files),
            'files_count': len(request.files) if request.files else 0,
            'form_keys': list(request.form.keys()) if request.form else [],
            'headers_content_type': request.headers.get('Content-Type', 'unknown')
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'limit': '100KB'})

if __name__ == '__main__':
    app.run(debug=True)
