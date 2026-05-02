FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/processed \
    exports ml/saved_models

EXPOSE 8501 5001

ENV SUPABASE_URL=""
ENV SUPABASE_KEY=""
ENV FLASK_DEBUG="false"
ENV API_BASE_URL="http://localhost:5001"

CMD ["sh", "-c", "python api/app.py & streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false"]
