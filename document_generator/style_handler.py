from typing import List, Dict, Any, Optional
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.shared import Pt, RGBColor

def hex_to_rgb(hex_color: str) -> RGBColor:
    """Convert hex color to RGBColor object"""
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB values
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return RGBColor(r, g, b)

def apply_hardcoded_style(run: Run, font_name: str = "Times New Roman", font_size: int = 11, 
                         bold: bool = False, italic: bool = False, underline: bool = False, 
                         color: Optional[str] = None, superscript: bool = False, 
                         spacing: Optional[float] = None, scale: Optional[int] = None) -> None:
    """Apply hardcoded style to a run with optional hex color
    
    Args:
        run: The run to style
        font_name: Font family name
        font_size: Font size in points
        bold: Bold formatting
        italic: Italic formatting  
        underline: Underline formatting
        color: Hex color (e.g., "#FF0000" for red, "#000000" for black)
        superscript: Superscript formatting
        spacing: Character spacing in points (None for normal)
        scale: Font scale as percentage (None for 100%)
    """
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.underline = underline
    run.font.superscript = superscript
    
    if color:
        run.font.color.rgb = hex_to_rgb(color)
    
    # Aggressively clear and set character spacing and scale using XML properties
    try:
        from docx.oxml.shared import qn
        from docx.oxml import OxmlElement
        
        # Get the run properties element
        rPr = run._r.get_or_add_rPr()
        
        # ALWAYS remove existing spacing element (clear any inherited condensed spacing)
        spacing_elem = rPr.find(qn('w:spacing'))
        if spacing_elem is not None:
            rPr.remove(spacing_elem)
        
        # ALWAYS remove existing scale element (clear any inherited scaling)    
        scale_elem = rPr.find(qn('w:w'))
        if scale_elem is not None:
            rPr.remove(scale_elem)
            
        # Force normal spacing (0) - explicitly add element with 0 value to override inheritance
        spacing_val = spacing if spacing is not None else 0
        spacing_elem = OxmlElement('w:spacing')
        spacing_elem.set(qn('w:val'), str(int(spacing_val * 20)))  # Convert to twips
        rPr.append(spacing_elem)
        
        # Force 100% scale - explicitly add element with 100 value to override inheritance
        scale_val = scale if scale is not None else 100
        scale_elem = OxmlElement('w:w')
        scale_elem.set(qn('w:val'), str(scale_val))
        rPr.append(scale_elem)
            
    except Exception as e:
        # Fallback to the basic properties (might not work)
        try:
            run.font.spacing = Pt(spacing if spacing is not None else 0)
            run.font.scale = scale if scale is not None else 100
        except:
            pass  # Ignore if not supported