import os
import sys
from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    """Simple health check."""
    return jsonify({
        'status': 'healthy',
        'message': 'PPT Analyzer API is running',
        'python_version': sys.version,
        'working_directory': os.getcwd()
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Test imports
        import tempfile
        from flask import render_template
        
        # Test file system access
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b'test')
        
        return jsonify({
            'status': 'healthy',
            'imports': 'ok',
            'filesystem': 'ok'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/test-imports')
def test_imports():
    """Test all required imports."""
    results = {}
    
    # Test basic imports
    try:
        import tempfile
        results['tempfile'] = 'ok'
    except Exception as e:
        results['tempfile'] = str(e)
    
    try:
        from pptx import Presentation
        results['python-pptx'] = 'ok'
    except Exception as e:
        results['python-pptx'] = str(e)
    
    try:
        from PIL import Image
        results['PIL'] = 'ok'
    except Exception as e:
        results['PIL'] = str(e)
    
    try:
        import numpy as np
        results['numpy'] = f'ok - version {np.__version__}'
    except Exception as e:
        results['numpy'] = str(e)
    
    try:
        import cv2
        results['opencv'] = f'ok - version {cv2.__version__}'
    except Exception as e:
        results['opencv'] = str(e)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
