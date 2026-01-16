FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    ffmpeg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 👇 COPY requirements trước
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# 👇 COPY phần còn lại sau
COPY . .

CMD ["python", "bot.py"]
