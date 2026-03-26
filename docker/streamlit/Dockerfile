FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    streamlit==1.37.0 \
    plotly==5.22.0 \
    pandas==2.2.2 \
    pyarrow==16.1.0 \
    deltalake==0.18.2

COPY dashboard/ /app/dashboard/
COPY src/ /app/src/

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
