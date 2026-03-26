# REPO_STRUCTURE.md — Estructura del Repositorio y Configuración

---

## Árbol de directorios

```
bigdata-fraud-pyspark/
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions: lint + test + Docker build
│
├── docker/
│   ├── spark/
│   │   └── Dockerfile                # Imagen Spark + PySpark + Delta Lake + JupyterLab
│   └── streamlit/
│       └── Dockerfile                # Imagen Streamlit para dashboard
│
├── notebooks/
│   ├── 01_ingesta_bronze.ipynb       # Ingesta de datos y capa Bronze
│   ├── 02_transformaciones_silver_gold.ipynb  # Limpieza, features, optimizaciones
│   └── 03_analisis_fraude_reportes.ipynb      # Reglas de fraude, SQL, time travel
│
├── src/
│   ├── __init__.py
│   ├── config.py                     # Configuración centralizada (paths, Spark config)
│   ├── data_generator.py             # Generador de datos sintéticos a escala
│   ├── transformations.py            # Funciones de transformación reutilizables
│   ├── fraud_rules.py                # Reglas de detección de fraude
│   └── utils.py                      # Utilidades (logging, benchmarking)
│
├── dashboard/
│   ├── app.py                        # Streamlit dashboard principal
│   ├── pages/
│   │   ├── 01_overview.py            # Resumen general de transacciones
│   │   ├── 02_fraud_analysis.py      # Análisis de fraude detallado
│   │   └── 03_optimizations.py       # Benchmarks y comparaciones
│   └── components/
│       └── charts.py                 # Funciones de Plotly reutilizables
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures: SparkSession de test
│   ├── test_transformations.py       # Tests de funciones de transformación
│   ├── test_fraud_rules.py           # Tests de reglas de fraude
│   └── test_data_generator.py        # Tests del generador de datos
│
├── data/
│   ├── raw/                          # Datos crudos descargados (gitignored)
│   │   └── .gitkeep
│   ├── seed/                         # Muestra pequeña para tests y demos
│   │   └── sample_transactions.csv
│   └── delta/                        # Tablas Delta Lake (gitignored)
│       ├── bronze/
│       ├── silver/
│       └── gold/
│
├── docs/
│   ├── PROJECT_CONTEXT.md            # Este documento de contexto
│   ├── OPTIMIZATIONS.md              # Documento de optimizaciones aplicadas
│   └── architecture.png              # Diagrama de arquitectura exportado
│
├── scripts/
│   ├── download_data.sh              # Script para descargar datos de Kaggle
│   └── generate_data.py              # CLI para generar datos sintéticos
│
├── .env.example                      # Plantilla de variables de entorno
├── .gitignore
├── docker-compose.yml                # Orquestación de servicios
├── pyproject.toml                    # Configuración del proyecto Python + ruff
├── requirements.txt                  # Dependencias Python (pinned)
├── requirements-dev.txt              # Dependencias de desarrollo
├── Makefile                          # Atajos de comandos frecuentes
├── LICENSE                           # MIT License
└── README.md                         # Documentación principal
```

---

## Archivos de configuración

### docker-compose.yml

```yaml
version: "3.9"

services:
  spark-jupyter:
    build:
      context: .
      dockerfile: docker/spark/Dockerfile
    container_name: spark-jupyter
    ports:
      - "8888:8888"   # JupyterLab
      - "4040:4040"   # Spark UI
    volumes:
      - ./notebooks:/home/jovyan/notebooks
      - ./src:/home/jovyan/src
      - ./data:/home/jovyan/data
      - ./scripts:/home/jovyan/scripts
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - SPARK_DRIVER_MEMORY=${SPARK_DRIVER_MEMORY:-8g}
      - SPARK_EXECUTOR_MEMORY=${SPARK_EXECUTOR_MEMORY:-4g}
      - SPARK_LOCAL_DIRS=/tmp/spark
      - DELTA_LAKE_VERSION=3.2.0
    env_file:
      - .env
    deploy:
      resources:
        limits:
          memory: 16g
          cpus: "8"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/api"]
      interval: 30s
      timeout: 10s
      retries: 3

  streamlit:
    build:
      context: .
      dockerfile: docker/streamlit/Dockerfile
    container_name: streamlit-dashboard
    ports:
      - "8501:8501"
    volumes:
      - ./dashboard:/app/dashboard
      - ./data/delta/gold:/app/data/gold:ro
      - ./src:/app/src
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    env_file:
      - .env
    depends_on:
      spark-jupyter:
        condition: service_healthy
```

