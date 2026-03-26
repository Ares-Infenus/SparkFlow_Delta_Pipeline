"""Tests para el generador de datos sintéticos."""

from src.data_generator import generate_reference_tables, generate_transactions


class TestGenerateTransactions:
    def test_generates_correct_count(self, spark):
        df = generate_transactions(spark, num_records=1000, num_partitions=2)
        assert df.count() == 1000

    def test_has_required_columns(self, spark):
        df = generate_transactions(spark, num_records=100, num_partitions=2)
        required_cols = [
            "transaction_id", "account_id", "merchant_id", "amount",
            "is_fraud", "risk_score", "transaction_timestamp",
            "merchant_category", "transaction_type", "channel", "country",
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_fraud_ratio_approximate(self, spark):
        df = generate_transactions(
            spark, num_records=10000, fraud_ratio=0.012, num_partitions=2,
        )
        fraud_count = df.where(df.is_fraud == 1).count()
        fraud_rate = fraud_count / 10000
        # Permitir margen amplio por naturaleza hash-based
        assert 0.001 < fraud_rate < 0.1

    def test_amounts_are_positive(self, spark):
        df = generate_transactions(spark, num_records=1000, num_partitions=2)
        negative_count = df.where(df.amount <= 0).count()
        assert negative_count == 0

    def test_deterministic_with_seed(self, spark):
        df1 = generate_transactions(spark, num_records=100, seed=42, num_partitions=2)
        df2 = generate_transactions(spark, num_records=100, seed=42, num_partitions=2)
        count1 = df1.where(df1.is_fraud == 1).count()
        count2 = df2.where(df2.is_fraud == 1).count()
        assert count1 == count2


class TestGenerateReferenceTables:
    def test_merchant_table_count(self, spark):
        df = generate_reference_tables(spark, num_merchants=100)
        assert df.count() == 100

    def test_merchant_table_columns(self, spark):
        df = generate_reference_tables(spark, num_merchants=100)
        assert "merchant_id" in df.columns
        assert "merchant_risk_level" in df.columns
        assert "merchant_category" in df.columns
