import numpy as np
import random
import cv2
from typing import List, Dict
import json
from datetime import datetime


class VegetableDetector:
    def __init__(self):
        self.vegetables = [
            'tomato', 'onion', 'potato', 'carrot', 'cauliflower',
            'brinjal', 'cabbage', 'capsicum', 'cucumber', 'radish',
            'beetroot', 'spinach', 'okra', 'peas', 'ginger',
            'garlic', 'coriander', 'chilli', 'bell_pepper', 'corn'
        ]

        # Realistic detection patterns based on common combinations
        self.realistic_combinations = [
            ['tomato', 'onion', 'potato'],
            ['carrot', 'capsicum', 'cucumber'],
            ['cabbage', 'cauliflower'],
            ['spinach', 'coriander'],
            ['ginger', 'garlic', 'chilli'],
            ['corn', 'peas'],
            ['brinjal', 'okra'],
            ['beetroot', 'radish']
        ]

        # Seasonal availability (affects detection probability)
        self.seasonal_weights = {
            'tomato': 0.9, 'onion': 0.95, 'potato': 0.95, 'carrot': 0.8,
            'cauliflower': 0.7, 'brinjal': 0.8, 'cabbage': 0.75, 'capsicum': 0.85,
            'cucumber': 0.8, 'radish': 0.6, 'beetroot': 0.6, 'spinach': 0.7,
            'okra': 0.75, 'peas': 0.6, 'ginger': 0.9, 'garlic': 0.95,
            'coriander': 0.8, 'chilli': 0.85, 'bell_pepper': 0.8, 'corn': 0.7
        }

        self.confidence_threshold = 0.6
        self.model_loaded = True  # Dummy flag

    def detect(self, image_array: np.ndarray) -> List[Dict]:
        """
        Smart dummy detection that analyzes image colors and patterns
        to provide realistic vegetable detection results
        """
        try:
            # Analyze image to make detection more realistic
            detections = self._analyze_image_and_detect(image_array)

            # Filter by confidence threshold
            filtered_detections = [
                d for d in detections
                if d['confidence'] >= self.confidence_threshold
            ]

            return filtered_detections

        except Exception as e:
            print(f"Detection error: {e}")
            return []

    def _analyze_image_and_detect(self, image_array: np.ndarray) -> List[Dict]:
        """Analyze image colors and patterns to generate realistic detections"""
        detections = []

        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)

        # Analyze dominant colors in image
        dominant_colors = self._get_dominant_colors(hsv)

        # Map colors to likely vegetables
        likely_vegetables = self._map_colors_to_vegetables(dominant_colors)

        # Generate realistic detection count (1-4 vegetables)
        num_detections = random.randint(1, min(4, len(likely_vegetables)))

        # Select vegetables based on color analysis and seasonal weights
        detected_vegetables = self._select_vegetables_realistically(
            likely_vegetables, num_detections
        )

        # Generate detection data for each vegetable
        for vegetable in detected_vegetables:
            detection = self._generate_detection_data(
                vegetable, image_array.shape)
            detections.append(detection)

        return detections

    def _get_dominant_colors(self, hsv_image: np.ndarray) -> List[str]:
        """Extract dominant colors from image"""
        # Calculate color histograms
        h_hist = cv2.calcHist([hsv_image], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv_image], [1], None, [256], [0, 256])
        v_hist = cv2.calcHist([hsv_image], [2], None, [256], [0, 256])

        # Find dominant hue ranges
        dominant_colors = []

        # Red range (tomatoes, chilli, bell_pepper)
        if h_hist[0:10].sum() + h_hist[170:180].sum() > hsv_image.size * 0.1:
            dominant_colors.append('red')

        # Orange range (carrot, corn)
        if h_hist[10:25].sum() > hsv_image.size * 0.1:
            dominant_colors.append('orange')

        # Yellow range (corn, onion)
        if h_hist[25:35].sum() > hsv_image.size * 0.1:
            dominant_colors.append('yellow')

        # Green range (cabbage, spinach, capsicum, cucumber)
        if h_hist[35:85].sum() > hsv_image.size * 0.1:
            dominant_colors.append('green')

        # Brown range (potato, onion, ginger)
        if v_hist[50:150].sum() > hsv_image.size * 0.2:
            dominant_colors.append('brown')

        # White/Light range (cauliflower, radish, garlic)
        if v_hist[200:256].sum() > hsv_image.size * 0.15:
            dominant_colors.append('white')

        return dominant_colors

    def _map_colors_to_vegetables(self, colors: List[str]) -> List[str]:
        """Map detected colors to likely vegetables"""
        color_vegetable_map = {
            'red': ['tomato', 'chilli', 'bell_pepper'],
            'orange': ['carrot', 'corn'],
            'yellow': ['corn', 'onion'],
            'green': ['cabbage', 'spinach', 'capsicum', 'cucumber', 'okra', 'coriander'],
            'brown': ['potato', 'onion', 'ginger'],
            'white': ['cauliflower', 'radish', 'garlic'],
            'purple': ['brinjal', 'onion', 'beetroot']
        }

        likely_vegetables = []
        for color in colors:
            if color in color_vegetable_map:
                likely_vegetables.extend(color_vegetable_map[color])

        # Remove duplicates and add some random vegetables
        likely_vegetables = list(set(likely_vegetables))

        # Add a few random vegetables to simulate real detection variability
        random_vegetables = random.sample(self.vegetables, k=2)
        likely_vegetables.extend(random_vegetables)

        return list(set(likely_vegetables))

    def _select_vegetables_realistically(self, candidates: List[str], count: int) -> List[str]:
        """Select vegetables based on seasonal weights and realistic combinations"""
        # Apply seasonal weights
        weighted_candidates = []
        for vegetable in candidates:
            weight = self.seasonal_weights.get(vegetable, 0.5)
            if random.random() < weight:
                weighted_candidates.append(vegetable)

        # If not enough candidates, add from realistic combinations
        if len(weighted_candidates) < count:
            combination = random.choice(self.realistic_combinations)
            weighted_candidates.extend(combination)

        # Remove duplicates and select final count
        weighted_candidates = list(set(weighted_candidates))

        return random.sample(weighted_candidates, min(count, len(weighted_candidates)))

    def _generate_detection_data(self, vegetable: str, image_shape: tuple) -> Dict:
        """Generate realistic detection data for a vegetable"""
        # Generate realistic confidence (higher for common vegetables)
        base_confidence = 0.65
        if vegetable in ['tomato', 'onion', 'potato']:
            base_confidence = 0.85
        elif vegetable in ['carrot', 'capsicum', 'cucumber']:
            base_confidence = 0.75

        confidence = base_confidence + random.uniform(-0.15, 0.15)
        confidence = max(0.5, min(0.98, confidence))

        # Generate realistic quantity based on vegetable type
        quantity_ranges = {
            'tomato': (0.3, 1.5), 'onion': (0.2, 1.0), 'potato': (0.5, 2.0),
            'carrot': (0.2, 0.8), 'cauliflower': (0.8, 2.5), 'brinjal': (0.3, 1.2),
            'cabbage': (1.0, 3.0), 'capsicum': (0.2, 0.8), 'cucumber': (0.3, 1.0),
            'radish': (0.1, 0.5), 'beetroot': (0.2, 0.8), 'spinach': (0.1, 0.5),
            'okra': (0.1, 0.4), 'peas': (0.1, 0.3), 'ginger': (0.05, 0.2),
            'garlic': (0.05, 0.15), 'coriander': (0.05, 0.1), 'chilli': (0.05, 0.15),
            'bell_pepper': (0.2, 0.8), 'corn': (0.3, 1.0)
        }

        quantity_range = quantity_ranges.get(vegetable, (0.1, 1.0))
        quantity = round(random.uniform(*quantity_range), 2)

        # Generate realistic bounding box
        height, width = image_shape[:2]

        # Box size varies with vegetable type
        box_size_factor = {
            'cabbage': 0.4, 'cauliflower': 0.35, 'corn': 0.3,
            'tomato': 0.15, 'onion': 0.12, 'potato': 0.18,
            'carrot': 0.25, 'cucumber': 0.3, 'brinjal': 0.2,
            'capsicum': 0.18, 'beetroot': 0.15, 'radish': 0.1,
            'spinach': 0.2, 'okra': 0.1, 'peas': 0.08,
            'ginger': 0.08, 'garlic': 0.06, 'coriander': 0.1,
            'chilli': 0.08, 'bell_pepper': 0.18
        }

        box_factor = box_size_factor.get(vegetable, 0.15)
        box_width = int(width * box_factor * random.uniform(0.8, 1.2))
        box_height = int(height * box_factor * random.uniform(0.8, 1.2))

        # Random position ensuring box stays within image
        x1 = random.randint(0, max(1, width - box_width))
        y1 = random.randint(0, max(1, height - box_height))
        x2 = x1 + box_width
        y2 = y1 + box_height

        return {
            'vegetable': vegetable,
            'quantity': quantity,
            'confidence': round(confidence, 3),
            'bbox': [x1, y1, x2, y2],
            'detection_method': 'smart_dummy',
            'timestamp': datetime.now().isoformat()
        }

    def get_supported_vegetables(self) -> List[str]:
        """Get list of supported vegetables"""
        return self.vegetables.copy()

    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for detections"""
        self.confidence_threshold = max(0.1, min(1.0, threshold))

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_type': 'Smart Dummy Detector',
            'version': '1.0.0',
            'supported_vegetables': len(self.vegetables),
            'confidence_threshold': self.confidence_threshold,
            'features': [
                'Color-based analysis',
                'Seasonal weighting',
                'Realistic combinations',
                'Smart quantity estimation'
            ]
        }

    def is_model_ready_for_real_data(self) -> bool:
        """Check if architecture is ready for real model integration"""
        return True  # Architecture is ready for drop-in replacement
