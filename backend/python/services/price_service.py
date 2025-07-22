import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math


class PriceService:
    def __init__(self):
        self.locations = ["Delhi", "Mumbai", "Bangalore",
                          "Chennai", "Kolkata", "Hyderabad"]

        self.base_prices = {
            'tomato': 28, 'onion': 35, 'potato': 25, 'carrot': 45,
            'cauliflower': 40, 'brinjal': 35, 'cabbage': 20, 'capsicum': 60,
            'cucumber': 30, 'radish': 25, 'beetroot': 55, 'spinach': 40,
            'okra': 45, 'peas': 80, 'ginger': 150, 'garlic': 250,
            'coriander': 60, 'chilli': 120, 'bell_pepper': 70, 'corn': 40
        }

        self.location_factors = {
            'Mumbai': 1.25, 'Delhi': 1.0, 'Bangalore': 1.15,
            'Chennai': 1.05, 'Kolkata': 0.85, 'Hyderabad': 0.95
        }

        self.seasonal_factors = {
            'tomato': {'factor': 0.2, 'cycle': 90},
            'onion': {'factor': 0.3, 'cycle': 120},
            'potato': {'factor': 0.15, 'cycle': 180},
            'carrot': {'factor': 0.25, 'cycle': 90},
            'cauliflower': {'factor': 0.35, 'cycle': 60},
            'brinjal': {'factor': 0.2, 'cycle': 120},
            'cabbage': {'factor': 0.3, 'cycle': 60},
            'capsicum': {'factor': 0.15, 'cycle': 90},
            'cucumber': {'factor': 0.2, 'cycle': 90},
            'radish': {'factor': 0.25, 'cycle': 60},
            'beetroot': {'factor': 0.2, 'cycle': 120},
            'spinach': {'factor': 0.3, 'cycle': 45},
            'okra': {'factor': 0.25, 'cycle': 90},
            'peas': {'factor': 0.4, 'cycle': 60},
            'ginger': {'factor': 0.1, 'cycle': 180},
            'garlic': {'factor': 0.15, 'cycle': 180},
            'coriander': {'factor': 0.35, 'cycle': 30},
            'chilli': {'factor': 0.2, 'cycle': 120},
            'bell_pepper': {'factor': 0.2, 'cycle': 90},
            'corn': {'factor': 0.3, 'cycle': 90}
        }

        self.contributions = []
        self.price_cache = {}

    def get_price(self, vegetable: str, location: str) -> float:
        """Get realistic price with market fluctuations"""
        if vegetable not in self.base_prices:
            return 30.0

        base_price = self.base_prices[vegetable]

        location_factor = self.location_factors.get(location, 1.0)

        seasonal_factor = self._get_seasonal_factor(vegetable)

        daily_variation = random.uniform(0.95, 1.05)

        volatility_factor = self._get_volatility_factor(vegetable)

        final_price = base_price * location_factor * \
            seasonal_factor * daily_variation * volatility_factor

        return round(final_price, 2)

    def _get_seasonal_factor(self, vegetable: str) -> float:
        """Calculate seasonal price factor based on time of year"""
        seasonal_info = self.seasonal_factors.get(
            vegetable, {'factor': 0.1, 'cycle': 90})

        day_of_year = datetime.now().timetuple().tm_yday
        cycle_days = seasonal_info['cycle']
        variation_factor = seasonal_info['factor']

        seasonal_multiplier = math.sin(2 * math.pi * day_of_year / cycle_days)
        seasonal_factor = 1 + (variation_factor * seasonal_multiplier)

        return max(0.5, min(2.0, seasonal_factor))

    def _get_volatility_factor(self, vegetable: str) -> float:
        """Apply market volatility based on vegetable type"""
        high_volatility = ['onion', 'tomato', 'coriander', 'chilli']
        medium_volatility = ['carrot', 'capsicum', 'okra', 'peas']
        low_volatility = ['potato', 'ginger', 'garlic']

        if vegetable in high_volatility:
            return random.uniform(0.85, 1.15)
        elif vegetable in medium_volatility:
            return random.uniform(0.90, 1.10)
        else:
            return random.uniform(0.95, 1.05)

    def get_locations(self) -> List[str]:
        """Get supported locations"""
        return self.locations.copy()

    def add_contribution(self, contribution: Dict) -> bool:
        """Add user price contribution"""
        try:
            contribution['timestamp'] = datetime.now().isoformat()
            contribution['id'] = len(self.contributions) + 1
            self.contributions.append(contribution)

            self._update_base_price_from_contribution(contribution)

            return True
        except Exception as e:
            print(f"Error adding contribution: {e}")
            return False

    def _update_base_price_from_contribution(self, contribution: Dict):
        """Slightly adjust base price based on user contribution"""
        vegetable = contribution['vegetable']
        contributed_price = contribution['price']

        if vegetable in self.base_prices:
            current_base = self.base_prices[vegetable]
            adjustment = (contributed_price - current_base) * 0.05
            self.base_prices[vegetable] = round(current_base + adjustment, 2)

    def predict_price(self, vegetable: str, location: str) -> float:
        """Predict future price (simple trend-based prediction)"""
        current_price = self.get_price(vegetable, location)

        trend_factor = random.uniform(0.95, 1.05)
        predicted_price = current_price * trend_factor

        return round(predicted_price, 2)

    def get_price_history(self, vegetable: str, location: str, days: int = 30) -> List[Dict]:
        """Generate realistic price history"""
        history = []
        base_price = self.get_price(vegetable, location)

        for i in range(days):
            date = datetime.now() - timedelta(days=i)

            variation = random.uniform(0.85, 1.15)
            historical_price = base_price * variation

            history.append({
                'date': date.isoformat(),
                'price': round(historical_price, 2),
                'vegetable': vegetable,
                'location': location
            })

        return list(reversed(history))

    def get_market_summary(self, location: str) -> Dict:
        """Get market summary for location"""
        summary = {
            'location': location,
            'date': datetime.now().isoformat(),
            'total_vegetables': len(self.base_prices),
            'price_ranges': {},
            'trending_up': [],
            'trending_down': [],
            'stable': []
        }

        for vegetable in self.base_prices:
            current_price = self.get_price(vegetable, location)
            predicted_price = self.predict_price(vegetable, location)

            if predicted_price > current_price * 1.02:
                summary['trending_up'].append(vegetable)
            elif predicted_price < current_price * 0.98:
                summary['trending_down'].append(vegetable)
            else:
                summary['stable'].append(vegetable)

            summary['price_ranges'][vegetable] = {
                'current': current_price,
                'predicted': predicted_price,
                'trend': 'up' if predicted_price > current_price else 'down' if predicted_price < current_price else 'stable'
            }

        return summary
