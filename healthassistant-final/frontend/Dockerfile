FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for speech recognition and audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    portaudio19-dev \
    libportaudio2 \
    flac \
    ffmpeg \
    libasound2-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

# If you have a requirements.txt in the frontend folder, copy & install it
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt || true

# Ensure streamlit is available
RUN pip install --no-cache-dir streamlit || true

# Copy frontend files from build context into image
COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
