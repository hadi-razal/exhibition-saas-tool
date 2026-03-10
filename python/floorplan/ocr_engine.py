"""
OCR Engine — Image preprocessing and text extraction using pytesseract.
"""
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger("exhibitiq.floorplan.ocr_engine")


class OCREngine:
    """Handles image preprocessing and OCR text extraction."""

    def process_image_file(self, file_path: str) -> dict:
        """Process an image file through OCR."""
        from PIL import Image
        img = Image.open(file_path)
        return self.process_image(img)

    def process_image(self, image) -> dict:
        """
        Preprocess image and run OCR extraction.
        Returns dict with 'text' and optionally 'boxes' (bounding box data).
        """
        import cv2
        from PIL import Image

        # Convert PIL Image to numpy array for OpenCV processing
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image

        # Preprocess the image
        processed = self._preprocess(img_array)

        # Run pytesseract
        text, boxes = self._run_tesseract(processed)

        return {
            "text": text,
            "boxes": boxes,
        }

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        Apply image preprocessing to improve OCR accuracy.
        Steps: grayscale → enlarge → denoise → threshold → sharpen
        """
        import cv2

        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()

        # Enlarge small images (helps OCR with small text)
        h, w = gray.shape[:2]
        if max(h, w) < 2000:
            scale = 2000 / max(h, w)
            gray = cv2.resize(
                gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
            )

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)

        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)

        # Adaptive threshold for better text detection
        thresh = cv2.adaptiveThreshold(
            contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Sharpen
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(thresh, -1, kernel)

        return sharpened

    def _run_tesseract(self, image: np.ndarray) -> tuple[str, list]:
        """
        Run pytesseract OCR on preprocessed image.
        Returns (full_text, bounding_box_list).
        """
        try:
            import pytesseract
            from PIL import Image

            pil_image = Image.fromarray(image)

            # Get full text
            text = pytesseract.image_to_string(
                pil_image,
                config="--oem 3 --psm 6",
            )

            # Get bounding box data
            boxes = []
            try:
                box_data = pytesseract.image_to_data(
                    pil_image,
                    output_type=pytesseract.Output.DICT,
                    config="--oem 3 --psm 6",
                )

                for i in range(len(box_data["text"])):
                    word = box_data["text"][i].strip()
                    conf = int(box_data["conf"][i])
                    if word and conf > 30:  # Filter low confidence
                        boxes.append({
                            "text": word,
                            "x": box_data["left"][i],
                            "y": box_data["top"][i],
                            "w": box_data["width"][i],
                            "h": box_data["height"][i],
                            "confidence": conf,
                        })
            except Exception as e:
                logger.warning(f"Could not extract bounding boxes: {e}")

            logger.info(
                f"OCR extracted {len(text.split())} words, {len(boxes)} boxes"
            )
            return text, boxes

        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            raise RuntimeError(
                f"OCR failed. Make sure Tesseract is installed. Error: {e}"
            )
