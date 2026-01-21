FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl

COPY . .

EXPOSE 8000

CMD ["uvicorn","main:app","--host","0.0.0.0","--reload","--port","8000"]
