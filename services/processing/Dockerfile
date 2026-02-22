FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Standard: zeigt Hilfe/Info, Batch läuft NICHT automatisch
CMD ["python", "run_batch.py", "--help"]
