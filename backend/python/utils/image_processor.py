import cv2
import numpy as np
from PIL import Image
import io
from fastapi import UploadFile
from typing import Tuple


class ImageProcessor:
    def __init__(self):
        self.supported_formats = ['jpg', 'jpeg', 'png', 'bmp']
        self.max_size = (640, 480)

    async def process_upload(self, upload_file: UploadFile) -> np.ndarray:
        """Process uploaded image file"""
        try:
            image_data = await upload_file.read()

            image_pil = Image.open(io.BytesIO(image_data))

            if image_pil.mode != 'RGB':
                image_pil = image_pil.convert('RGB')

            if image_pil.size[0] > self.max_size[0] or image_pil.size[1] > self.max_size[1]:
                image_pil = image_pil.resize(
                    self.max_size, Image.Resampling.LANCZOS)

            image_array = np.array(image_pil)

            return image_array

        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

    def preprocess_for_detection(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for ML model"""
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image = image.astype(np.float32) / 255.0

        return image

    def resize_image(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Resize image to target size"""
        return cv2.resize(image, target_size)

    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better detection"""
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])

        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        return enhanced
