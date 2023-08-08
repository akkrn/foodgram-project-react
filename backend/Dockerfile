FROM python:3.9-slim
WORKDIR /app/requirements
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
WORKDIR /app
COPY . .
CMD ["sh", "docker-entrypoint.sh"]