### docker/spark/Dockerfile

```dockerfile
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

# Configurar Spark para Delta Lake
ENV PYSPARK_SUBMIT_ARGS="--packages io.delta:delta-spark_2.12:3.2.0 \
    --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
    --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
    pyspark-shell"

# Configuración de Spark optimizada para local
COPY docker/spark/spark-defaults.conf /usr/local/spark/conf/spark-defaults.conf

USER ${NB_UID}

WORKDIR /home/jovyan
```

### docker/spark/spark-defaults.conf

```properties
# === Motor y memoria ===
spark.driver.memory                  8g
spark.executor.memory                4g
spark.driver.maxResultSize           2g
spark.sql.shuffle.partitions         200

# === Adaptive Query Execution (AQE) ===
spark.sql.adaptive.enabled                          true
spark.sql.adaptive.coalescePartitions.enabled        true
spark.sql.adaptive.skewJoin.enabled                  true
spark.sql.adaptive.localShuffleReader.enabled         true

# === Delta Lake ===
spark.sql.extensions                                 io.delta.sql.DeltaSparkSessionExtension
spark.sql.catalog.spark_catalog                      org.apache.spark.sql.delta.catalog.DeltaCatalog
spark.databricks.delta.retentionDurationCheck.enabled false

# === Optimización general ===
spark.serializer                     org.apache.spark.serializer.KryoSerializer
spark.sql.parquet.compression.codec  zstd
spark.sql.broadcastTimeout           600
spark.sql.autoBroadcastJoinThreshold  50MB
spark.local.dir                      /tmp/spark

# === UI ===
spark.ui.showConsoleProgress         true
spark.eventLog.enabled               true
spark.eventLog.dir                   /tmp/spark-events
```

### docker/streamlit/Dockerfile

```dockerfile
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
```

### requirements.txt

```txt
pyspark==3.5.2
delta-spark==3.2.0
faker==28.0.0
pyarrow==16.1.0
pandas==2.2.2
plotly==5.22.0
streamlit==1.37.0
python-dotenv==1.0.1
```

### requirements-dev.txt

```txt
-r requirements.txt
pytest==8.2.2
chispa==0.10.1
ruff==0.5.0
pre-commit==3.7.1
ipykernel==6.29.4
```

### pyproject.toml

```toml
[project]
name = "bigdata-fraud-pyspark"
version = "1.0.0"
description = "Big Data analytics pipeline for fraud detection using PySpark and Delta Lake"
requires-python = ">=3.10"
license = { text = "MIT" }

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "W", "UP", "S", "B", "SIM"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::FutureWarning",
]
```

### Makefile

