from flask import Flask, request, jsonify
from ultralytics import YOLO
import os

app = Flask(__name__)
model = YOLO("yolov8n.pt")


@app.route("/detect", methods=["POST"])
def detect():
    file = request.files["image"]
    path = "temp.jpg"
    file.save(path)
    results = model(path)[0]
    boxes = []
    for box in results.boxes:
        cls = int(box.cls[0])
        label = results.names[cls]
        if "bottle" in label.lower():
            x, y, w, h = map(int, box.xywh[0])
            boxes.append({"x": x, "y": y, "width": w,
                         "height": h, "label": label})
    return jsonify(boxes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
