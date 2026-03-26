"""Utilidades para logging, benchmarking y helpers comunes."""

import logging
import time
from contextlib import contextmanager
from functools import wraps

from pyspark.sql import SparkSession

from src.config import SPARK_APP_NAME, SPARK_DRIVER_MEMORY, SPARK_EXECUTOR_MEMORY

logger = logging.getLogger(__name__)


def get_spark_session(app_name=None):
    """Crea o retorna una SparkSession configurada con Delta Lake."""
    from delta import configure_spark_with_delta_pip

    builder = (
        SparkSession.builder.appName(app_name or SPARK_APP_NAME)
        .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
        .config("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .config("spark.sql.parquet.compression.codec", "zstd")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


@contextmanager
def benchmark(description="Operation"):
    """Context manager para medir el tiempo de ejecución de un bloque."""
    start = time.perf_counter()
    logger.info("⏱ Iniciando: %s", description)
    yield
    elapsed = time.perf_counter() - start
    logger.info("✅ %s completado en %.2f segundos", description, elapsed)


def timed(func):
    """Decorador para medir el tiempo de ejecución de una función."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info("⏱ %s ejecutado en %.2f segundos", func.__name__, elapsed)
        return result

    return wrapper


def setup_logging(level=logging.INFO):
    """Configura logging para el pipeline."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def count_nulls(df):
    """Retorna un diccionario con el conteo de nulos por columna."""
    from pyspark.sql import functions as F

    null_counts = {}
    for col_name in df.columns:
        null_count = df.where(F.col(col_name).isNull()).count()
        null_counts[col_name] = null_count
    return null_counts


def show_table_info(df, table_name="DataFrame"):
    """Muestra información básica de un DataFrame."""
    print(f"\n{'='*60}")
    print(f"📊 {table_name}")
    print(f"{'='*60}")
    print(f"  Filas:    {df.count():,}")
    print(f"  Columnas: {len(df.columns)}")
    print(f"  Particiones: {df.rdd.getNumPartitions()}")
    print(f"{'='*60}\n")
    df.printSchema()
