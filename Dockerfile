# Use official Python 3.8 slim image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies for ML, GUI, audio, and OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxcb1 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-shape0-dev \
    libxcb-randr0-dev \
    libxkbcommon-x11-0 \
    libxkbcommon-dev \
    libgtk-3-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    portaudio19-dev \
    xvfb \
    x11-utils \
    xauth \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*



# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLTK packages
RUN python -m nltk.downloader omw-1.4 stopwords wordnet words

# Expose display environment for GUI
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Start the app using X virtual framebuffer for GUI
CMD ["xvfb-run", "-a", "python", "Main.py"]
