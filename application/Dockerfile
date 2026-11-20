FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=wsgi \
    FLASK_DEBUG=0 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
