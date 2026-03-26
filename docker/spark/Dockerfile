FROM jupyter/pyspark-notebook:spark-3.5.0

USER root

# Instalar Delta Lake JARs
RUN pip install --no-cache-dir \
    delta-spark==3.2.0 \
    faker==28.0.0 \
    chispa==0.10.1 \
    plotly==5.22.0 \
    pyarrow==16.1.0 \
    python-dotenv==1.0.1

# Crear directorios de Spark con permisos para jovyan
RUN mkdir -p /tmp/spark /tmp/spark-events && chmod 777 /tmp/spark /tmp/spark-events

# Configuración de Spark optimizada para local
COPY docker/spark/spark-defaults.conf /usr/local/spark/conf/spark-defaults.conf

USER ${NB_UID}

WORKDIR /home/jovyan
