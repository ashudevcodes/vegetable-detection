FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (cached layer)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip (cached layer)
RUN pip install --upgrade pip

# Copy ONLY requirements.txt first (enables layer caching)
COPY requirements.txt .

# Install requirements first (cached unless requirements.txt changes)
RUN pip install --no-cache-dir --resume-retries=5 -r requirements.txt

# Install TensorFlow based on build argument (after requirements to avoid conflicts)
ARG INSTALL_GPU=false
RUN if [ "$INSTALL_GPU" = "true" ]; then \
    pip install --no-cache-dir tensorflow-gpu==2.15.0; \
    else \
    pip install --no-cache-dir tensorflow-cpu==2.15.0; \
    fi

# Copy application code (this layer changes most frequently)
COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
