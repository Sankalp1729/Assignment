"""Image Extraction Module - Extract and process images from documents"""

import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json


class ImageExtractor:
    """
    Extract, process, and manage images from documents.
    
    Features:
    - Extract images from PDFs
    - Process and resize images
    - Generate thumbnails
    - Create image metadata
    - Link images to observations
    """

    def __init__(self, output_dir: str = "./images", thumbnail_size: Tuple[int, int] = (150, 150)):
        """
        Initialize image extractor.
        
        Args:
            output_dir: Directory to save extracted images
            thumbnail_size: Size for thumbnail generation (width, height)
        """
        self.output_dir = Path(output_dir)
        self.thumbnail_size = thumbnail_size
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_images_from_pdf(
        self, pdf_path: str
    ) -> List[Dict[str, Any]]:
        """
        Extract images from PDF file.
        
        Returns:
            List of image metadata dictionaries
        """
        images = []

        # In production:
        # from pdf2image import convert_from_path
        # pdf_images = convert_from_path(pdf_path)
        # for idx, image in enumerate(pdf_images):
        #     image_path = self.save_image(image, f"{Path(pdf_path).stem}_page_{idx}")
        #     images.append(self.create_image_metadata(image_path, idx, pdf_path))

        # For now, check for associated JSON
        json_path = str(pdf_path).replace(".pdf", ".json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                data = json.load(f)
                for img_data in data.get("images", []):
                    images.append({
                        "id": img_data.get("id"),
                        "filename": img_data.get("filename"),
                        "source_document": Path(pdf_path).name,
                        "page_number": img_data.get("page", 0),
                        "description": img_data.get("description", ""),
                        "extracted_at": datetime.now().isoformat(),
                    })

        return images

    def save_image(self, image_obj, filename: str) -> str:
        """
        Save image to disk.
        
        Args:
            image_obj: PIL Image object
            filename: Output filename (without extension)
            
        Returns:
            Path to saved image
        """
        # In production:
        # output_path = self.output_dir / f"{filename}.png"
        # image_obj.save(output_path, quality=95)
        # return str(output_path)

        # For now, just return expected path
        return str(self.output_dir / f"{filename}.png")

    def create_thumbnail(self, image_path: str) -> str:
        """
        Create thumbnail for image.
        
        Args:
            image_path: Path to image
            
        Returns:
            Path to thumbnail
        """
        # In production:
        # image = Image.open(image_path)
        # image.thumbnail(self.thumbnail_size)
        # thumb_path = self.output_dir / f"{Path(image_path).stem}_thumb.png"
        # image.save(thumb_path)
        # return str(thumb_path)

        return str(self.output_dir / f"{Path(image_path).stem}_thumb.png")

    def create_image_metadata(
        self, image_path: str, page_num: int, source_pdf: str
    ) -> Dict[str, Any]:
        """
        Create metadata for an image.
        
        Returns:
            Dictionary with image metadata
        """
        path = Path(image_path)

        metadata = {
            "id": f"img_{path.stem}",
            "filename": path.name,
            "path": image_path,
            "page_number": page_num,
            "source_document": Path(source_pdf).name,
            "extracted_at": datetime.now().isoformat(),
            "description": "",  # Will be populated later
            "related_observations": [],
        }

        return metadata

    def link_image_to_observation(
        self, image_id: str, observation_id: str
    ) -> None:
        """Link an image to an observation"""
        # Store in a mapping
        pass

    def get_images_for_observation(self, observation_id: str) -> List[Dict[str, Any]]:
        """Get all images linked to an observation"""
        # Retrieve from mapping
        return []

    def batch_extract_images(
        self, pdf_directory: str
    ) -> List[Dict[str, Any]]:
        """
        Extract images from all PDFs in directory.
        
        Args:
            pdf_directory: Directory containing PDFs
            
        Returns:
            List of image metadata
        """
        all_images = []

        pdf_dir = Path(pdf_directory)
        for pdf_file in pdf_dir.glob("*.pdf"):
            try:
                images = self.extract_images_from_pdf(str(pdf_file))
                all_images.extend(images)
            except Exception as e:
                print(f"Error extracting images from {pdf_file}: {e}")

        return all_images

    def organize_images_by_type(
        self, images: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize images by type/category.
        
        Returns:
            Dictionary with images grouped by category
        """
        organized = {
            "thermal": [],
            "structural": [],
            "moisture": [],
            "other": [],
        }

        for image in images:
            description = image.get("description", "").lower()

            if "thermal" in description:
                organized["thermal"].append(image)
            elif "crack" in description or "structural" in description:
                organized["structural"].append(image)
            elif "water" in description or "moisture" in description or "damp" in description:
                organized["moisture"].append(image)
            else:
                organized["other"].append(image)

        return organized

    def generate_image_report(
        self, images: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate report on extracted images.
        
        Returns:
            Summary statistics
        """
        organized = self.organize_images_by_type(images)

        report = {
            "total_images": len(images),
            "by_type": {k: len(v) for k, v in organized.items()},
            "by_document": {},
            "extraction_timestamp": datetime.now().isoformat(),
        }

        # Group by source document
        for image in images:
            doc = image.get("source_document", "unknown")
            if doc not in report["by_document"]:
                report["by_document"][doc] = 0
            report["by_document"][doc] += 1

        return report
