import numpy as np
import cv2
from typing import List, Dict
import json
from datetime import datetime
import torch
from ultralytics import YOLO
import requests
from pathlib import Path


class VegetableDetector:
    def __init__(self, model_path: str = None):
        self.vegetables = [
            'tomato', 'onion', 'potato', 'carrot', 'cauliflower',
            'brinjal', 'cabbage', 'capsicum', 'cucumber', 'radish',
            'beetroot', 'spinach', 'okra', 'peas', 'ginger',
            'garlic', 'coriander', 'chilli', 'bell_pepper', 'corn'
        ]

        self.confidence_threshold = 0.6
        self.model = None
        self.model_loaded = False

        # Load the model
        self._load_model(model_path)

    def _load_model(self, model_path: str = None):
        """Load YOLOv8 model for vegetable detection"""
        try:
            if model_path is None:
                # Use pre-trained YOLO model and fine-tune class mapping
                print("Loading pre-trained YOLOv8 model...")
                # or yolov8s.pt, yolov8m.pt for better accuracy
                self.model = YOLO('yolov8n.pt')
            else:
                # Load custom trained model
                print(f"Loading custom model from {model_path}")
                self.model = YOLO(model_path)

            self.model_loaded = True
            print("Model loaded successfully!")

        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model_loaded = False

    def detect(self, image_array: np.ndarray) -> List[Dict]:
        """
        Real vegetable detection using YOLOv8 model
        """
        if not self.model_loaded:
            print("Model not loaded!")
            return []

        try:
            # Run inference
            results = self.model(image_array, conf=self.confidence_threshold)

            # Process results
            detections = self._process_yolo_results(
                results[0], image_array.shape)

            return detections

        except Exception as e:
            print(f"Detection error: {e}")
            return []

    def _process_yolo_results(self, result, image_shape: tuple) -> List[Dict]:
        """Process YOLO detection results into our format"""
        detections = []

        if result.boxes is not None:
            boxes = result.boxes.cpu().numpy()

            for i, box in enumerate(boxes.data):
                x1, y1, x2, y2, confidence, class_id = box

                # Get class name
                class_name = self.model.names[int(class_id)]

                # Map detected class to our vegetable names
                vegetable_name = self._map_class_to_vegetable(class_name)

                if vegetable_name:
                    detection = {
                        'vegetable': vegetable_name,
                        'quantity': self._estimate_quantity_from_bbox(x1, y1, x2, y2, image_shape),
                        'confidence': round(float(confidence), 3),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'detection_method': 'yolov8_real',
                        'timestamp': datetime.now().isoformat()
                    }
                    detections.append(detection)

        return detections

    def _map_class_to_vegetable(self, class_name: str) -> str:
        """Map YOLO class names to our vegetable names"""
        # Mapping from common COCO classes to vegetables
        class_mapping = {
            'apple': 'tomato',  # Close enough for demo
            'orange': 'carrot',
            'banana': 'corn',
            'broccoli': 'cauliflower',
            'carrot': 'carrot',
            # Add more mappings as needed
        }

        # Direct match
        if class_name.lower() in self.vegetables:
            return class_name.lower()

        # Mapped match
        if class_name.lower() in class_mapping:
            return class_mapping[class_name.lower()]

        # For unknown classes, you might want to return None or handle differently
        return None

    def _estimate_quantity_from_bbox(self, x1: float, y1: float, x2: float, y2: float, image_shape: tuple) -> float:
        """Estimate quantity based on bounding box size"""
        bbox_area = (x2 - x1) * (y2 - y1)
        image_area = image_shape[0] * image_shape[1]
        relative_size = bbox_area / image_area

        # Simple heuristic: larger objects = more quantity
        base_quantity = 0.1
        size_factor = relative_size * 10

        return round(base_quantity + size_factor, 2)

    def detect_and_draw(self, image_array: np.ndarray, draw_boxes: bool = True) -> tuple:
        """
        Detect vegetables and optionally draw bounding boxes
        Returns: (detections, annotated_image)
        """
        detections = self.detect(image_array)
        annotated_image = image_array.copy()

        if draw_boxes:
            annotated_image = self._draw_detections(
                annotated_image, detections)

        return detections, annotated_image

    def _draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels on image"""
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            vegetable = detection['vegetable']
            confidence = detection['confidence']

            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            label = f"{vegetable}: {confidence:.2f}"
            label_size = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]

            # Background rectangle for text
            cv2.rectangle(image, (x1, y1 - label_size[1] - 10),
                          (x1 + label_size[0], y1), (0, 255, 0), -1)

            # Text
            cv2.putText(image, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        return image

    # Keep existing utility methods
    def get_supported_vegetables(self) -> List[str]:
        return self.vegetables.copy()

    def set_confidence_threshold(self, threshold: float):
        self.confidence_threshold = max(0.1, min(1.0, threshold))

    def get_model_info(self) -> Dict:
        return {
            'model_type': 'YOLOv8 Real Detector',
            'version': '1.0.0',
            'model_loaded': self.model_loaded,
            'supported_vegetables': len(self.vegetables),
            'confidence_threshold': self.confidence_threshold,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }
