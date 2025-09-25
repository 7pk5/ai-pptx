import os
import json
from datetime import datetime
from typing import Dict, Any


def save_analysis_result(result: Dict[str, Any], filename: str = None) -> str:
    """Save analysis result to JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppt_analysis_{timestamp}.json"
    
    filepath = os.path.join("analysis_results", filename)
    os.makedirs("analysis_results", exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return filepath


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def validate_ppt_file(file_path: str) -> Dict[str, Any]:
    """Validate PowerPoint file."""
    result = {
        "valid": False,
        "error": None,
        "file_info": {}
    }
    
    try:
        if not os.path.exists(file_path):
            result["error"] = "File does not exist"
            return result
        
        if not file_path.lower().endswith(('.pptx', '.ppt')):
            result["error"] = "File is not a PowerPoint presentation"
            return result
        
        file_size = os.path.getsize(file_path)
        result["file_info"] = {
            "size": file_size,
            "size_formatted": format_file_size(file_size),
            "extension": os.path.splitext(file_path)[1],
            "filename": os.path.basename(file_path)
        }
        
        result["valid"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def create_color_palette_html(colors: list) -> str:
    """Create HTML for color palette display."""
    if not colors:
        return "<p>No colors detected</p>"
    
    html = '<div class="color-palette">'
    for color in colors[:10]:  # Limit to 10 colors
        if color and color.startswith('#'):
            html += f'<div class="color-swatch" style="background-color: {color};" title="{color}"></div>'
    html += '</div>'
    
    return html


def generate_summary_stats(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary statistics from analysis result."""
    stats = {
        "slides": {
            "total": analysis_result.get("global_analysis", {}).get("total_slides", 0),
            "with_images": 0,
            "text_heavy": 0,
            "visual_heavy": 0
        },
        "content": {
            "total_images": analysis_result.get("global_analysis", {}).get("image_count", 0),
            "unique_colors": len(set(analysis_result.get("global_analysis", {}).get("color_palette", []))),
            "unique_fonts": len(set(analysis_result.get("global_analysis", {}).get("fonts_used", [])))
        },
        "design": {
            "color_diversity": "Unknown",
            "font_consistency": "Unknown",
            "layout_variety": len(set(analysis_result.get("global_analysis", {}).get("slide_layouts", [])))
        }
    }
    
    # Calculate slide statistics
    for slide in analysis_result.get("slides", []):
        if slide.get("image_count", 0) > 0:
            stats["slides"]["with_images"] += 1
        if slide.get("text_count", 0) > 5:
            stats["slides"]["text_heavy"] += 1
        if slide.get("image_count", 0) > 2:
            stats["slides"]["visual_heavy"] += 1
    
    # Determine color diversity
    color_count = stats["content"]["unique_colors"]
    if color_count > 10:
        stats["design"]["color_diversity"] = "High"
    elif color_count > 5:
        stats["design"]["color_diversity"] = "Medium"
    else:
        stats["design"]["color_diversity"] = "Low"
    
    # Determine font consistency
    font_count = stats["content"]["unique_fonts"]
    if font_count <= 3:
        stats["design"]["font_consistency"] = "Good"
    elif font_count <= 6:
        stats["design"]["font_consistency"] = "Moderate"
    else:
        stats["design"]["font_consistency"] = "Poor"
    
    return stats
