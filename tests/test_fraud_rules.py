"""Tests para reglas de detección de fraude."""

from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from src.fraud_rules import (
    calculate_fraud_score,
    flag_high_amount,
    flag_high_zscore,
    flag_night_transaction,
)


def _create_fraud_test_df(spark, data=None):
    """Helper para crear un DataFrame con columnas necesarias para reglas de fraude."""
    schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("account_id", StringType(), False),
        StructField("amount", DoubleType(), True),
        StructField("amount_zscore", DoubleType(), True),
        StructField("is_fraud", IntegerType(), True),
        StructField("is_night", IntegerType(), True),
        StructField("merchant_risk_level", StringType(), True),
        StructField("transaction_date", StringType(), True),
    ])

    if data is None:
        data = [
            ("TXN_001", "ACC_001", 150.50, 0.5, 0, 0, "low", "2024-03-15"),
            ("TXN_002", "ACC_001", 8500.00, 4.2, 1, 1, "high", "2024-03-15"),
            ("TXN_003", "ACC_002", 45.99, -0.3, 0, 0, "low", "2024-03-16"),
            ("TXN_004", "ACC_002", 6000.00, 3.5, 0, 1, "medium", "2024-03-16"),
        ]

    return spark.createDataFrame(data, schema)


class TestFlagHighAmount:
    def test_flags_above_threshold(self, spark):
        df = _create_fraud_test_df(spark)
        result = flag_high_amount(df, threshold=5000.0)
        flagged = result.where(F.col("flag_high_amount") == 1).count()
        assert flagged == 2  # TXN_002 (8500) y TXN_004 (6000)

    def test_does_not_flag_below_threshold(self, spark):
        df = _create_fraud_test_df(spark)
        result = flag_high_amount(df, threshold=5000.0)
        not_flagged = result.where(F.col("flag_high_amount") == 0).count()
        assert not_flagged == 2

    def test_custom_threshold(self, spark):
        df = _create_fraud_test_df(spark)
        result = flag_high_amount(df, threshold=100.0)
        flagged = result.where(F.col("flag_high_amount") == 1).count()
        assert flagged == 3  # 150.50, 8500, 6000


class TestFlagHighZscore:
    def test_flags_high_zscore(self, spark):
        df = _create_fraud_test_df(spark)
        result = flag_high_zscore(df, zscore_threshold=3.0)
        flagged = result.where(F.col("flag_high_zscore") == 1).count()
        assert flagged == 2  # TXN_002 (4.2) y TXN_004 (3.5)

    def test_does_not_flag_normal_zscore(self, spark):
        df = _create_fraud_test_df(spark)
        result = flag_high_zscore(df, zscore_threshold=3.0)
        not_flagged = result.where(F.col("flag_high_zscore") == 0).count()
        assert not_flagged == 2


class TestFlagNightTransaction:
    def test_flags_night_transactions(self, spark):
        df = _create_fraud_test_df(spark)
        result = flag_night_transaction(df)
        flagged = result.where(F.col("flag_night_txn") == 1).count()
        assert flagged == 2  # TXN_002 y TXN_004


class TestCalculateFraudScore:
    def test_score_calculation(self, spark):
        data = [
            ("TXN_001", "ACC_001", 100.0, 0.5, 0, 0, "low", "2024-03-15"),
        ]
        df = _create_fraud_test_df(spark, data)
        df = (
            df
            .withColumn("flag_high_amount", F.lit(0))
            .withColumn("flag_high_zscore", F.lit(0))
            .withColumn("flag_high_frequency", F.lit(0))
            .withColumn("flag_night_txn", F.lit(0))
            .withColumn("flag_high_risk_merchant", F.lit(0))
        )
        result = calculate_fraud_score(df)
        score = result.select("fraud_score").collect()[0]["fraud_score"]
        assert score == 0.0

    def test_max_score(self, spark):
        data = [
            ("TXN_001", "ACC_001", 100.0, 0.5, 0, 0, "low", "2024-03-15"),
        ]
        df = _create_fraud_test_df(spark, data)
        df = (
            df
            .withColumn("flag_high_amount", F.lit(1))
            .withColumn("flag_high_zscore", F.lit(1))
            .withColumn("flag_high_frequency", F.lit(1))
            .withColumn("flag_night_txn", F.lit(1))
            .withColumn("flag_high_risk_merchant", F.lit(1))
        )
        result = calculate_fraud_score(df)
        score = result.select("fraud_score").collect()[0]["fraud_score"]
        assert score == 1.0
