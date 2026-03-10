"""
OCR Engine — Image preprocessing and Tesseract extraction for floor plan images.

Key improvements over basic OCR:
- PSM 11 (sparse text) — designed for scattered text like floor plans
- Multi-pass: tries PSM 11, PSM 6, PSM 12 and merges unique words
- Returns per-block grouped text using Tesseract's block_num field
- Better preprocessing for colored/complex floor plan backgrounds
"""
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger("exhibitiq.floorplan.ocr_engine")


class OCREngine:
    """Handles image preprocessing and OCR text extraction for floor plans."""

    def process_image_file(self, file_path: str) -> dict:
        """Process an image file through the OCR pipeline."""
        from PIL import Image
        img = Image.open(file_path)
        return self.process_image(img)

    def process_image(self, image) -> dict:
        """
        Preprocess image and run multi-pass OCR.
        Returns dict with:
          - 'text': full concatenated text
          - 'blocks': list of text strings, each representing one spatial block
          - 'word_boxes': list of dicts with per-word position + text
        """
        import cv2
        from PIL import Image

        if isinstance(image, Image.Image):
            img_array = np.array(image.convert("RGB"))
        else:
            img_array = image

        processed = self._preprocess(img_array)

        text, blocks, word_boxes = self._run_tesseract_multipass(processed)

        return {
            "text": text,
            "blocks": blocks,
            "word_boxes": word_boxes,
        }

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        Adaptive preprocessing that handles both light and dark floor plan backgrounds.
        Steps:
          1. Upscale to ensure minimum resolution for OCR
          2. Convert to grayscale with background detection
          3. Denoise (gentle — floor plans have fine lines we want to keep)
          4. Normalize contrast
          5. Binarize with Otsu or adaptive threshold
        """
        import cv2

        # --- 1. Upscale ---
        h, w = img.shape[:2]
        target = 3000
        if max(h, w) < target:
            scale = target / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # --- 2. Grayscale ---
        if len(img.shape) == 3:
            # Check if image has a dark background (like the blue GSMA floor plan)
            rgb_mean = img.mean(axis=(0, 1))
            brightness = float(np.mean(rgb_mean))
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
            brightness = float(gray.mean())

        # --- 3. Gentle denoise (preserve thin lines) ---
        denoised = cv2.fastNlMeansDenoising(gray, h=6, templateWindowSize=7, searchWindowSize=21)

        # --- 4. Contrast normalization ---
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # --- 5. Binarize ---
        # Dark background: invert first so text is dark on white
        if brightness < 100:
            enhanced = cv2.bitwise_not(enhanced)

        # Try Otsu first (better for high-contrast images)
        _, otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Also adaptive for complex backgrounds
        adaptive = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 8
        )

        # Blend: if Otsu gives good separation, use it; otherwise use adaptive
        otsu_ratio = np.mean(otsu == 255)
        if 0.15 < otsu_ratio < 0.85:
            binarized = otsu
        else:
            binarized = adaptive

        # Slight sharpening to help OCR on thin text
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        sharpened = cv2.filter2D(binarized, -1, kernel)
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

        return sharpened

    @staticmethod
    def _configure_tesseract():
        """
        Auto-detect Tesseract installation path.
        On Windows, pytesseract cannot find the executable unless the path is set explicitly.
        Checks common install locations and raises a clear error if not found.
        """
        import os
        import shutil

        try:
            import pytesseract
        except ImportError:
            raise RuntimeError(
                "pytesseract not installed. Run: pip install pytesseract"
            )

        # If already findable via PATH, nothing to do
        if shutil.which("tesseract"):
            return

        if os.name == "nt":  # Windows
            username = os.environ.get("USERNAME", "user")
            candidates = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                rf"C:\Users\{username}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
                r"C:\tools\Tesseract-OCR\tesseract.exe",
                r"C:\ProgramData\chocolatey\bin\tesseract.exe",
            ]
            for path in candidates:
                if os.path.isfile(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract configured at: {path}")
                    return

            raise RuntimeError(
                "Tesseract OCR not found. Please install it:\n"
                "  Download: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "  Default path: C:\\Program Files\\Tesseract-OCR\\tesseract.exe\n"
                "  Or add Tesseract to your system PATH and restart."
            )

    def _run_tesseract_multipass(self, image: np.ndarray) -> tuple[str, list[str], list[dict]]:
        """
        Run Tesseract with multiple PSM modes and merge results.
        PSM 11: Sparse text — best for floor plans (text scattered everywhere)
        PSM 6: Uniform text block — fallback
        PSM 12: Sparse text with OSD — additional coverage
        Returns (full_text, blocks, word_boxes)
        """
        self._configure_tesseract()

        try:
            import pytesseract
            from PIL import Image

            pil_img = Image.fromarray(image)
            all_word_boxes = {}  # key: (x,y) → word data, to deduplicate

            # Run each PSM mode and collect word-level data
            for psm in [11, 6, 12]:
                config = f"--oem 3 --psm {psm}"
                try:
                    data = pytesseract.image_to_data(
                        pil_img,
                        output_type=pytesseract.Output.DICT,
                        config=config,
                    )
                    n = len(data["text"])
                    for i in range(n):
                        word = str(data["text"][i]).strip()
                        conf = int(data["conf"][i])
                        if word and conf > 25:
                            key = (data["left"][i], data["top"][i])
                            if key not in all_word_boxes:
                                all_word_boxes[key] = {
                                    "text": word,
                                    "x": data["left"][i],
                                    "y": data["top"][i],
                                    "w": data["width"][i],
                                    "h": data["height"][i],
                                    "conf": conf,
                                    "block_num": data["block_num"][i],
                                    "par_num": data["par_num"][i],
                                    "line_num": data["line_num"][i],
                                    "psm": psm,
                                }
                except Exception as e:
                    logger.debug(f"PSM {psm} failed: {e}")
                    continue

            word_boxes = list(all_word_boxes.values())

            if not word_boxes:
                # Last-ditch: just get plain text with PSM 11
                plain = pytesseract.image_to_string(pil_img, config="--oem 3 --psm 11")
                return plain, [plain], []

            # Group words into spatial blocks using OpenCV geometric shapes
            blocks = self._group_geometrically(word_boxes, image)

            full_text = "\n".join(
                " ".join(w["text"] for w in sorted(b, key=lambda x: (x["y"], x["x"])))
                for b in blocks
            )

            logger.info(f"OCR: {len(word_boxes)} words → {len(blocks)} spatial blocks")
            return full_text, [
                "\n".join(w["text"] for w in sorted(b, key=lambda x: (x["y"], x["x"])))
                for b in blocks
            ], word_boxes

        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            raise RuntimeError(
                f"OCR failed. Ensure Tesseract is installed. Error: {e}"
            )

    def _group_geometrically(self, word_boxes: list[dict], img: np.ndarray) -> list[list[dict]]:
        """
        Group word boxes using mathematical bounding shapes extracted via OpenCV contour detection.
        Ensures that text within the same drawn cell/rectangle is kept together, even if spaced far apart.
        Falls back to proximity clustering for text not inside any clear box.
        """
        import cv2

        if not word_boxes:
            return []

        # 1. Find contours on the binarized image using Canny edges
        edges = cv2.Canny(img, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)

        # RETR_LIST gets all contours including inner grid cells
        contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        h_img, w_img = img.shape[:2]
        boxes = []
        # Min area to avoid noise (e.g. 70x70 pixels in a 3000px image)
        min_area = 4500
        max_area = (h_img * w_img) * 0.8  # Ignore huge outer map frames

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            if min_area < area < max_area:
                boxes.append((x, y, w, h))

        # Sort by area ascending so smaller/inner boxes (individual booths) catch the text first
        boxes.sort(key=lambda b: b[2] * b[3])

        clusters: list[list[dict]] = []
        used_indices = set()

        for (bx, by, bw, bh) in boxes:
            current_cluster = []
            for i, word in enumerate(word_boxes):
                if i in used_indices:
                    continue
                # Center of the word
                cx = word["x"] + word["w"] / 2
                cy = word["y"] + word["h"] / 2
                
                # If word center is inside this bounding box
                if bx <= cx <= (bx + bw) and by <= cy <= (by + bh):
                    current_cluster.append(word)
                    used_indices.add(i)
            
            if current_cluster:
                clusters.append(current_cluster)

        # 2. For remaining unboxed words, fallback to proximity grouping
        leftover_words = [w for i, w in enumerate(word_boxes) if i not in used_indices]
        if leftover_words:
            fallback_clusters = self._group_into_blocks(leftover_words)
            clusters.extend(fallback_clusters)

        return clusters

    def _group_into_blocks(self, word_boxes: list[dict]) -> list[list[dict]]:
        """
        Group word boxes into spatial clusters representing individual booths.
        Uses proximity-based merging: words within ~100px horizontally and
        ~80px vertically are considered part of the same booth text block.
        """
        if not word_boxes:
            return []

        # Sort by y then x for processing order
        words = sorted(word_boxes, key=lambda w: (w["y"], w["x"]))

        # Proximity thresholds (in pixels at 3000px resolution)
        X_GAP = 120   # max horizontal gap between words in same block
        Y_GAP = 90    # max vertical gap between lines in same block

        clusters: list[list[dict]] = []
        used = [False] * len(words)

        for i, word in enumerate(words):
            if used[i]:
                continue
            cluster = [word]
            used[i] = True

            # BFS: find all words close enough to anyone in this cluster
            queue = [word]
            while queue:
                current = queue.pop(0)
                for j, other in enumerate(words):
                    if used[j]:
                        continue
                    # Check proximity to current word
                    dx = abs(current["x"] - other["x"])
                    dy = abs(current["y"] - other["y"])
                    if dx <= X_GAP and dy <= Y_GAP:
                        cluster.append(other)
                        used[j] = True
                        queue.append(other)

            clusters.append(cluster)

        return clusters
