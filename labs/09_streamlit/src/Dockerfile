FROM python:3.9-slim

WORKDIR /app

COPY data_visualization.py /app/src/
COPY requirements.txt /app/src/

EXPOSE 8501

RUN pip install -r src/requirements.txt

CMD ["streamlit", "run", "src/data_visualization.py", "--server.port=8501", "--server.address=0.0.0.0"]