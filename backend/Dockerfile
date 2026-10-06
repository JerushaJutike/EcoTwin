FROM python:3.13-slim

WORKDIR /app

COPY docker/backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./backend/app
COPY simulation ./simulation
COPY baseline ./baseline
COPY analytics ./analytics
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
