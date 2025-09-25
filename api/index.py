import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import json
import tempfile

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.analyzers.detailed_analyzer_serverless import DetailedPPTAnalyzer
except ImportError:
    from src.analyzers.detailed_analyzer import DetailedPPTAnalyzer
from src.analyzers.groq_analyzer import GroqAnalyzer
from src.utils.helpers import validate_ppt_file, save_analysis_result, generate_summary_stats

app = Flask(__name__, 
           static_folder='../static',
           template_folder='../templates')

# Use environment variable for secret key, fallback to default
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'ppt-ai-analyzer-secret-key-2024')

# Configuration for Vercel
ALLOWED_EXTENSIONS = {'pptx', 'ppt'}
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # Default 50MB

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize analyzers
detailed_analyzer = DetailedPPTAnalyzer()
groq_analyzer = GroqAnalyzer()

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with file upload."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redirect to analysis."""
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
                if os.path.exists(temp_filepath):
                    os.unlink(temp_filepath)
                flash(f'Error analyzing file: {str(e)}', 'error')
                return redirect(request.url)
            
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'error')
            return redirect(request.url)
    else:
        flash('Invalid file type. Please upload a .pptx or .ppt file', 'error')
        return redirect(request.url)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for programmatic analysis."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
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
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel."""
    return jsonify({
        'status': 'healthy',
        'service': 'PPT AI Analyzer',
        'version': '1.0.0'
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File is too large. Maximum file size is 50MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

# Vercel requires the app to be available as a WSGI application
def handler(request, context):
    """Vercel handler function."""
    return app(request, context)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
