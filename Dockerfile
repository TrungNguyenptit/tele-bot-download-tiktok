FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    ffmpeg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

WORKDIR /app
COPY . .

CMD ["python", "bot.py"]