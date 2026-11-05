FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home estudante
COPY --chown=estudante:estudante . .
RUN mkdir -p /app/logs /app/dados/cache && chown -R estudante:estudante /app
USER estudante
CMD ["python", "servidor.py"]
