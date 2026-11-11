FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

EXPOSE 5000

# Run as a non-root user for good hygiene, even though this is a toy app.
RUN useradd -m ctfuser
USER ctfuser

CMD ["python", "app.py"]
