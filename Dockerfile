FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install setuptools
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py install

COPY . /app/

# Set environment variables (defaults can be overridden)
ENV AWS_REGION=us-east-1
ENV REFRESH_INTERVAL=60
ENV PORT=8200
ENV MAX_WORKERS=4

EXPOSE 8200

CMD ["prometheus-api-gateway-v2-exporter"]

