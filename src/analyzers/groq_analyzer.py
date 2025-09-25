from groq import Groq
from typing import Dict, Any, List
import json


class GroqAnalyzer:
    """Enhanced Groq analyzer for comprehensive PPT insights."""
    
    def __init__(self, api_key: str = None):
        import os
        if not api_key:
            # Try environment variable - no fallback key for security
            api_key = os.getenv('GROQ_API_KEY')
        
        try:
            if api_key:
                from groq import Groq
                self.client = Groq(api_key=api_key)
            else:
                print("Warning: No GROQ_API_KEY found in environment variables")
                self.client = None
        except Exception as e:
            print(f"Warning: Could not initialize Groq client: {e}")
            print("AI analysis will be limited to basic heuristics")
            self.client = None
    
    def analyze_presentation(self, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze presentation with comprehensive insights."""
        
        if not self.client:
            return {"error": "Groq client not initialized"}
        
        # Create structured prompt
        prompt = self._create_analysis_prompt(detailed_data)
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            # Parse the analysis into structured format
            structured_analysis = self._parse_analysis(analysis, detailed_data)
            
            return structured_analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt."""
        
        # Summarize key information for the prompt
        summary = {
            "total_slides": data["global_analysis"]["total_slides"],
            "total_images": data["global_analysis"]["image_count"],
            "color_palette": data["global_analysis"]["color_palette"][:10],  # Limit colors
            "fonts_used": data["global_analysis"]["fonts_used"][:10],  # Limit fonts
            "slide_layouts": list(set(data["global_analysis"]["slide_layouts"])),
            "presentation_dimensions": data["presentation_info"]["slide_dimensions"]
        }
        
        # Sample slide data (first 3 slides to avoid token limits)
        sample_slides = data["slides"][:3]
        
        prompt = f"""
You are an expert presentation analyst. Analyze this PowerPoint presentation data and provide comprehensive insights.

PRESENTATION OVERVIEW:
{json.dumps(summary, indent=2)}

SAMPLE SLIDES DATA:
{json.dumps(sample_slides, indent=2)}

Please provide a detailed analysis covering:

1. PRESENTATION PURPOSE & TOPIC:
   - What is this presentation about?
   - What's the main topic or theme?
   - Target audience assessment

2. DESIGN ANALYSIS:
   - Overall design quality (1-10 scale)
   - Color scheme analysis (professional/creative/etc.)
   - Typography assessment
   - Visual hierarchy evaluation

3. CONTENT STRUCTURE:
   - Slide classification (Title, Content, Conclusion, etc.)
   - Content organization quality
   - Information density per slide

4. VISUAL ELEMENTS:
   - Image usage effectiveness
   - Color psychology insights
   - Brand consistency evaluation

5. TECHNICAL ASSESSMENT:
   - Slide dimensions and format
   - Template vs custom design
   - Completeness level (skeleton vs finished)

6. RECOMMENDATIONS:
   - Design improvements
   - Content suggestions
   - Accessibility considerations

7. OVERALL SCORE:
   - Design: X/10
   - Content: X/10
   - Professional Quality: X/10

Please format your response in clear sections with specific insights and actionable recommendations.
"""
        
        return prompt
    
    def _parse_analysis(self, analysis_text: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure the analysis response."""
        
        structured = {
            "raw_analysis": analysis_text,
            "presentation_topic": self._extract_topic(analysis_text),
            "design_score": self._extract_score(analysis_text, "Design"),
            "content_score": self._extract_score(analysis_text, "Content"),
            "professional_score": self._extract_score(analysis_text, "Professional Quality"),
            "slide_classifications": self._classify_slides(original_data),
            "key_insights": self._extract_key_insights(analysis_text),
            "recommendations": self._extract_recommendations(analysis_text),
            "color_analysis": self._analyze_colors(original_data["global_analysis"]["color_palette"]),
            "summary": {
                "total_slides": original_data["global_analysis"]["total_slides"],
                "total_images": original_data["global_analysis"]["image_count"],
                "unique_colors": len(set(original_data["global_analysis"]["color_palette"])),
                "unique_fonts": len(set(original_data["global_analysis"]["fonts_used"])),
                "presentation_type": self._determine_presentation_type(original_data)
            }
        }
        
        return structured
    
    def _extract_topic(self, text: str) -> str:
        """Extract the main topic from analysis."""
        lines = text.split('\n')
        for line in lines:
            if 'about' in line.lower() or 'topic' in line.lower():
                return line.strip()
        return "Topic not clearly identified"
    
    def _extract_score(self, text: str, score_type: str) -> int:
        """Extract numerical scores from analysis."""
        import re
        pattern = rf"{score_type}[:\s]*(\d+)/10"
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _classify_slides(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Classify each slide based on content."""
        classifications = []
        
        for slide in data["slides"]:
            slide_type = "Content"  # Default
            
            # Simple heuristics for classification
            text_count = slide["text_count"]
            image_count = slide["image_count"]
            
            if slide["slide_number"] == 1:
                slide_type = "Title"
            elif slide["slide_number"] == data["global_analysis"]["total_slides"]:
                slide_type = "Thank You / Conclusion"
            elif text_count == 0 and image_count > 0:
                slide_type = "Image-only"
            elif text_count > 5:
                slide_type = "Content-heavy"
            elif image_count > 2:
                slide_type = "Visual-heavy"
            
            classifications.append({
                "slide_number": slide["slide_number"],
                "classification": slide_type,
                "layout": slide["layout"]
            })
        
        return classifications
    
    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights from analysis."""
        insights = []
        lines = text.split('\n')
        
        current_section = ""
        for line in lines:
            line = line.strip()
            if line and (line.endswith(':') or line.isupper()):
                current_section = line
            elif line and line.startswith('-') and current_section:
                insights.append(f"{current_section}: {line[1:].strip()}")
        
        return insights[:10]  # Limit to top 10 insights
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from analysis."""
        recommendations = []
        lines = text.split('\n')
        
        in_recommendations = False
        for line in lines:
            line = line.strip()
            if 'recommendation' in line.lower():
                in_recommendations = True
            elif in_recommendations and line.startswith('-'):
                recommendations.append(line[1:].strip())
        
        return recommendations
    
    def _analyze_colors(self, color_palette: List[str]) -> Dict[str, Any]:
        """Analyze color palette."""
        if not color_palette:
            return {"analysis": "No colors detected"}
        
        unique_colors = list(set(color_palette))
        
        analysis = {
            "total_colors": len(color_palette),
            "unique_colors": len(unique_colors),
            "dominant_colors": unique_colors[:5],
            "color_diversity": "High" if len(unique_colors) > 10 else "Medium" if len(unique_colors) > 5 else "Low"
        }
        
        return analysis
    
    def _determine_presentation_type(self, data: Dict[str, Any]) -> str:
        """Determine if presentation is template, draft, or complete."""
        total_slides = data["global_analysis"]["total_slides"]
        total_images = data["global_analysis"]["image_count"]
        total_colors = len(set(data["global_analysis"]["color_palette"]))
        
        # Simple heuristics
        if total_slides < 5 and total_images == 0:
            return "Template/Skeleton"
        elif total_images > 0 and total_colors > 3:
            return "Complete Presentation"
        else:
            return "Draft/In Progress"
