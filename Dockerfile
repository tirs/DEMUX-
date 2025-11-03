FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads outputs downloads

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port 8000 &\
streamlit run ui/app.py --server.port=8501 --server.address=0.0.0.0"]