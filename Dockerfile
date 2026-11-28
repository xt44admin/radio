FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn
COPY app.py /app.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
