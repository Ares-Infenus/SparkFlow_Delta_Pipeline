"""Generador de datos sintéticos de transacciones bancarias a escala."""

import random
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from src.config import DEFAULT_NUM_RECORDS, FRAUD_RATIO, SEED


# === Constantes para generación ===
MERCHANT_CATEGORIES = [
    "grocery", "gas_station", "restaurant", "online_shopping", "electronics",
    "travel", "entertainment", "healthcare", "education", "utilities",
    "clothing", "home_improvement", "automotive", "insurance", "subscription",
]

TRANSACTION_TYPES = ["purchase", "withdrawal", "transfer", "payment", "refund"]

COUNTRIES = ["US", "UK", "CA", "MX", "BR", "DE", "FR", "ES", "JP", "AU", "IN", "CN"]

CHANNELS = ["pos", "online", "atm", "mobile", "branch"]


def generate_transactions(
    spark: SparkSession,
    num_records: int = DEFAULT_NUM_RECORDS,
    num_accounts: int = 500_000,
    num_merchants: int = 50_000,
    start_date: str = "2024-01-01",
    end_date: str = "2024-06-30",
    fraud_ratio: float = FRAUD_RATIO,
    seed: int = SEED,
    num_partitions: int = 200,
) -> "DataFrame":
    """
    Genera un DataFrame de transacciones sintéticas a escala.

    Args:
        spark: SparkSession activa
        num_records: Número total de transacciones a generar
        num_accounts: Número de cuentas únicas
        num_merchants: Número de merchants únicos
        start_date: Fecha de inicio del rango
        end_date: Fecha de fin del rango
        fraud_ratio: Proporción de transacciones fraudulentas
        seed: Semilla para reproducibilidad
        num_partitions: Número de particiones del DataFrame

    Returns:
        DataFrame con transacciones sintéticas
    """
    random.seed(seed)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end_dt - start_dt).days

    # Generar IDs base con distribución realista
    base_df = spark.range(0, num_records, numPartitions=num_partitions)

    transactions_df = (
        base_df
        .withColumn("transaction_id", F.concat(F.lit("TXN_"), F.lpad(F.col("id").cast("string"), 12, "0")))
        .withColumn("account_id", F.concat(F.lit("ACC_"), F.lpad((F.col("id") % num_accounts).cast("string"), 8, "0")))
        .withColumn("merchant_id", F.concat(F.lit("MER_"), F.lpad((F.hash(F.col("id")) % num_merchants).cast("string").substr(2, 8), 8, "0")))
        # Timestamp con distribución uniforme en el rango
        .withColumn(
            "transaction_timestamp",
            F.from_unixtime(
                F.unix_timestamp(F.lit(start_date), "yyyy-MM-dd")
                + (F.abs(F.hash(F.col("id"), F.lit(1))) % (total_days * 86400))
            ),
        )
        .withColumn("transaction_date", F.to_date("transaction_timestamp"))
        .withColumn("year", F.year("transaction_date"))
        .withColumn("month", F.month("transaction_date"))
        .withColumn("hour", F.hour("transaction_timestamp"))
        .withColumn("day_of_week", F.dayofweek("transaction_date"))
        # Categoría y tipo
        .withColumn(
            "merchant_category",
            F.element_at(
                F.array(*[F.lit(c) for c in MERCHANT_CATEGORIES]),
                (F.abs(F.hash(F.col("id"), F.lit(2))) % len(MERCHANT_CATEGORIES)) + 1,
            ),
        )
        .withColumn(
            "transaction_type",
            F.element_at(
                F.array(*[F.lit(t) for t in TRANSACTION_TYPES]),
                (F.abs(F.hash(F.col("id"), F.lit(3))) % len(TRANSACTION_TYPES)) + 1,
            ),
        )
        .withColumn(
            "channel",
            F.element_at(
                F.array(*[F.lit(c) for c in CHANNELS]),
                (F.abs(F.hash(F.col("id"), F.lit(4))) % len(CHANNELS)) + 1,
            ),
        )
        .withColumn(
            "country",
            F.element_at(
                F.array(*[F.lit(c) for c in COUNTRIES]),
                (F.abs(F.hash(F.col("id"), F.lit(5))) % len(COUNTRIES)) + 1,
            ),
        )
        # Monto con distribución log-normal (realista para transacciones)
        .withColumn(
            "amount",
            F.round(
                F.exp(F.abs(F.hash(F.col("id"), F.lit(6)).cast("double") / 2147483647.0) * 4 + 1),
                2,
            ),
        )
        # Fraude: etiqueta basada en ratio
        .withColumn(
            "is_fraud",
            F.when(
                (F.abs(F.hash(F.col("id"), F.lit(7))) % 1000) < int(fraud_ratio * 1000),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        # Ajustar montos de fraude (tienden a ser más altos)
        .withColumn(
            "amount",
            F.when(F.col("is_fraud") == 1, F.col("amount") * F.lit(3.5))
            .otherwise(F.col("amount")),
        )
        # Score de riesgo simulado
        .withColumn(
            "risk_score",
            F.round(
                F.when(F.col("is_fraud") == 1, F.abs(F.hash(F.col("id"), F.lit(8)).cast("double") / 2147483647.0) * 0.3 + 0.7)
                .otherwise(F.abs(F.hash(F.col("id"), F.lit(9)).cast("double") / 2147483647.0) * 0.6 + 0.05),
                4,
            ),
        )
        .drop("id")
    )

    return transactions_df


def generate_reference_tables(spark: SparkSession, num_merchants: int = 50_000):
    """Genera tablas de referencia para joins (merchants, countries)."""
    # Tabla de merchants
    merchants_df = (
        spark.range(0, num_merchants)
        .withColumn("merchant_id", F.concat(F.lit("MER_"), F.lpad(F.col("id").cast("string"), 8, "0")))
        .withColumn(
            "merchant_name",
            F.concat(F.lit("Merchant_"), F.col("id").cast("string")),
        )
        .withColumn(
            "merchant_category",
            F.element_at(
                F.array(*[F.lit(c) for c in MERCHANT_CATEGORIES]),
                (F.col("id") % len(MERCHANT_CATEGORIES)).cast("int") + 1,
            ),
        )
        .withColumn(
            "merchant_country",
            F.element_at(
                F.array(*[F.lit(c) for c in COUNTRIES]),
                (F.col("id") % len(COUNTRIES)).cast("int") + 1,
            ),
        )
        .withColumn(
            "merchant_risk_level",
            F.when(F.col("id") % 20 == 0, F.lit("high"))
            .when(F.col("id") % 5 == 0, F.lit("medium"))
            .otherwise(F.lit("low")),
        )
        .drop("id")
    )

    return merchants_df
