"""Reglas de detección de fraude basadas en umbrales y z-scores."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def flag_high_amount(df: DataFrame, threshold: float = 5000.0) -> DataFrame:
    """Marca transacciones con montos inusualmente altos."""
    return df.withColumn(
        "flag_high_amount",
        F.when(F.col("amount") > threshold, 1).otherwise(0),
    )


def flag_high_zscore(df: DataFrame, zscore_threshold: float = 3.0) -> DataFrame:
    """Marca transacciones con z-score alto (anomalía estadística)."""
    return df.withColumn(
        "flag_high_zscore",
        F.when(F.abs(F.col("amount_zscore")) > zscore_threshold, 1).otherwise(0),
    )


def flag_high_frequency(df: DataFrame, max_daily_txns: int = 20) -> DataFrame:
    """Marca cuentas con frecuencia de transacciones inusualmente alta."""
    daily_counts = df.groupBy("account_id", "transaction_date").agg(
        F.count("*").alias("daily_txn_count")
    )

    high_freq_accounts = (
        daily_counts.where(F.col("daily_txn_count") > max_daily_txns)
        .select("account_id", "transaction_date")
        .withColumn("flag_high_frequency", F.lit(1))
    )

    return df.join(
        high_freq_accounts,
        on=["account_id", "transaction_date"],
        how="left",
    ).fillna(0, subset=["flag_high_frequency"])


def flag_night_transaction(df: DataFrame) -> DataFrame:
    """Marca transacciones realizadas en horario nocturno (22:00 - 05:00)."""
    return df.withColumn(
        "flag_night_txn",
        F.when(F.col("is_night") == 1, 1).otherwise(0),
    )


def flag_high_risk_merchant(df: DataFrame) -> DataFrame:
    """Marca transacciones con merchants de alto riesgo."""
    return df.withColumn(
        "flag_high_risk_merchant",
        F.when(F.col("merchant_risk_level") == "high", 1).otherwise(0),
    )


def calculate_fraud_score(df: DataFrame) -> DataFrame:
    """
    Calcula un score de fraude combinado basado en las flags individuales.

    Pesos:
    - High amount: 0.25
    - High z-score: 0.30
    - High frequency: 0.15
    - Night transaction: 0.10
    - High risk merchant: 0.20
    """
    return df.withColumn(
        "fraud_score",
        F.round(
            F.col("flag_high_amount") * 0.25
            + F.col("flag_high_zscore") * 0.30
            + F.col("flag_high_frequency") * 0.15
            + F.col("flag_night_txn") * 0.10
            + F.col("flag_high_risk_merchant") * 0.20,
            4,
        ),
    )


def apply_all_fraud_rules(
    df: DataFrame,
    amount_threshold: float = 5000.0,
    zscore_threshold: float = 3.0,
    max_daily_txns: int = 20,
) -> DataFrame:
    """Aplica todas las reglas de fraude y calcula el score combinado."""
    return (
        df.transform(lambda d: flag_high_amount(d, amount_threshold))
        .transform(lambda d: flag_high_zscore(d, zscore_threshold))
        .transform(lambda d: flag_high_frequency(d, max_daily_txns))
        .transform(flag_night_transaction)
        .transform(flag_high_risk_merchant)
        .transform(calculate_fraud_score)
    )


def build_fraud_summary(df: DataFrame) -> DataFrame:
    """Genera resumen de fraude por merchant_category y mes."""
    return (
        df.groupBy("merchant_category", "year", "month")
        .agg(
            F.count("*").alias("total_transactions"),
            F.sum("is_fraud").alias("total_fraud"),
            F.round(F.avg("amount"), 2).alias("avg_amount"),
            F.round(F.avg("fraud_score"), 4).alias("avg_fraud_score"),
            F.sum(F.when(F.col("fraud_score") > 0.5, 1).otherwise(0)).alias("high_risk_count"),
            F.round(F.sum(F.when(F.col("is_fraud") == 1, F.col("amount")).otherwise(0)), 2).alias(
                "fraud_amount"
            ),
        )
        .withColumn(
            "fraud_rate",
            F.round(F.col("total_fraud") / F.col("total_transactions"), 6),
        )
        .orderBy("year", "month", "merchant_category")
    )
