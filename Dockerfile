FROM python:3.14-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV ALLOWED_ORIGINS="https://stock-dashboard.vercel.app,http://localhost:5500"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
