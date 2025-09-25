import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import json
import tempfile
import traceback

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize analyzers with error handling
detailed_analyzer = None
groq_analyzer = None

try:
    from src.analyzers.detailed_analyzer_serverless import DetailedPPTAnalyzer
    detailed_analyzer = DetailedPPTAnalyzer()
except ImportError as e:
    print(f"Failed to import serverless analyzer: {e}")
    try:
        from src.analyzers.detailed_analyzer import DetailedPPTAnalyzer
        detailed_analyzer = DetailedPPTAnalyzer()
    except ImportError as e2:
        print(f"Failed to import regular analyzer: {e2}")

try:
    from src.analyzers.groq_analyzer import GroqAnalyzer
    groq_analyzer = GroqAnalyzer()
except ImportError as e:
    print(f"Failed to import Groq analyzer: {e}")

try:
    from src.utils.helpers import validate_ppt_file, save_analysis_result, generate_summary_stats
except ImportError as e:
    print(f"Failed to import helpers: {e}")
    # Provide fallback functions
    def validate_ppt_file(filepath):
        return {"valid": True, "error": None}
    def save_analysis_result(result, filename):
        return True
    def generate_summary_stats(result):
        return {"status": "Summary stats not available"}

app = Flask(__name__, 
           static_folder='../static',
           template_folder='../templates')

# Use environment variable for secret key, fallback to default
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'ppt-ai-analyzer-secret-key-2024')

# Configuration for Vercel - Extremely restrictive limits for serverless
ALLOWED_EXTENSIONS = {'pptx', 'ppt'}
# Vercel has very strict payload limits - reducing to 1MB to be safe
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 1 * 1024 * 1024))  # 1MB maximum for Vercel serverless

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_request_size():
    """Validate request size before processing."""
    content_length = request.content_length
    if content_length and content_length > MAX_FILE_SIZE:
        return False, f'Request too large: {content_length} bytes. Maximum allowed: {MAX_FILE_SIZE} bytes (4MB)'
    return True, None

@app.route('/')
def index():
    """Main page with file upload."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redirect to analysis."""
    try:
        # Validate request size first
        valid_size, size_error = validate_request_size()
        if not valid_size:
            flash(size_error, 'error')
            return redirect(request.url)
            
        if not detailed_analyzer:
            flash('Analysis service unavailable', 'error')
            return redirect(request.url)
            
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        
        try:
            # Use temporary file for Vercel
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx' if filename.endswith('.pptx') else '.ppt') as temp_file:
                file.save(temp_file.name)
                temp_filepath = temp_file.name
            
            # Validate file
            validation = validate_ppt_file(temp_filepath)
            if not validation['valid']:
                flash(f'Invalid file: {validation["error"]}', 'error')
                os.unlink(temp_filepath)  # Clean up
                return redirect(request.url)
            
            # Store the temp file path in session or pass as parameter
            # For simplicity, we'll analyze immediately and store results
            try:
                # Perform detailed analysis
                detailed_result = detailed_analyzer.parse_ppt_detailed(temp_filepath)
                
                # Get AI insights
                ai_analysis = groq_analyzer.analyze_presentation(detailed_result)
                
                # Generate summary statistics
                summary_stats = generate_summary_stats(detailed_result)
                
                # Combine results
                final_result = {
                    'filename': filename,
                    'detailed_analysis': detailed_result,
                    'ai_insights': ai_analysis,
                    'summary_stats': summary_stats
                }
                
                # Clean up temp file
                os.unlink(temp_filepath)
                
                # Store results in session (note: in production, use a database)
                session_key = f"analysis_{filename}_{hash(str(final_result)[:100])}"
                
                # For demo purposes, we'll pass the result directly
                return render_template('analysis.html', 
                                     result=final_result, 
                                     filename=filename)
                
            except Exception as e:
                print(f"Analysis error: {traceback.format_exc()}")
                if os.path.exists(temp_filepath):
                    os.unlink(temp_filepath)
                flash(f'Error analyzing file: {str(e)}', 'error')
                return redirect(request.url)
            
        except Exception as e:
            print(f"Upload error: {traceback.format_exc()}")
            flash(f'Error uploading file: {str(e)}', 'error')
            return redirect(request.url)
    
        else:
            flash('Invalid file type. Please upload a .pptx or .ppt file', 'error')
            return redirect(request.url)
    
    except Exception as e:
        print(f"General error: {traceback.format_exc()}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for programmatic analysis."""
    try:
        # Validate request size first
        valid_size, size_error = validate_request_size()
        if not valid_size:
            return jsonify({'error': size_error}), 413
            
        if not detailed_analyzer:
            return jsonify({'error': 'Analysis service unavailable'}), 503
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        filename = secure_filename(file.filename)
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx' if filename.endswith('.pptx') else '.ppt') as temp_file:
            file.save(temp_file.name)
            temp_filepath = temp_file.name
        
        # Validate file
        validation = validate_ppt_file(temp_filepath)
        if not validation['valid']:
            os.unlink(temp_filepath)
            return jsonify({'error': validation['error']}), 400
        
        # Perform analysis
        detailed_result = detailed_analyzer.parse_ppt_detailed(temp_filepath)
        ai_analysis = groq_analyzer.analyze_presentation(detailed_result)
        summary_stats = generate_summary_stats(detailed_result)
        
        result = {
            'filename': filename,
            'detailed_analysis': detailed_result,
            'ai_insights': ai_analysis,
            'summary_stats': summary_stats
        }
        
        # Clean up temp file
        os.unlink(temp_filepath)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel."""
    return jsonify({
        'status': 'healthy',
        'service': 'PPT AI Analyzer',
        'version': '1.0.0',
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    })

@app.route('/api/limits')
def get_limits():
    """Get current API limits."""
    return jsonify({
        'max_file_size_bytes': MAX_FILE_SIZE,
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024),
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'serverless': True
    })

@app.route('/api/test-payload', methods=['POST'])
def test_payload():
    """Test endpoint to check payload size handling."""
    try:
        content_length = request.content_length or 0
        
        # Get request size info
        result = {
            'content_length': content_length,
            'content_length_mb': content_length / (1024 * 1024),
            'max_allowed_mb': MAX_FILE_SIZE / (1024 * 1024),
            'within_limits': content_length <= MAX_FILE_SIZE,
            'has_files': bool(request.files),
            'file_count': len(request.files) if request.files else 0
        }
        
        if request.files:
            for key, file in request.files.items():
                if hasattr(file, 'filename') and file.filename:
                    # Read file size without saving
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    result['file_info'] = {
                        'filename': file.filename,
                        'size_bytes': file_size,
                        'size_mb': file_size / (1024 * 1024)
                    }
                    break
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.errorhandler(413) 
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File is too large. Maximum file size is 1MB for Vercel serverless. Please use a very small PowerPoint file.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

# For Vercel, the app instance needs to be available at module level
# Vercel will automatically handle the WSGI interface

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
