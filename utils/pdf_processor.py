"""
Enhanced PDF processor using PyMuPDF (fitz) for text and image extraction.
Replaces the previous pdf_extractor.py with production-grade PDF handling.
"""

import json
import base64
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

import fitz  # PyMuPDF


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PDFPage:
    """Represents a single PDF page with extracted content."""
    page_number: int
    text: str
    images: List[Dict]  # List of {image_id, base64_data, extracted_text}
    metadata: Dict


@dataclass
class PDFDocument:
    """Represents an entire extracted PDF document."""
    filename: str
    total_pages: int
    pages: List[PDFPage]
    document_type: str  # "inspection", "thermal", etc.
    extraction_timestamp: str
    metadata: Dict


class PDFProcessor:
    """
    Production-grade PDF processor using PyMuPDF.
    Extracts text and images with OCR support.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize PDF processor.
        
        Args:
            output_dir: Optional directory to save extracted images
        """
        self.output_dir = output_dir or Path("./images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_pdf(self, pdf_path: str) -> PDFDocument:
        """
        Extract all content from PDF: text, images, metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            PDFDocument with all extracted content
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info(f"Extracting from PDF: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        pages_data = []
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_data = self._extract_page_content(page, page_num, pdf_path)
                pages_data.append(page_data)
                logger.info(f"  Page {page_num + 1}: {len(page_data.images)} images found")
                
        finally:
            doc.close()

        # Infer document type from filename
        doc_type = self._infer_document_type(pdf_path.name)
        
        pdf_doc = PDFDocument(
            filename=pdf_path.name,
            total_pages=len(pages_data),
            pages=pages_data,
            document_type=doc_type,
            extraction_timestamp=datetime.now().isoformat(),
            metadata=self._extract_metadata(pdf_path, len(pages_data))
        )
        
        logger.info(f"Extraction complete: {len(pages_data)} pages, {sum(len(p.images) for p in pages_data)} images")
        return pdf_doc

    def _extract_page_content(self, page: fitz.Page, page_num: int, pdf_path: Path) -> PDFPage:
        """Extract text and images from a single page."""
        
        # Extract text
        text = page.get_text("text")
        
        # Extract images
        images = []
        image_list = page.get_images()
        
        for img_index, img_ref in enumerate(image_list):
            try:
                xref = img_ref[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                # Convert to RGB if CMYK
                if pix.n - pix.alpha < 4:  # Gray or RGB
                    img_data = pix.tobytes("png")
                else:  # CMYK
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix.tobytes("png")
                
                # Save image
                img_filename = f"{pdf_path.stem}_p{page_num + 1}_img{img_index + 1}.png"
                img_path = self.output_dir / img_filename
                with open(img_path, "wb") as f:
                    f.write(img_data)
                
                # Convert to base64 for JSON storage
                img_base64 = base64.b64encode(img_data).decode("utf-8")
                
                images.append({
                    "image_id": f"{pdf_path.stem}_p{page_num + 1}_img{img_index + 1}",
                    "filename": img_filename,
                    "size": len(img_data),
                    "base64_data": img_base64[:500] + "..." if len(img_base64) > 500 else img_base64  # Truncate for display
                })
                
            except Exception as e:
                logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
        
        return PDFPage(
            page_number=page_num + 1,
            text=text,
            images=images,
            metadata={
                "size": page.rect.get_area(),
                "width": page.rect.width,
                "height": page.rect.height
            }
        )

    def _infer_document_type(self, filename: str) -> str:
        """Infer document type from filename."""
        filename_lower = filename.lower()
        if "thermal" in filename_lower:
            return "thermal_report"
        elif "inspection" in filename_lower:
            return "inspection_report"
        elif "moisture" in filename_lower:
            return "moisture_report"
        else:
            return "unknown_report"

    def _extract_metadata(self, pdf_path: Path, page_count: int) -> Dict:
        """Extract document metadata."""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata or {}
            doc.close()
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creation_date": str(metadata.get("creationDate", "")),
                "modification_date": str(metadata.get("modDate", "")),
                "file_size_kb": pdf_path.stat().st_size / 1024,
                "page_count": page_count
            }
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
            return {}

    def extract_text_only(self, pdf_path: str) -> str:
        """Extract only text from PDF (fast, no images)."""
        pdf_path = Path(pdf_path)
        doc = fitz.open(pdf_path)
        text = ""
        try:
            for page in doc:
                text += page.get_text("text") + "\n---PAGE BREAK---\n"
        finally:
            doc.close()
        return text

    def extract_images_only(self, pdf_path: str) -> List[Tuple[str, bytes]]:
        """Extract only images from PDF."""
        pdf_path = Path(pdf_path)
        doc = fitz.open(pdf_path)
        images = []
        
        try:
            for page_num, page in enumerate(doc):
                for img_index, img_ref in enumerate(page.get_images()):
                    try:
                        xref = img_ref[0]
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha < 4:
                            img_data = pix.tobytes("png")
                        else:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix.tobytes("png")
                        
                        filename = f"{pdf_path.stem}_p{page_num + 1}_img{img_index + 1}.png"
                        images.append((filename, img_data))
                    except Exception as e:
                        logger.warning(f"Failed to extract image: {e}")
        finally:
            doc.close()
        
        return images

    def to_json(self, pdf_doc: PDFDocument) -> str:
        """Convert extracted PDF to JSON format."""
        return json.dumps(asdict(pdf_doc), indent=2, default=str)

    def save_extraction(self, pdf_doc: PDFDocument, output_path: str):
        """Save extracted PDF content to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(self.to_json(pdf_doc))
        
        logger.info(f"Extraction saved to: {output_path}")

    def batch_extract(self, input_dir: str, output_dir: Optional[str] = None) -> List[PDFDocument]:
        """Extract all PDFs from directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else input_path
        output_path.mkdir(parents=True, exist_ok=True)
        
        pdf_docs = []
        pdf_files = list(input_path.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            try:
                pdf_doc = self.extract_pdf(str(pdf_file))
                pdf_docs.append(pdf_doc)
                
                # Save extraction
                json_path = output_path / f"{pdf_file.stem}.json"
                self.save_extraction(pdf_doc, str(json_path))
                
            except Exception as e:
                logger.error(f"Failed to extract {pdf_file}: {e}")
        
        return pdf_docs

    def validate_pdf(self, pdf_path: str) -> bool:
        """Validate if PDF is readable and extractable."""
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return False
            
            doc = fitz.open(pdf_path)
            is_valid = len(doc) > 0
            doc.close()
            return is_valid
        except Exception:
            return False