```makefile
.PHONY: help up down build test lint clean generate-data

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Docker ===
up: ## Levantar todos los servicios
	docker compose up -d

down: ## Detener todos los servicios
	docker compose down

build: ## Reconstruir imágenes Docker
	docker compose build --no-cache

logs: ## Ver logs de todos los servicios
	docker compose logs -f

# === Desarrollo ===
lint: ## Ejecutar linter (ruff)
	ruff check src/ tests/ dashboard/ --fix
	ruff format src/ tests/ dashboard/

test: ## Ejecutar tests
	docker compose exec spark-jupyter pytest tests/ -v

test-local: ## Ejecutar tests localmente (requiere Spark instalado)
	pytest tests/ -v

# === Datos ===
generate-data: ## Generar datos sintéticos (100M+ registros)
	docker compose exec spark-jupyter python scripts/generate_data.py \
		--num-records 100000000 \
		--output-path data/raw/transactions

download-data: ## Descargar dataset seed de Kaggle
	bash scripts/download_data.sh

# === Limpieza ===
clean: ## Limpiar datos generados y caches de Spark
	rm -rf data/raw/*.parquet data/raw/*.csv
	rm -rf data/delta/bronze/* data/delta/silver/* data/delta/gold/*
	rm -rf /tmp/spark/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null || true

clean-all: clean down ## Limpieza total (datos + contenedores)
	docker compose down -v --rmi local
```

### .env.example

```bash
# === Spark Configuration ===
SPARK_DRIVER_MEMORY=8g
SPARK_EXECUTOR_MEMORY=4g

# === Kaggle (opcional, para descarga automática) ===
KAGGLE_USERNAME=
KAGGLE_KEY=

# === Paths ===
DATA_RAW_PATH=data/raw
DATA_DELTA_PATH=data/delta
```

### .gitignore

```gitignore
# === Python ===
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/

# === Jupyter ===
.ipynb_checkpoints/
*.ipynb_metadata/

# === Data (no subir datos pesados) ===
data/raw/*.csv
data/raw/*.parquet
data/delta/bronze/
data/delta/silver/
data/delta/gold/

# === Spark ===
spark-warehouse/
metastore_db/
derby.log
/tmp/spark/
/tmp/spark-events/

# === Environment ===
.env
.venv/
venv/

# === IDE ===
.idea/
.vscode/
*.swp
*.swo

# === OS ===
.DS_Store
Thumbs.db
```

### .github/workflows/ci.yml

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install ruff
        run: pip install ruff==0.5.0
      - name: Run linter
        run: |
          ruff check src/ tests/ dashboard/
          ruff format --check src/ tests/ dashboard/

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest tests/ -v --tb=short
        env:
          SPARK_LOCAL_IP: 127.0.0.1

  docker-build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Build Spark image
        run: docker build -f docker/spark/Dockerfile -t bigdata-fraud-spark .
      - name: Build Streamlit image
        run: docker build -f docker/streamlit/Dockerfile -t bigdata-fraud-streamlit .
      - name: Verify compose config
        run: docker compose config --quiet
```

### tests/conftest.py

```python
"""Shared fixtures for PySpark tests."""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """Create a SparkSession for testing with Delta Lake support."""
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("test-bigdata-fraud")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "4")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )
    yield session
    session.stop()
```

### src/config.py

```python
"""Centralized configuration for the Big Data Fraud pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# === Paths ===
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / os.getenv("DATA_RAW_PATH", "data/raw")
DATA_DELTA = PROJECT_ROOT / os.getenv("DATA_DELTA_PATH", "data/delta")
BRONZE_PATH = str(DATA_DELTA / "bronze" / "transactions")
SILVER_PATH = str(DATA_DELTA / "silver" / "transactions")
GOLD_PATH = str(DATA_DELTA / "gold" / "fraud_metrics")

# === Spark Config ===
SPARK_APP_NAME = "bigdata-fraud-pyspark"
SPARK_DRIVER_MEMORY = os.getenv("SPARK_DRIVER_MEMORY", "8g")
SPARK_EXECUTOR_MEMORY = os.getenv("SPARK_EXECUTOR_MEMORY", "4g")

# === Data Generation ===
DEFAULT_NUM_RECORDS = 100_000_000
FRAUD_RATIO = 0.012  # ~1.2% fraud rate (realistic)
SEED = 42

# === Partitioning ===
PARTITION_COLS_BRONZE = ["year", "month"]
PARTITION_COLS_SILVER = ["year", "month", "is_fraud"]
NUM_BUCKETS = 64
BUCKET_COL = "account_id"
```
