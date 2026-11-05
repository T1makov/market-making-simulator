FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=80 \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

COPY requirements-runtime.txt .
RUN pip install -r requirements-runtime.txt

COPY src ./src
COPY results ./results

EXPOSE 80

CMD ["python", "-m", "streamlit", "run", "src/dashboard.py"]
