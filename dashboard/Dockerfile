FROM python:3.10-slim

WORKDIR /app

COPY app.py .

RUN pip install streamlit pandas matplotlib

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
