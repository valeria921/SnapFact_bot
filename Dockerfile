FROM python:3.11

WORKDIR /app

COPY bot/ .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "snapfact.py"]