FROM python:3.13-alpine
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && pip uninstall -y pip \
    && find /usr/local -name '__pycache__' -type d -prune -exec rm -rf {} +
COPY main.py .
USER 65534
EXPOSE 8000
CMD ["python", "main.py"]
