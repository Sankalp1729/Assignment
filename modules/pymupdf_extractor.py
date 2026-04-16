"""
PDF text and image extraction using PyMuPDF (fitz).
"""

import fitz  # PyMuPDF
import json
from pathlib import Path
from typing import Tuple, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PDFExtractionResult:
    """Result of PDF extraction."""
    text: str
    images: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    page_count: int


class PyMuPDFExtractor:
    """Extract text and images from PDFs using PyMuPDF."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize extractor.
        
        Args:
            pdf_path: Path to PDF file
            
        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If file is not a valid PDF
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        try:
            self.doc = fitz.open(pdf_path)
        except Exception as e:
            raise ValueError(f"Invalid PDF file: {e}")
    
    def extract_text(self) -> str:
        """
        Extract all text from PDF.
        
        Returns:
            Combined text from all pages
        """
        text_blocks = []
        for page_num, page in enumerate(self.doc):
            text = page.get_text()
            text_blocks.append(f"--- Page {page_num + 1} ---\n{text}")
        
        return "\n".join(text_blocks)
    
    def extract_images(self, output_dir: str = None) -> List[Dict[str, Any]]:
        """
        Extract images from PDF.
        
        Args:
            output_dir: Directory to save extracted images (optional)
            
        Returns:
            List of image metadata
        """
        images = []
        image_count = 0
        
        for page_num, page in enumerate(self.doc):
            image_list = page.get_images()
            
            for img_index, img_ref in enumerate(image_list):
                try:
                    xref = img_ref[0]
                    pix = fitz.Pixmap(self.doc, xref)
                    image_name = f"page_{page_num + 1}_img_{img_index + 1}"
                    
                    img_info = {
                        "name": image_name,
                        "page": page_num + 1,
                        "position": f"image_{img_index + 1}",
                        "format": pix.n == 4 and "RGBA" or "RGB",
                        "width": pix.width,
                        "height": pix.height
                    }
                    
                    # Save image if output directory specified
                    if output_dir:
                        output_path = Path(output_dir) / f"{image_name}.png"
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        pix.save(str(output_path))
                        img_info["saved_path"] = str(output_path)
                    
                    images.append(img_info)
                    image_count += 1
                except Exception as e:
                    print(f"Error extracting image: {e}")
        
        return images
    
    def extract_all(self, output_dir: str = None) -> PDFExtractionResult:
        """
        Extract text, images, and metadata.
        
        Args:
            output_dir: Directory to save extracted images
            
        Returns:
            PDFExtractionResult with all extracted data
        """
        text = self.extract_text()
        images = self.extract_images(output_dir)
        
        metadata = {
            "source_file": str(self.pdf_path),
            "extraction_date": datetime.now().isoformat(),
            "page_count": len(self.doc),
            "image_count": len(images),
            "text_length": len(text),
            "pdf_title": self.doc.metadata().get("title", "Unknown"),
            "pdf_author": self.doc.metadata().get("author", "Unknown")
        }
        
        return PDFExtractionResult(
            text=text,
            images=images,
            metadata=metadata,
            page_count=len(self.doc)
        )
    
    def extract_to_json(self, output_path: str = None) -> Dict[str, Any]:
        """
        Extract as JSON representation.
        
        Args:
            output_path: Path to save JSON (optional)
            
        Returns:
            JSON-serializable extraction result
        """
        result = self.extract_all()
        json_data = {
            "text": result.text,
            "images": result.images,
            "metadata": result.metadata,
            "page_count": result.page_count
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return json_data
    
    def close(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def batch_extract_pdfs(pdf_dir: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Extract text from all PDFs in a directory.
    
    Args:
        pdf_dir: Directory containing PDFs
        output_dir: Directory to save extracted images
        
    Returns:
        Dictionary with extraction results for all PDFs
    """
    pdf_dir = Path(pdf_dir)
    results = {}
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        try:
            with PyMuPDFExtractor(str(pdf_file)) as extractor:
                result = extractor.extract_all(output_dir)
                results[pdf_file.stem] = {
                    "success": True,
                    "text": result.text,
                    "image_count": len(result.images),
                    "page_count": result.page_count,
                    "metadata": result.metadata
                }
        except Exception as e:
            results[pdf_file.stem] = {
                "success": False,
                "error": str(e)
            }
    
    return results
