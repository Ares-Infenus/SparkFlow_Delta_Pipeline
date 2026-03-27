"""Tests para funciones de transformación."""

from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from src.transformations import (
    add_time_features,
    build_silver_layer,
    cast_types,
    deduplicate_transactions,
    filter_invalid_transactions,
)


def _create_sample_df(spark, data=None):
    """Helper para crear un DataFrame de prueba."""
    schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("account_id", StringType(), False),
        StructField("merchant_id", StringType(), True),
        StructField("amount", StringType(), True),
        StructField("is_fraud", StringType(), True),
        StructField("risk_score", StringType(), True),
        StructField("transaction_timestamp", StringType(), True),
        StructField("transaction_date", StringType(), True),
        StructField("merchant_category", StringType(), True),
    ])

    if data is None:
        data = [
            ("TXN_001", "ACC_001", "MER_001", "150.50", "0", "0.12", "2024-03-15 10:30:00", "2024-03-15", "grocery"),
            ("TXN_002", "ACC_001", "MER_002", "3200.00", "1", "0.85", "2024-03-15 23:45:00", "2024-03-15", "electronics"),
            ("TXN_003", "ACC_002", "MER_001", "45.99", "0", "0.05", "2024-03-16 14:20:00", "2024-03-16", "restaurant"),
        ]

    return spark.createDataFrame(data, schema)


class TestDeduplication:
    def test_removes_exact_duplicates(self, spark):
        data = [
            ("TXN_001", "ACC_001", "MER_001", "100.0", "0", "0.1", "2024-01-01 10:00:00", "2024-01-01", "grocery"),
            ("TXN_001", "ACC_001", "MER_001", "100.0", "0", "0.1", "2024-01-01 10:00:00", "2024-01-01", "grocery"),
            ("TXN_002", "ACC_002", "MER_002", "200.0", "0", "0.2", "2024-01-02 11:00:00", "2024-01-02", "electronics"),
        ]
        df = _create_sample_df(spark, data)
        result = deduplicate_transactions(df)
        assert result.count() == 2

    def test_keeps_unique_transactions(self, spark):
        df = _create_sample_df(spark)
        result = deduplicate_transactions(df)
        assert result.count() == 3


class TestCastTypes:
    def test_amount_is_double(self, spark):
        df = _create_sample_df(spark)
        result = cast_types(df)
        assert result.schema["amount"].dataType == DoubleType()

    def test_is_fraud_is_integer(self, spark):
        df = _create_sample_df(spark)
        result = cast_types(df)
        assert result.schema["is_fraud"].dataType == IntegerType()


class TestFilterInvalidTransactions:
    def test_removes_negative_amounts(self, spark):
        data = [
            ("TXN_001", "ACC_001", "MER_001", "-50.0", "0", "0.1", "2024-01-01 10:00:00", "2024-01-01", "grocery"),
            ("TXN_002", "ACC_001", "MER_001", "100.0", "0", "0.1", "2024-01-01 10:00:00", "2024-01-01", "grocery"),
        ]
        df = _create_sample_df(spark, data)
        df = cast_types(df)
        result = filter_invalid_transactions(df)
        assert result.count() == 1

    def test_removes_extremely_high_amounts(self, spark):
        data = [
            ("TXN_001", "ACC_001", "MER_001", "999999999.0", "0", "0.1", "2024-01-01 10:00:00", "2024-01-01", "grocery"),
            ("TXN_002", "ACC_001", "MER_001", "100.0", "0", "0.1", "2024-01-01 10:00:00", "2024-01-01", "grocery"),
        ]
        df = _create_sample_df(spark, data)
        df = cast_types(df)
        result = filter_invalid_transactions(df)
        assert result.count() == 1


class TestAddTimeFeatures:
    def test_adds_weekend_flag(self, spark):
        df = _create_sample_df(spark)
        df = cast_types(df)
        result = add_time_features(df)
        assert "is_weekend" in result.columns

    def test_adds_night_flag(self, spark):
        df = _create_sample_df(spark)
        df = cast_types(df)
        result = add_time_features(df)
        assert "is_night" in result.columns
        # TXN_002 es a las 23:45, debería ser night
        night_txn = result.where(F.col("transaction_id") == "TXN_002").select("is_night").collect()
        assert night_txn[0]["is_night"] == 1


class TestBuildSilverLayer:
    def test_full_pipeline(self, spark):
        df = _create_sample_df(spark)
        result = build_silver_layer(df)
        assert result.count() == 3
        assert "is_weekend" in result.columns
        assert "is_night" in result.columns
