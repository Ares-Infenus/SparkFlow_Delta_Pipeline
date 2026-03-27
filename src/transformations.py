"""Funciones de transformación reutilizables para el pipeline."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def deduplicate_transactions(df: DataFrame) -> DataFrame:
    """Elimina transacciones duplicadas basándose en transaction_id."""
    return df.dropDuplicates(["transaction_id"])


def cast_types(df: DataFrame) -> DataFrame:
    """Asegura tipos de datos correctos para todas las columnas."""
    return (
        df.withColumn("amount", F.col("amount").cast("double"))
        .withColumn("is_fraud", F.col("is_fraud").cast("integer"))
        .withColumn("risk_score", F.col("risk_score").cast("double"))
        .withColumn("transaction_timestamp", F.to_timestamp("transaction_timestamp"))
        .withColumn("transaction_date", F.to_date("transaction_date"))
    )


def filter_invalid_transactions(df: DataFrame) -> DataFrame:
    """Filtra transacciones con datos inválidos."""
    return (
        df.where(F.col("amount") > 0)
        .where(F.col("amount") < 1_000_000)  # Cap en 1M
        .where(F.col("transaction_id").isNotNull())
        .where(F.col("account_id").isNotNull())
    )


def add_time_features(df: DataFrame) -> DataFrame:
    """Agrega features temporales derivadas."""
    return (
        df.withColumn("hour", F.hour("transaction_timestamp"))
        .withColumn("day_of_week", F.dayofweek("transaction_date"))
        .withColumn("is_weekend", F.when(F.col("day_of_week").isin(1, 7), 1).otherwise(0))
        .withColumn(
            "is_night", F.when((F.col("hour") >= 22) | (F.col("hour") <= 5), 1).otherwise(0)
        )
    )


def add_rolling_account_stats(df: DataFrame, window_days: int = 7) -> DataFrame:
    """
    Calcula estadísticas rolling por cuenta usando window functions.

    Features generadas:
    - rolling_avg_amount: Promedio de monto en la ventana
    - rolling_count: Número de transacciones en la ventana
    - rolling_max_amount: Monto máximo en la ventana
    - rolling_std_amount: Desviación estándar en la ventana
    """
    seconds_in_window = window_days * 86400

    window_spec = (
        Window.partitionBy("account_id")
        .orderBy(F.col("transaction_timestamp").cast("long"))
        .rangeBetween(-seconds_in_window, 0)
    )

    return (
        df.withColumn("rolling_avg_amount", F.round(F.avg("amount").over(window_spec), 2))
        .withColumn("rolling_count", F.count("*").over(window_spec))
        .withColumn("rolling_max_amount", F.max("amount").over(window_spec))
        .withColumn("rolling_std_amount", F.round(F.stddev("amount").over(window_spec), 2))
    )


def add_amount_zscore(df: DataFrame) -> DataFrame:
    """Calcula z-score del monto respecto al promedio de la cuenta."""
    account_stats = df.groupBy("account_id").agg(
        F.avg("amount").alias("account_avg_amount"),
        F.stddev("amount").alias("account_std_amount"),
    )

    return (
        df.join(account_stats, on="account_id", how="left")
        .withColumn(
            "amount_zscore",
            F.when(
                F.col("account_std_amount") > 0,
                F.round(
                    (F.col("amount") - F.col("account_avg_amount")) / F.col("account_std_amount"), 4
                ),
            ).otherwise(F.lit(0.0)),
        )
        .drop("account_avg_amount", "account_std_amount")
    )


def enrich_with_merchants(
    transactions_df: DataFrame,
    merchants_df: DataFrame,
) -> DataFrame:
    """Enriquece transacciones con información de merchants via broadcast join."""
    # Eliminar columnas duplicadas del merchants_df antes del join
    cols_to_drop = set(transactions_df.columns) & set(merchants_df.columns) - {"merchant_id"}
    merchants_clean = merchants_df.drop(*cols_to_drop)
    return transactions_df.join(
        F.broadcast(merchants_clean),
        on="merchant_id",
        how="left",
    )


def build_silver_layer(df: DataFrame) -> DataFrame:
    """Aplica todas las transformaciones para la capa Silver."""
    return (
        df.transform(deduplicate_transactions)
        .transform(cast_types)
        .transform(filter_invalid_transactions)
        .transform(add_time_features)
    )
