# PowerPoint AI Analyzer 🎯

A comprehensive Gradio-based application that analyzes PowerPoint presentations using AI to extract detailed insights about design, content, colors, images, and provides intelligent recommendations.

## Features ✨

- **Comprehensive Analysis**: Deep dive into slide layouts, text content, and visual elements
- **Color Intelligence**: Extract and analyze color palettes with dominant color detection  
- **Image Processing**: Advanced image analysis with color extraction and properties
- **AI-Powered Insights**: Groq LLM integration for intelligent presentation analysis
- **Gradio Interface**: Simple, intuitive web interface with file upload
- **Serverless Optimized**: Lightweight design perfect for Vercel deployment
- **Real-time Processing**: Upload and analyze presentations instantly

## Project Structure

```
PPTAI/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── api/
│   └── gradio_app.py              # Main Gradio application
├── src/
│   ├── analyzers/
│   │   ├── detailed_analyzer.py    # Comprehensive PPT analysis
│   │   ├── detailed_analyzer_serverless.py  # Serverless optimized version
│   │   └── groq_analyzer.py        # AI-powered insights
│   └── utils/
│       └── helpers.py              # Utility functions
├── uploads/                        # Uploaded files (temporary)
└── vercel.json                     # Vercel deployment config
```

## Installation

1. **Clone or download the project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional):
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   ```
   
   Note: The app includes a default API key, but it's recommended to use your own for production.

## Usage

### Web Interface

1. **Start the Flask application**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Upload a PowerPoint file** (.pptx or .ppt format, up to 50MB)

4. **View comprehensive analysis results** including:
   - AI-powered insights and recommendations
   - Color palette analysis
   - Slide-by-slide breakdown
   - Image analysis with dominant colors
   - Font usage statistics
   - Design quality scores

### API Usage

You can also use the API endpoint for programmatic access:

```bash
curl -X POST -F "file=@your-presentation.pptx" http://localhost:5000/api/analyze
```

### Command Line Usage (Legacy)

You can still use the original command-line interface by creating a simple script:

```python
from src.analyzers.detailed_analyzer import DetailedPPTAnalyzer
from src.analyzers.groq_analyzer import GroqAnalyzer

# Initialize analyzers
detailed_analyzer = DetailedPPTAnalyzer()
groq_analyzer = GroqAnalyzer()

# Analyze presentation
file_path = "your-presentation.pptx"
detailed_result = detailed_analyzer.parse_ppt_detailed(file_path)
ai_insights = groq_analyzer.analyze_presentation(detailed_result)

print("Analysis complete!")
```

## What the Tool Analyzes

### 🎨 Visual Elements
- **Colors**: Hex codes, color names, psychological associations
- **Images**: Dominant colors, brightness, dimensions, format
- **Shapes**: Position, size, fill colors, line colors
- **Background**: Colors, gradients, images

### 📝 Content Elements
- **Text**: Content extraction, font analysis, formatting
- **Typography**: Font names, sizes, styles (bold, italic, underline)
- **Layout**: Slide layouts, content organization
- **Structure**: Slide types, content hierarchy

### 🧠 AI Analysis
- **Topic Identification**: What the presentation is about
- **Design Quality**: Professional design assessment
- **Content Quality**: Information organization and clarity
- **Recommendations**: Specific improvement suggestions
- **Classification**: Slide types and presentation category

### 📊 Statistical Analysis
- **Content Distribution**: Text vs visual elements
- **Color Diversity**: Palette richness assessment
- **Font Consistency**: Typography coherence
- **Layout Variety**: Design variation analysis

## Technical Features

- **Comprehensive Color Extraction**: Uses multiple methods including ColorThief and OpenCV
- **Image Processing**: PIL/Pillow for image analysis and color extraction
- **AI Integration**: Groq LLM for intelligent insights
- **Modern UI**: Bootstrap 5 with custom styling
- **Responsive Design**: Works on desktop and mobile
- **Interactive Elements**: Click-to-copy colors, expandable sections
- **Progress Indication**: Real-time upload and analysis progress
- **Error Handling**: Robust error handling and user feedback

## File Support

- **Supported Formats**: .pptx, .ppt
- **Maximum File Size**: 50MB
- **Image Formats**: All formats supported by PIL/Pillow
- **Color Spaces**: RGB, with automatic conversion

## API Endpoints

- `GET /` - Main upload interface
- `POST /upload` - File upload handler
- `GET /analyze/<filename>` - Analysis results page
- `GET /slide/<filename>/<slide_number>` - Individual slide details
- `POST /api/analyze` - API endpoint for programmatic access

## Dependencies

### Core Libraries
- **python-pptx**: PowerPoint file parsing
- **Flask**: Web framework
- **Pillow**: Image processing
- **OpenCV**: Advanced image analysis
- **NumPy**: Numerical operations

### AI & Analysis
- **Groq**: AI-powered insights
- **ColorThief**: Dominant color extraction
- **webcolors**: Color name resolution

### UI & Visualization
- **Bootstrap 5**: UI framework
- **Chart.js**: Data visualization
- **Font Awesome**: Icons

## Customization

### Adding New Analysis Features
1. Extend the `DetailedPPTAnalyzer` class
2. Add new methods for specific analysis
3. Update the UI templates to display new data

### Modifying AI Prompts
1. Edit the `_create_analysis_prompt` method in `GroqAnalyzer`
2. Customize the analysis criteria and output format

### UI Customization
1. Modify `static/css/style.css` for styling
2. Update templates in the `templates/` directory
3. Add custom JavaScript in `static/js/script.js`

## Error Handling

The application includes comprehensive error handling:
- File validation (type, size, format)
- Graceful fallbacks for missing data
- User-friendly error messages
- Detailed logging for debugging

## Security Considerations

- File upload restrictions (type and size)
- Secure filename handling
- Input sanitization
- API key management recommendations

## Performance Optimization

- Efficient color extraction algorithms
- Optimized image processing
- Lazy loading for large presentations
- Caching of analysis results

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Responsive design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Support

For issues or questions:
1. Check the error messages and console logs
2. Verify file format and size requirements
3. Ensure all dependencies are installed
4. Check the Flask application logs

## Future Enhancements

- **Chart Analysis**: Detect and analyze embedded charts
- **Animation Detection**: Identify slide transitions and animations
- **Accessibility Scoring**: Color contrast and readability analysis
- **Brand Consistency**: Logo and brand element detection
- **Template Matching**: Identify presentation templates
- **Export Options**: PDF reports, JSON data export
- **Batch Processing**: Analyze multiple presentations
- **Cloud Integration**: Direct integration with cloud storage

---

*Enhanced PPT Analysis Tool with AI-Powered Insights and Modern Web Interface*
