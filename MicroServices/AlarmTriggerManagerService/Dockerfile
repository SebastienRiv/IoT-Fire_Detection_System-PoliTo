FROM python:3.10-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran \
    liblapack-dev \
    libopenblas-dev \
    build-essential \
    cython3 \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy project files
COPY ./MicroServices/AlarmTriggerManagerService /workspace/MicroServices/AlarmTriggerManagerService
COPY ./src /workspace/src
COPY ./requirements.txt /workspace/requirements.txt

# Add workspace to PYTHONPATH
ENV PYTHONPATH="/workspace:${PYTHONPATH}"

# Désactiver le buffering Python
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r /workspace/requirements.txt

# Command to run
CMD ["python3", "-u", "MicroServices/AlarmTriggerManagerService/AlarmTriggerManagerCreator.py"]