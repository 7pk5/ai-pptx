import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import json

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.analyzers.detailed_analyzer import DetailedPPTAnalyzer
from src.analyzers.groq_analyzer import GroqAnalyzer
from src.utils.helpers import validate_ppt_file, save_analysis_result, generate_summary_stats

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pptx', 'ppt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            
            # Validate file
            validation = validate_ppt_file(filepath)
            if not validation['valid']:
                flash(f'Invalid file: {validation["error"]}', 'error')
                os.remove(filepath)  # Clean up
                return redirect(request.url)
            
            return redirect(url_for('analyze', filename=filename))
            
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'error')
            return redirect(request.url)
    else:
        flash('Invalid file type. Please upload a .pptx or .ppt file', 'error')
        return redirect(request.url)


@app.route('/analyze/<filename>')
def analyze(filename):
    """Analyze uploaded PowerPoint file."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Perform detailed analysis
        detailed_result = detailed_analyzer.parse_ppt_detailed(filepath)
        
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
        
        # Save results
        result_file = save_analysis_result(final_result, f"{filename}_analysis.json")
        
        return render_template('analysis.html', 
                             result=final_result, 
                             filename=filename)
        
    except Exception as e:
        flash(f'Error analyzing file: {str(e)}', 'error')
        return redirect(url_for('index'))


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
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate file
        validation = validate_ppt_file(filepath)
        if not validation['valid']:
            os.remove(filepath)
            return jsonify({'error': validation['error']}), 400
        
        # Perform analysis
        detailed_result = detailed_analyzer.parse_ppt_detailed(filepath)
        ai_analysis = groq_analyzer.analyze_presentation(detailed_result)
        summary_stats = generate_summary_stats(detailed_result)
        
        result = {
            'filename': filename,
            'detailed_analysis': detailed_result,
            'ai_insights': ai_analysis,
            'summary_stats': summary_stats
        }
        
        # Clean up file
        os.remove(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/slide/<filename>/<int:slide_number>')
def slide_detail(filename, slide_number):
    """Show detailed view of a specific slide."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    try:
        detailed_result = detailed_analyzer.parse_ppt_detailed(filepath)
        
        # Find the specific slide
        slide_data = None
        for slide in detailed_result['slides']:
            if slide['slide_number'] == slide_number:
                slide_data = slide
                break
        
        if not slide_data:
            flash('Slide not found', 'error')
            return redirect(url_for('analyze', filename=filename))
        
        return render_template('slide_detail.html', 
                             slide=slide_data, 
                             filename=filename,
                             total_slides=detailed_result['global_analysis']['total_slides'])
        
    except Exception as e:
        flash(f'Error loading slide: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum file size is 50MB.', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
