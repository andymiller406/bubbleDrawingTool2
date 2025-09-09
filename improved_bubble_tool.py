#!/usr/bin/env python3
"""
Improved Bubble Drawing Tool for PDF Technical Drawings

This improved version uses better algorithms for detecting dimension lines
and includes manual fallback options.

Author: Manus AI
"""

import os
import sys
import argparse
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedBubbleDrawingTool:
    def __init__(self):
        self.bubble_radius = 20
        self.bubble_color = (255, 0, 0)  # Red
        self.text_color = (255, 255, 255)  # White
        self.font_size = 14
        
    def pdf_to_images(self, pdf_path, dpi=300):
        """Convert PDF to list of PIL images."""
        try:
            logger.info(f"Converting PDF to images: {pdf_path}")
            images = convert_from_path(pdf_path, dpi=dpi)
            logger.info(f"Successfully converted {len(images)} pages")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF: {e}")
            return []
    
    def preprocess_image(self, pil_image):
        """Preprocess image for better analysis."""
        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding for better line detection
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Invert if needed (make lines black on white background)
        if np.mean(thresh) < 127:
            thresh = cv2.bitwise_not(thresh)
        
        return cv_image, gray, thresh
    
    def detect_dimension_lines_improved(self, thresh_image):
        """Improved dimension line detection using morphological operations."""
        # Create kernels for detecting horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(thresh_image, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Detect vertical lines
        vertical_lines = cv2.morphologyEx(thresh_image, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combine horizontal and vertical lines
        lines_image = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
        
        # Find contours of the lines
        contours, _ = cv2.findContours(lines_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        dimension_lines = []
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter based on aspect ratio and size
            if w > 30 and h < 10:  # Horizontal line
                dimension_lines.append(('horizontal', x, y, x + w, y + h//2))
            elif h > 30 and w < 10:  # Vertical line
                dimension_lines.append(('vertical', x + w//2, y, x + w//2, y + h))
        
        logger.info(f"Detected {len(dimension_lines)} dimension lines using morphological operations")
        return dimension_lines
    
    def detect_arrowheads(self, thresh_image):
        """Detect arrowheads in the image."""
        # Create a kernel for detecting small triangular shapes
        kernel = np.array([
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0]
        ], dtype=np.uint8)
        
        # Apply morphological operations to detect arrowheads
        arrowheads = cv2.morphologyEx(thresh_image, cv2.MORPH_HITMISS, kernel)
        
        # Find contours of arrowheads
        contours, _ = cv2.findContours(arrowheads, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        arrowhead_positions = []
        for contour in contours:
            if cv2.contourArea(contour) > 5:  # Filter small noise
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    arrowhead_positions.append((cx, cy))
        
        logger.info(f"Detected {len(arrowhead_positions)} potential arrowheads")
        return arrowhead_positions
    
    def detect_text_regions_improved(self, thresh_image):
        """Improved text detection using connected components."""
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            cv2.bitwise_not(thresh_image), connectivity=8)
        
        text_regions = []
        for i in range(1, num_labels):  # Skip background (label 0)
            x, y, w, h, area = stats[i]
            
            # Filter based on size and aspect ratio for text
            if (10 < w < 200 and 8 < h < 40 and 
                area > 50 and area < 5000):
                
                # Check aspect ratio (text is usually wider than tall)
                aspect_ratio = w / h
                if 0.5 < aspect_ratio < 15:
                    text_regions.append((x, y, w, h))
        
        logger.info(f"Detected {len(text_regions)} potential text regions")
        return text_regions
    
    def create_manual_dimensions(self, image_shape):
        """Create manual dimension annotations for testing."""
        height, width = image_shape[:2]
        
        # Define some manual dimensions based on typical drawing locations
        manual_dimensions = [
            {
                'line': ('horizontal', width//4, height//3, 3*width//4, height//3),
                'text': (width//2 - 30, height//3 - 30, 60, 20),
                'dimension_id': 1
            },
            {
                'line': ('vertical', width//4, height//3, width//4, 2*height//3),
                'text': (width//4 - 60, height//2 - 10, 40, 20),
                'dimension_id': 2
            },
            {
                'line': ('horizontal', width//2, 2*height//3 + 20, 3*width//4, 2*height//3 + 20),
                'text': (5*width//8 - 20, 2*height//3 + 30, 40, 20),
                'dimension_id': 3
            },
            {
                'line': ('vertical', 3*width//4 + 20, height//2, 3*width//4 + 20, 2*height//3),
                'text': (3*width//4 + 30, height//2 + 20, 30, 20),
                'dimension_id': 4
            }
        ]
        
        logger.info(f"Created {len(manual_dimensions)} manual dimension annotations")
        return manual_dimensions
    
    def find_bubble_position_improved(self, line_info, text_region, image_shape):
        """Improved bubble positioning algorithm."""
        line_type, x1, y1, x2, y2 = line_info
        tx, ty, tw, th = text_region
        height, width = image_shape[:2]
        
        # Calculate text center
        text_center_x = tx + tw / 2
        text_center_y = ty + th / 2
        
        # Determine best position based on line orientation
        if line_type == 'horizontal':
            # For horizontal lines, place bubble to the right or left of text
            candidates = [
                (text_center_x + tw/2 + 30, text_center_y),  # Right of text
                (text_center_x - tw/2 - 30, text_center_y),  # Left of text
            ]
        else:  # vertical
            # For vertical lines, place bubble above or below text
            candidates = [
                (text_center_x, text_center_y - th/2 - 30),  # Above text
                (text_center_x, text_center_y + th/2 + 30),  # Below text
            ]
        
        # Choose the first position that's within image bounds
        for x, y in candidates:
            if (self.bubble_radius + 5 < x < width - self.bubble_radius - 5 and 
                self.bubble_radius + 5 < y < height - self.bubble_radius - 5):
                return int(x), int(y)
        
        # Fallback to text center with offset
        return int(text_center_x + 40), int(text_center_y - 20)
    
    def draw_bubble_improved(self, image, position, number):
        """Draw an improved numbered bubble on the image."""
        x, y = position
        
        # Convert OpenCV image to PIL for better text rendering
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # Draw circle with border
        draw.ellipse([x - self.bubble_radius, y - self.bubble_radius,
                     x + self.bubble_radius, y + self.bubble_radius],
                    fill=self.bubble_color, outline=(0, 0, 0), width=3)
        
        # Draw number
        try:
            # Try to use a default font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
                                    self.font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Get text size for centering
        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw text centered in bubble
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        draw.text((text_x, text_y), text, fill=self.text_color, font=font)
        
        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def process_image_improved(self, pil_image, use_manual=False):
        """Process a single image with improved algorithms."""
        logger.info("Processing image for dimension detection (improved)")
        
        # Preprocess image
        cv_image, gray, thresh = self.preprocess_image(pil_image)
        
        if use_manual:
            # Use manual dimensions for demonstration
            associations = self.create_manual_dimensions(cv_image.shape)
        else:
            # Try automatic detection
            dimension_lines = self.detect_dimension_lines_improved(thresh)
            text_regions = self.detect_text_regions_improved(thresh)
            
            # Create associations
            associations = []
            for i, line_info in enumerate(dimension_lines):
                # Find closest text region
                line_type, x1, y1, x2, y2 = line_info
                line_center_x = (x1 + x2) / 2
                line_center_y = (y1 + y2) / 2
                
                min_distance = float('inf')
                closest_text = None
                
                for text_region in text_regions:
                    tx, ty, tw, th = text_region
                    text_center_x = tx + tw / 2
                    text_center_y = ty + th / 2
                    
                    distance = np.sqrt((line_center_x - text_center_x)**2 + 
                                     (line_center_y - text_center_y)**2)
                    
                    if distance < 150 and distance < min_distance:
                        min_distance = distance
                        closest_text = text_region
                
                if closest_text:
                    associations.append({
                        'line': line_info,
                        'text': closest_text,
                        'dimension_id': i + 1
                    })
        
        # Draw bubbles
        result_image = cv_image.copy()
        for assoc in associations:
            if use_manual:
                position = self.find_bubble_position_improved(
                    assoc['line'], assoc['text'], cv_image.shape)
            else:
                position = self.find_bubble_position_improved(
                    assoc['line'], assoc['text'], cv_image.shape)
            
            result_image = self.draw_bubble_improved(result_image, position, 
                                                   assoc['dimension_id'])
        
        # Convert back to PIL
        result_pil = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
        
        logger.info(f"Added {len(associations)} dimension bubbles")
        return result_pil
    
    def process_pdf_improved(self, input_pdf_path, output_dir, use_manual=False):
        """Process entire PDF with improved algorithms."""
        # Convert PDF to images
        images = self.pdf_to_images(input_pdf_path)
        if not images:
            logger.error("Failed to convert PDF to images")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each page
        for i, image in enumerate(images):
            logger.info(f"Processing page {i+1}/{len(images)}")
            
            # Process image
            annotated_image = self.process_image_improved(image, use_manual)
            
            # Save annotated image
            output_path = os.path.join(output_dir, f"page_{i+1:03d}_bubbled.png")
            annotated_image.save(output_path, "PNG")
            logger.info(f"Saved annotated page: {output_path}")
        
        logger.info(f"Processing complete. Annotated images saved to: {output_dir}")
        return True

def main():
    parser = argparse.ArgumentParser(description="Improved bubble drawing tool for PDF technical drawings")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("-o", "--output", default="output_improved", 
                       help="Output directory for annotated images")
    parser.add_argument("-m", "--manual", action="store_true",
                       help="Use manual dimension placement for demonstration")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if input file exists
    if not os.path.exists(args.input_pdf):
        logger.error(f"Input file not found: {args.input_pdf}")
        sys.exit(1)
    
    # Create tool instance and process PDF
    tool = ImprovedBubbleDrawingTool()
    success = tool.process_pdf_improved(args.input_pdf, args.output, args.manual)
    
    if success:
        logger.info("Improved bubble drawing tool completed successfully!")
        sys.exit(0)
    else:
        logger.error("Improved bubble drawing tool failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

