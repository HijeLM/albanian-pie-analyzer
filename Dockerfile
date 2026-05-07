FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG CACHEBUST=2
COPY . .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["/bin/bash", "start.sh"]
