## Project Overview

Vegetable Detection App 

---
## Tech Stack

This is a full-stack object detection application using:

* **Frontend**: Vanilla JavaScript + HTML + Webcam Access
* **Backend**: Go + Gin Framework
* **Detection**: YOLOv8 (Ultralytics, Python + Flask)
* **Container Runtime**: Podman/Docker + Podman-Compose/Podman-Compose

---
## Architecture

```text
+-------------+        POST /upload         +-----------------+
|   Frontend  | --------------------------> |      Go API     |
|  (JavaScript)    |                             | (REST with Gin) |
+-------------+                             +-----------------+
       |                                              |
       |                                              |---> [Object Detection] (Go/OpenCV or via Python microservice)
       |                                              |
       |        JSON response w/ boxes, labels        |
       +<---------------------------------------------+
       |
       |--> Display results (bounding boxes etc.)
```
---
##  Project Structure

```bash
object-detector/
├── backend/              # Go backend API (uploads + forwards to detection)
│   ├── main.go
│   ├── Dockerfile
│   └── wait-for-it.sh
├── detection/            # YOLOv8 Flask detection service
│   ├── detect.py
│   └── Dockerfile
├── frontend/             # Vanilla JS + Webcam + UI
│   ├── index.html
│   ├── main.js
│   ├── styles.css
│   └── Dockerfile
├── docker-compose.yml
├── start.sh
└── cleanup-object-detector.sh
```
---
##  How to Run the Project

### 1. Run the full app

```bash
cd object-detector/
./start.sh
```

### 2. Open the app in your browser

```txt
http://localhost:5173
```

* Allow camera access
* Click **"Detect Bottle"**
* The app will show bounding boxes on detected bottles

---

##  Stop and Remove Everything

```bash
./cleanup-object-detector.sh

```
---

## Scripts

### Reset and Rebuild the App

```bash
./reset-object-detector.sh
```
---

## ✅ Requirements

* Python 3.10+, Go 1.22 (inside containers only)
* YOLOv8 model (`ultralytics` handles download in container)

---

> Created for educational and testing purposes. Supports real-time webcam capture and detection.
