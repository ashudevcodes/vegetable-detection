from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.vegetable_detector import VegetableDetector
from services.price_service import PriceService
from utils.image_processor import ImageProcessor
from datetime import datetime
import asyncio

app = FastAPI(title="Real Vegetable Detection API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = VegetableDetector()
price_service = PriceService()
image_processor = ImageProcessor()


@app.post("/detect")
async def detect_vegetables(image: UploadFile = File(...), location: str = Form("Delhi")):
    """Real vegetable detection using YOLOv8 ML model"""
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, detail="File must be an image")

        image_array = await image_processor.process_upload(image)

        if not detector.model_loaded:
            raise HTTPException(status_code=503, detail="ML model not loaded")

        loop = asyncio.get_event_loop()
        detections = await loop.run_in_executor(None, detector.detect, image_array)

        if not detections:
            return {
                "message": "No vegetables detected",
                "detections": [],
                "total_items": 0,
                "total_value": 0.0
            }

        results = []
        total_value = 0.0

        for detection in detections:
            price = price_service.get_price(detection['vegetable'], location)
            line_total = round(detection['quantity'] * price, 2)
            total_value += line_total

            results.append({
                'vegetable': detection['vegetable'],
                'quantity': detection['quantity'],
                'confidence': detection['confidence'],
                'price_per_kg': price,
                'line_total': line_total,
                'bbox': detection['bbox'],
                'detection_method': detection['detection_method'],
                'timestamp': detection['timestamp'],
            })

        return {
            "detections": results,
            "summary": {
                "total_items": len(results),
                "total_value": round(total_value, 2),
                "location": location,
                "detection_time": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )


@app.get("/model/info")
async def get_model_info():
    """Get real ML model information"""
    model_info = detector.get_model_info()
    return {
        **model_info,
        "api_version": "2.0.0",
        "model_status": "loaded" if detector.model_loaded else "not_loaded",
        "current_mode": "production_ml"
    }


@app.get("/model/ready-for-real-data")
async def check_real_data_readiness():
    """Updated to reflect real ML model status"""
    return {
        'ready': detector.model_loaded,
        'current_mode': 'production_ml',
        'model_type': 'YOLOv8',
        'status': 'Real ML model active',
        'features': [
            'Real vegetable detection',
            'Accurate bounding boxes',
            'Production-ready inference',
            'YOLOv8 based detection'
        ]
    }


@app.get("/health")
async def health_check():
    """Enhanced health check for real ML model"""
    model_status = "healthy" if detector.model_loaded else "model_not_loaded"

    return {
        "status": model_status,
        "message": "Real ML vegetable detection system running",
        "mode": "production",
        "model_loaded": detector.model_loaded,
        "api_version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.on_event("startup")
async def startup_event():
    """Warm up the model on startup"""
    print("Starting Real Vegetable Detection API...")
    if detector.model_loaded:
        print("✅ YOLOv8 model loaded successfully")
        import numpy as np
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = detector.detect(dummy_image)
        print("✅ Model warmed up")
    else:
        print("❌ Model failed to load - check dependencies")
