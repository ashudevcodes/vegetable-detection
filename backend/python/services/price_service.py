import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math


class PriceService:
    def __init__(self):
        self.locations = ["Delhi", "Mumbai", "Bangalore",
                          "Chennai", "Kolkata", "Hyderabad"]

        # Base prices with realistic Indian market rates (₹ per kg)
        self.base_prices = {
            'tomato': 28, 'onion': 35, 'potato': 25, 'carrot': 45,
            'cauliflower': 40, 'brinjal': 35, 'cabbage': 20, 'capsicum': 60,
            'cucumber': 30, 'radish': 25, 'beetroot': 55, 'spinach': 40,
            'okra': 45, 'peas': 80, 'ginger': 150, 'garlic': 250,
            'coriander': 60, 'chilli': 120, 'bell_pepper': 70, 'corn': 40
        }

        # Location-based price factors
        self.location_factors = {
            'Mumbai': 1.25, 'Delhi': 1.0, 'Bangalore': 1.15,
            'Chennai': 1.05, 'Kolkata': 0.85, 'Hyderabad': 0.95
        }

        # Seasonal factors (simulate real market fluctuations)
        self.seasonal_factors = {
            # High seasonal variation
            'tomato': {'factor': 0.2, 'cycle': 90},
            'onion': {'factor': 0.3, 'cycle': 120},    # Very high variation
            'potato': {'factor': 0.15, 'cycle': 180},  # Moderate variation
            'carrot': {'factor': 0.25, 'cycle': 90},
            'cauliflower': {'factor': 0.35, 'cycle': 60},  # Highly seasonal
            'brinjal': {'factor': 0.2, 'cycle': 120},
            'cabbage': {'factor': 0.3, 'cycle': 60},
            'capsicum': {'factor': 0.15, 'cycle': 90},
            'cucumber': {'factor': 0.2, 'cycle': 90},
            'radish': {'factor': 0.25, 'cycle': 60},
            'beetroot': {'factor': 0.2, 'cycle': 120},
            'spinach': {'factor': 0.3, 'cycle': 45},   # Very seasonal
            'okra': {'factor': 0.25, 'cycle': 90},
            'peas': {'factor': 0.4, 'cycle': 60},      # Extremely seasonal
            'ginger': {'factor': 0.1, 'cycle': 180},   # Stable prices
            'garlic': {'factor': 0.15, 'cycle': 180},
            'coriander': {'factor': 0.35, 'cycle': 30},  # Very volatile
            'chilli': {'factor': 0.2, 'cycle': 120},
            'bell_pepper': {'factor': 0.2, 'cycle': 90},
            'corn': {'factor': 0.3, 'cycle': 90}
        }

        self.contributions = []
        self.price_cache = {}

    def get_price(self, vegetable: str, location: str) -> float:
        """Get realistic price with market fluctuations"""
        if vegetable not in self.base_prices:
            return 30.0  # Default price

        base_price = self.base_prices[vegetable]

        # Apply location factor
        location_factor = self.location_factors.get(location, 1.0)

        # Apply seasonal variation
        seasonal_factor = self._get_seasonal_factor(vegetable)

        # Add daily variation (±5%)
        daily_variation = random.uniform(0.95, 1.05)

        # Apply market volatility (some vegetables are more volatile)
        volatility_factor = self._get_volatility_factor(vegetable)

        final_price = base_price * location_factor * \
            seasonal_factor * daily_variation * volatility_factor

        return round(final_price, 2)

    def _get_seasonal_factor(self, vegetable: str) -> float:
        """Calculate seasonal price factor based on time of year"""
        seasonal_info = self.seasonal_factors.get(
            vegetable, {'factor': 0.1, 'cycle': 90})

        # Use day of year for seasonal calculation
        day_of_year = datetime.now().timetuple().tm_yday
        cycle_days = seasonal_info['cycle']
        variation_factor = seasonal_info['factor']

        # Create sine wave for seasonal variation
        seasonal_multiplier = math.sin(2 * math.pi * day_of_year / cycle_days)
        seasonal_factor = 1 + (variation_factor * seasonal_multiplier)

        # Limit between 50% and 200%
        return max(0.5, min(2.0, seasonal_factor))

    def _get_volatility_factor(self, vegetable: str) -> float:
        """Apply market volatility based on vegetable type"""
        high_volatility = ['onion', 'tomato', 'coriander', 'chilli']
        medium_volatility = ['carrot', 'capsicum', 'okra', 'peas']
        low_volatility = ['potato', 'ginger', 'garlic']

        if vegetable in high_volatility:
            return random.uniform(0.85, 1.15)  # ±15% volatility
        elif vegetable in medium_volatility:
            return random.uniform(0.90, 1.10)  # ±10% volatility
        else:
            return random.uniform(0.95, 1.05)  # ±5% volatility

    def get_locations(self) -> List[str]:
        """Get supported locations"""
        return self.locations.copy()

    def add_contribution(self, contribution: Dict) -> bool:
        """Add user price contribution"""
        try:
            contribution['timestamp'] = datetime.now().isoformat()
            contribution['id'] = len(self.contributions) + 1
            self.contributions.append(contribution)

            # Update base price slightly based on contribution
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
            # Adjust by 5% towards contributed price
            adjustment = (contributed_price - current_base) * 0.05
            self.base_prices[vegetable] = round(current_base + adjustment, 2)

    def predict_price(self, vegetable: str, location: str) -> float:
        """Predict future price (simple trend-based prediction)"""
        current_price = self.get_price(vegetable, location)

        # Simulate price trend prediction
        trend_factor = random.uniform(0.95, 1.05)  # ±5% trend
        predicted_price = current_price * trend_factor

        return round(predicted_price, 2)

    def get_price_history(self, vegetable: str, location: str, days: int = 30) -> List[Dict]:
        """Generate realistic price history"""
        history = []
        base_price = self.get_price(vegetable, location)

        for i in range(days):
            date = datetime.now() - timedelta(days=i)

            # Add some realistic variation to historical prices
            variation = random.uniform(0.85, 1.15)
            historical_price = base_price * variation

            history.append({
                'date': date.isoformat(),
                'price': round(historical_price, 2),
                'vegetable': vegetable,
                'location': location
            })

        return list(reversed(history))  # Chronological order

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

            # Categorize trends
            if predicted_price > current_price * 1.02:
                summary['trending_up'].append(vegetable)
            elif predicted_price < current_price * 0.98:
                summary['trending_down'].append(vegetable)
            else:
                summary['stable'].append(vegetable)

            # Add to price ranges
            summary['price_ranges'][vegetable] = {
                'current': current_price,
                'predicted': predicted_price,
                'trend': 'up' if predicted_price > current_price else 'down' if predicted_price < current_price else 'stable'
            }

        return summary
