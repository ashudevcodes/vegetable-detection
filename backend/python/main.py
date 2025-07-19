from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.vegetable_detector import VegetableDetector
from services.price_service import PriceService
from utils.image_processor import ImageProcessor
from datetime import datetime

app = FastAPI(title="Smart Dummy Vegetable Detection API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
detector = VegetableDetector()
price_service = PriceService()
image_processor = ImageProcessor()


@app.post("/detect")
async def detect_vegetables(image: UploadFile = File(...), location: str = Form("Delhi")):
    """Smart vegetable detection with realistic results"""
    try:
        # Process image
        image_array = await image_processor.process_upload(image)
        print(image_array)

        # Detect vegetables using smart dummy detector
        detections = detector.detect(image_array)
        print(detections)

        # Get realistic prices for detected vegetables
        results = []
        for detection in detections:
            price = price_service.get_price(detection['vegetable'], location)

            results.append({
                'vegetable': detection['vegetable'],
                'quantity': detection['quantity'],
                'confidence': detection['confidence'],
                'price_per_kg': price,
                'line_total': round(detection['quantity'] * price, 2),
                'bbox': detection['bbox'],
                'detection_method': 'smart_dummy',
                'timestamp': detection['timestamp'],
            })

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Detection failed: {str(e)}")


# @app.get("/vegetables")
# async def get_vegetables():
#     """Get supported vegetables"""
#     return detector.get_supported_vegetables()
#
#
# @app.get("/locations")
# async def get_locations():
#     """Get supported locations"""
#     return price_service.get_locations()
#
#
# @app.get("/price/{vegetable}")
# async def get_price(vegetable: str, location: str = "Delhi"):
#     """Get current price for vegetable"""
#     try:
#         price = price_service.get_price(vegetable, location)
#         return {
#             'vegetable': vegetable,
#             'location': location,
#             'price': price,
#             'currency': 'INR',
#             'unit': 'kg',
#             'timestamp': datetime.now().isoformat(),
#             'source': 'smart_dummy'
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @app.get("/market-summary/{location}")
# async def get_market_summary(location: str):
#     """Get market summary for location"""
#     try:
#         summary = price_service.get_market_summary(location)
#         return summary
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @app.post("/contribute")
# async def contribute_price(data: dict):
#     """Submit price contribution"""
#     try:
#         success = price_service.add_contribution(data)
#         if success:
#             return {"status": "success", "message": "Price contributed successfully"}
#         else:
#             raise HTTPException(
#                 status_code=400, detail="Failed to add contribution")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#

@app.get("/model/info")
async def get_model_info():
    """Get model information"""
    return detector.get_model_info()


@app.get("/model/ready-for-real-data")
async def check_real_data_readiness():
    """Check if system is ready for real ML model"""
    return {
        'ready': detector.is_model_ready_for_real_data(),
        'current_mode': 'smart_dummy',
        'upgrade_path': 'Drop-in replacement ready',
        'benefits_of_upgrade': [
            'Real vegetable detection',
            'Higher accuracy',
            'Custom trained model',
            'Better quantity estimation'
        ]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Smart dummy detection system running",
        "mode": "development_ready",
        "timestamp": datetime.now().isoformat()
    }
