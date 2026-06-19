import pikepdf
from pikepdf import PdfImage
import pdfplumber
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def extract_text_from_content_stream(pikepdf_page) -> str:
    text_parts = []
    def clean_val(val):
        if isinstance(val, pikepdf.String):
            s = str(val)
            return s.replace('\x00', '')
        elif isinstance(val, pikepdf.Array):
            return "".join(clean_val(x) for x in val)
        return ""

    try:
        for operands, operator in pikepdf.parse_content_stream(pikepdf_page):
            op = str(operator)
            if op in ['Tj', '\'', '"']:
                if operands:
                    text_parts.append(clean_val(operands[0]))
            elif op == 'TJ':
                if operands:
                    text_parts.append(clean_val(operands[0]))
    except Exception as e:
        logger.warning(f"Error parsing text content stream: {e}")
        
    return "\n".join(text_parts)

def extract_pdf(pdf_path: str) -> dict:
    """
    Extracts text and unique, filtered images from a PDF page-by-page.
    
    Returns:
    {
        "pageCount": int,
        "pages": [
            { "page": int, "text": str, "images": [PIL.Image, ...] },
            ...
        ]
    }
    """
    logger.info(f"Opening PDF for extraction: {pdf_path}")
    
    try:
        pdf = pikepdf.Pdf.open(pdf_path)
        plumber = pdfplumber.open(pdf_path)
    except Exception as e:
        logger.error(f"Failed to open PDF {pdf_path}: {e}")
        raise ValueError(f"Could not open or parse PDF file: {e}")
        
    pages_data = []
    page_count = len(pdf.pages)
    
    try:
        for idx in range(page_count):
            page_num = idx + 1
            pikepdf_page = pdf.pages[idx]
            plumber_page = plumber.pages[idx]
            
            # Extract text using pdfplumber without layout=True
            text = plumber_page.extract_text() or ""
            
            # Fallback to direct content stream parsing if extracted text is empty
            if not text.strip():
                text = extract_text_from_content_stream(pikepdf_page)
            
            # Parse content stream to find image drawing order
            image_names = []
            try:
                for operands, operator in pikepdf.parse_content_stream(pikepdf_page):
                    # Check for 'Do' operator (draws XObject)
                    if str(operator) == 'Do':
                        if operands and len(operands) > 0:
                            image_names.append(operands[0])
            except Exception as e:
                logger.warning(f"Error parsing content stream on Page {page_num}: {e}")
            
            # Extract and filter images
            images = []
            resources = pikepdf_page.get('/Resources')
            if resources and '/XObject' in resources:
                xobjects = resources['/XObject']
                for name in image_names:
                    if name in xobjects:
                        obj = xobjects[name]
                        # Check Subtype is Image
                        if obj.get('/Subtype') == '/Image':
                            try:
                                width = int(obj.get('/Width', 0))
                                height = int(obj.get('/Height', 0))
                                
                                # Filter 1: Min size 150px (width or height)
                                if width < 150 and height < 150:
                                    continue
                                    
                                # Filter 2: Aspect ratio not extreme (not > 3:1 or < 1:3)
                                if height > 0:
                                    aspect_ratio = width / height
                                    if aspect_ratio > 3.0 or aspect_ratio < 0.333:
                                        continue
                                
                                # Convert to PIL Image
                                pil_img = PdfImage(obj).as_pil_image()
                                images.append(pil_img)
                            except Exception as e:
                                logger.warning(f"Error extracting image {name} on Page {page_num}: {e}")
            
            pages_data.append({
                "page": page_num,
                "text": text,
                "images": images
            })
            
    finally:
        plumber.close()
        pdf.close()
        
    return {
        "pageCount": page_count,
        "pages": pages_data
    }
