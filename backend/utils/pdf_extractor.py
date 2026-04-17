"""PDF Extraction Module - Extract text, images, and metadata from PDFs"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


class PDFExtractor:
    """
    Extracts text, images, and metadata from PDF documents.
    
    Supports:
    - Text extraction with OCR (for scanned PDFs)
    - Image extraction
    - Metadata preservation
    - Multi-page documents
    
    In production, this uses:
    - pdfplumber: PDF text extraction
    - pdf2image: Convert PDF pages to images
    - pytesseract: OCR for scanned documents
    """

    def __init__(self, extract_images: bool = True, dpi: int = 300):
        """
        Initialize PDF extractor.
        
        Args:
            extract_images: Whether to extract images from PDFs
            dpi: Resolution for image extraction
        """
        self.extract_images = extract_images
        self.dpi = dpi
        self.extracted_images = []

    def extract_pdf(
        self, pdf_path: str, output_image_dir: str = None
    ) -> Dict[str, Any]:
        """
        Extract all content from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            output_image_dir: Directory to save extracted images
            
        Returns:
            Dictionary containing:
            - text: Full extracted text
            - metadata: PDF metadata
            - images: List of extracted images
            - pages: Number of pages
            - observations: Extracted observations (if parseable)
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # In production, would use actual PDF libraries
        # For now, using fallback JSON method
        filename = Path(pdf_path).stem

        # Try to find corresponding JSON for demo
        json_path = str(pdf_path).replace(".pdf", ".json")

        if os.path.exists(json_path):
            with open(json_path) as f:
                return json.load(f)

        # Fallback: create empty structure
        return {
            "filename": filename,
            "source": pdf_path,
            "extraction_timestamp": datetime.now().isoformat(),
            "text": f"[PDF Content from {filename}]",
            "metadata": {"filename": filename, "pages": 0},
            "images": [],
            "observations": [],
        }

    def extract_text_only(self, pdf_path: str) -> str:
        """Extract only text from PDF"""
        content = self.extract_pdf(pdf_path)
        return content.get("text", "")
    
    def extract_text_by_page(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from each page separately.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with:
            - page_num: Page number (1-indexed)
            - text: Text content from that page
        """
        content = self.extract_pdf(pdf_path)
        
        # If JSON has page-level data, use it
        if "pages" in content and isinstance(content["pages"], list):
            pages = []
            for idx, page_data in enumerate(content["pages"], 1):
                if isinstance(page_data, dict):
                    pages.append({
                        "page_num": idx,
                        "text": page_data.get("text", str(page_data))
                    })
                else:
                    pages.append({
                        "page_num": idx,
                        "text": str(page_data)
                    })
            return pages
        
        # Otherwise, return single "page" for full text
        # (In production, would use PyMuPDF to split actual pages)
        full_text = content.get("text", "")
        if full_text:
            return [
                {
                    "page_num": 1,
                    "text": full_text
                }
            ]
        
        return []

    def extract_images_from_pdf(
        self, pdf_path: str, output_dir: str = None
    ) -> List[str]:
        """
        Extract images from PDF.
        
        Returns:
            List of file paths to extracted images
        """
        if not output_dir:
            output_dir = Path(pdf_path).parent / "images"
        
        os.makedirs(output_dir, exist_ok=True)

        content = self.extract_pdf(pdf_path)
        return content.get("images", [])

    def extract_with_ocr(self, pdf_path: str) -> str:
        """
        Extract text from scanned PDF using OCR.
        
        Requires: pytesseract, pdf2image
        """
        try:
            # In production:
            # from pdf2image import convert_from_path
            # import pytesseract
            # images = convert_from_path(pdf_path, dpi=self.dpi)
            # text = "\n".join([pytesseract.image_to_string(img) for img in images])
            
            # For now, return placeholder
            return f"[OCR extracted text from {pdf_path}]"
        except ImportError:
            return self.extract_text_only(pdf_path)

    def validate_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Validate PDF structure and extract-ability.
        
        Returns:
            Validation report
        """
        report = {
            "file": pdf_path,
            "valid": False,
            "errors": [],
            "warnings": [],
            "can_extract_text": False,
            "can_extract_images": False,
        }

        if not os.path.exists(pdf_path):
            report["errors"].append("File not found")
            return report

        if not pdf_path.lower().endswith(".pdf"):
            report["errors"].append("Not a PDF file")
            return report

        # Try extraction
        try:
            content = self.extract_pdf(pdf_path)
            report["valid"] = True
            report["can_extract_text"] = bool(content.get("text"))
            report["can_extract_images"] = bool(content.get("images"))

            if not content.get("text"):
                report["warnings"].append("No text content found (might be scanned PDF)")

            if not content.get("images"):
                report["warnings"].append("No images found in PDF")

        except Exception as e:
            report["errors"].append(str(e))

        return report

    @staticmethod
    def batch_extract(
        pdf_directory: str, output_dir: str = None
    ) -> List[Dict[str, Any]]:
        """
        Extract content from all PDFs in a directory.
        
        Args:
            pdf_directory: Directory containing PDF files
            output_dir: Output directory for extracted content
            
        Returns:
            List of extraction results
        """
        extractor = PDFExtractor()
        results = []

        pdf_dir = Path(pdf_directory)
        for pdf_file in pdf_dir.glob("*.pdf"):
            try:
                result = extractor.extract_pdf(str(pdf_file), output_dir)
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "filename": pdf_file.name,
                        "error": str(e),
                    }
                )

        return results


# Convenience functions for module-level access

def extract_text_by_page(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Quick function to extract text from each page of a PDF using PyMuPDF.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of dicts with page_num and text
    """
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    pages = []
    
    for page_num, page in enumerate(doc, 1):
        text = page.get_text("text")
        print(f"PAGE {page_num} TEXT:", text[:200])  # DEBUG
        pages.append({
            "page_num": page_num,
            "text": text
        })
        
    return pages


def extract_text_all(pdf_path: str) -> str:
    """
    Quick function to extract all text from a PDF.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Combined text from all pages
    """
    pages = extract_text_by_page(pdf_path)
    return " ".join([p.get("text", "") for p in pages])


def extract_images_base64(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract images from PDF and return as base64 strings.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of dicts with page_num, image_index, and base64 string
    """
    import fitz  # PyMuPDF
    import base64
    
    doc = fitz.open(pdf_path)
    extracted_images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Convert to base64
                b64_str = base64.b64encode(image_bytes).decode('utf-8')
                data_uri = f"data:image/{image_ext};base64,{b64_str}"
                
                extracted_images.append({
                    "page_num": page_num + 1,
                    "img_index": img_index + 1,
                    "data_uri": data_uri
                })
            except Exception as e:
                print(f"Warning: Failed to extract image {img_index} on page {page_num + 1}: {e}")
                
    return extracted_images

