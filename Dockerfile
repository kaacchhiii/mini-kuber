FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/operator.py .

RUN groupadd -f -g 1000 operator && \
    useradd -m -u 1000 -g operator operator && \
    chown -R operator:operator /app

USER operator

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["kopf", "run"]
CMD ["/app/operator.py", "--verbose"]
