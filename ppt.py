"""
Legacy PPT Analyzer - Enhanced Version
This file maintains backward compatibility while using the new enhanced analyzers.
"""

import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.analyzers.detailed_analyzer import DetailedPPTAnalyzer
from src.analyzers.groq_analyzer import GroqAnalyzer

# Legacy function for backward compatibility
def parse_ppt(file_path):
    """
    Legacy function - now uses enhanced analyzer but returns simplified format
    for backward compatibility.
    """
    analyzer = DetailedPPTAnalyzer()
    detailed_result = analyzer.parse_ppt_detailed(file_path)
    
    # Convert to legacy format
    slides_data = []
    for slide in detailed_result['slides']:
        slides_data.append({
            "slide_number": slide["slide_number"],
            "layout": slide["layout"],
            "text": slide["texts"],
            "has_image": slide["image_count"] > 0
        })
    
    return slides_data


def analyze_with_groq(slides_data):
    """
    Legacy function - now uses enhanced Groq analyzer.
    """
    # Convert legacy format to detailed format for analysis
    mock_detailed_data = {
        "global_analysis": {
            "total_slides": len(slides_data),
            "image_count": sum(1 for slide in slides_data if slide.get("has_image", False)),
            "color_palette": [],
            "fonts_used": [],
            "slide_layouts": [slide.get("layout", "Unknown") for slide in slides_data]
        },
        "slides": []
    }
    
    for slide in slides_data:
        mock_slide = {
            "slide_number": slide["slide_number"],
            "layout": slide["layout"],
            "texts": slide["text"] if isinstance(slide["text"], list) else [slide["text"]],
            "image_count": 1 if slide.get("has_image", False) else 0,
            "text_count": len(slide["text"]) if isinstance(slide["text"], list) else (1 if slide["text"] else 0),
            "colors": [],
            "fonts": []
        }
        mock_detailed_data["slides"].append(mock_slide)
    
    # Add presentation info
    mock_detailed_data["presentation_info"] = {
        "slide_dimensions": {
            "width": 9144000,
            "height": 6858000,
            "width_inches": 10.0,
            "height_inches": 7.5,
            "aspect_ratio": 1.33
        }
    }
    
    analyzer = GroqAnalyzer()
    ai_analysis = analyzer.analyze_presentation(mock_detailed_data)
    
    return ai_analysis.get("raw_analysis", "Analysis completed successfully.")


# Enhanced functions for users who want more detailed analysis
def analyze_ppt_detailed(file_path):
    """
    Enhanced analysis function that returns comprehensive details.
    """
    analyzer = DetailedPPTAnalyzer()
    return analyzer.parse_ppt_detailed(file_path)


def get_ai_insights(detailed_data):
    """
    Get AI insights from detailed analysis data.
    """
    analyzer = GroqAnalyzer()
    return analyzer.analyze_presentation(detailed_data)


if __name__ == "__main__":
    file_path = "aissms.pptx"   # replace with your PPT path

    slides = parse_ppt(file_path)
    print("Extracted Slide Data:", slides)

    insights = analyze_with_groq(slides)
    print("\nGroq LLM Insights:\n", insights)
