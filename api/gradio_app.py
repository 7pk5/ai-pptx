import os
import sys
import tempfile
import traceback
import gradio as gr

# Add parent directory to path
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

# Configuration
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB for Vercel serverless
ALLOWED_EXTENSIONS = ['.pptx', '.ppt']

def analyze_ppt(file):
    """Analyze PowerPoint file using Gradio interface."""
    try:
        if file is None:
            return "❌ No file uploaded. Please select a PowerPoint file."
        
        # Check file size
        file_size = os.path.getsize(file.name)
        if file_size > MAX_FILE_SIZE:
            return f"❌ File too large: {file_size / (1024*1024):.2f}MB. Maximum allowed: 1MB for serverless deployment."
        
        # Check file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return f"❌ Invalid file type: {file_ext}. Please upload a .pptx or .ppt file."
        
        if not detailed_analyzer:
            return "❌ Analysis service unavailable. Please check server configuration."
        
        # Perform analysis
        detailed_result = detailed_analyzer.parse_ppt_detailed(file.name)
        
        # Format results for display
        output = []
        output.append("# 📊 PowerPoint Analysis Results\n")
        
        # Basic info
        if 'presentation_info' in detailed_result:
            info = detailed_result['presentation_info']
            output.append(f"**File:** {os.path.basename(file.name)}")
            output.append(f"**Total Slides:** {detailed_result['global_analysis']['total_slides']}")
            output.append(f"**Dimensions:** {info.get('slide_dimensions', 'Unknown')}")
            output.append("")
        
        # Global analysis
        if 'global_analysis' in detailed_result:
            global_info = detailed_result['global_analysis']
            output.append("## 🎨 Design Overview")
            output.append(f"**Total Images:** {global_info.get('image_count', 0)}")
            output.append(f"**Unique Colors:** {len(set(global_info.get('color_palette', [])))}")
            output.append(f"**Fonts Used:** {len(set(global_info.get('fonts_used', [])))}")
            output.append("")
            
            # Top colors
            if global_info.get('color_palette'):
                colors = list(set(global_info['color_palette'][:10]))
                output.append("**Top Colors:** " + ", ".join(colors))
                output.append("")
            
            # Fonts
            if global_info.get('fonts_used'):
                fonts = list(set(global_info['fonts_used'][:5]))
                output.append("**Fonts:** " + ", ".join(fonts))
                output.append("")
        
        # Slide breakdown
        if 'slides' in detailed_result and detailed_result['slides']:
            output.append("## 📋 Slide Details")
            for slide in detailed_result['slides'][:5]:  # Show first 5 slides
                output.append(f"**Slide {slide['slide_number']}:**")
                output.append(f"- Layout: {slide.get('layout', 'Unknown')}")
                output.append(f"- Text items: {slide.get('text_count', 0)}")
                output.append(f"- Images: {slide.get('image_count', 0)}")
                output.append(f"- Shapes: {slide.get('shape_count', 0)}")
                output.append("")
        
        # AI Analysis (if available)
        if groq_analyzer:
            try:
                ai_analysis = groq_analyzer.analyze_presentation(detailed_result)
                if ai_analysis and 'error' not in ai_analysis:
                    output.append("## 🤖 AI Insights")
                    if 'presentation_topic' in ai_analysis:
                        output.append(f"**Topic:** {ai_analysis['presentation_topic']}")
                    if 'design_score' in ai_analysis:
                        output.append(f"**Design Score:** {ai_analysis['design_score']}/10")
                    if 'content_score' in ai_analysis:
                        output.append(f"**Content Score:** {ai_analysis['content_score']}/10")
                    output.append("")
            except Exception as e:
                output.append(f"## ⚠️ AI Analysis: {str(e)}")
                output.append("")
        
        output.append("---")
        output.append("✅ Analysis completed successfully!")
        
        return "\n".join(output)
        
    except Exception as e:
        error_msg = f"❌ Analysis failed: {str(e)}\n\n"
        error_msg += f"**Error Details:**\n```\n{traceback.format_exc()}\n```"
        return error_msg

def get_app_info():
    """Get application information."""
    info = []
    info.append("# 🎯 PowerPoint AI Analyzer")
    info.append("")
    info.append("**Features:**")
    info.append("- 📊 Comprehensive slide analysis")
    info.append("- 🎨 Color palette extraction")
    info.append("- 🖼️ Image analysis")
    info.append("- 📝 Text and font analysis")
    info.append("- 🤖 AI-powered insights (when available)")
    info.append("")
    info.append("**Limits:**")
    info.append(f"- Maximum file size: {MAX_FILE_SIZE / (1024*1024):.0f}MB")
    info.append("- Supported formats: .pptx, .ppt")
    info.append("- Optimized for Vercel serverless deployment")
    info.append("")
    info.append("**Usage:** Upload your PowerPoint file and click 'Analyze' to get detailed insights!")
    
    return "\n".join(info)

# Create Gradio interface
with gr.Blocks(
    title="PowerPoint AI Analyzer",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 800px !important;
        margin: auto !important;
    }
    """
) as demo:
    
    gr.Markdown("# 🎯 PowerPoint AI Analyzer")
    gr.Markdown("Upload your PowerPoint file to get comprehensive analysis with AI insights!")
    
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="📁 Upload PowerPoint File",
                file_types=[".pptx", ".ppt"],
                file_count="single"
            )
            
            analyze_btn = gr.Button(
                "🔍 Analyze Presentation", 
                variant="primary",
                size="lg"
            )
            
            gr.Markdown(f"""
            **📋 Requirements:**
            - File size: Max {MAX_FILE_SIZE / (1024*1024):.0f}MB
            - Formats: .pptx, .ppt
            - Processing time: ~10-30 seconds
            """)
    
    with gr.Row():
        output = gr.Markdown(
            value=get_app_info(),
            label="Analysis Results"
        )
    
    # Event handlers
    analyze_btn.click(
        fn=analyze_ppt,
        inputs=[file_input],
        outputs=[output],
        show_progress=True
    )
    
    # Example section
    gr.Markdown("""
    ---
    ### 📖 How to Use:
    1. **Upload** your PowerPoint file (.pptx or .ppt)
    2. **Click** the "Analyze Presentation" button
    3. **Wait** for the analysis to complete (10-30 seconds)
    4. **Review** the comprehensive results including colors, fonts, images, and AI insights
    
    ### 🔧 Technical Details:
    - Serverless deployment optimized for Vercel
    - Advanced image processing and color extraction
    - AI-powered content analysis using Groq LLM
    - Secure temporary file handling
    """)

# For Vercel deployment
app = demo

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
