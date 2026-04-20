# syntax=docker/dockerfile:1.7

FROM python:3.12-slim

# Make Python behave nicely in containers:
#  - PYTHONUNBUFFERED: flush stdout/stderr immediately so `docker logs` is live
#  - PYTHONDONTWRITEBYTECODE: don't litter the image with .pyc files
#  - PIP_*: quieter, smaller pip installs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python dependencies first so this layer is cached
# across code-only changes (big speed-up on rebuilds).
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source
COPY . .

# Run as a non-root user for better security
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/Log \
    && chown -R app:app /app
USER app

# Specify the command to run the bot
CMD ["python", "tournament.py"]