"""CLI para generar datos sintéticos de transacciones a escala."""

import argparse
import sys
import time

sys.path.insert(0, ".")

from src.config import DEFAULT_NUM_RECORDS, DATA_RAW
from src.data_generator import generate_reference_tables, generate_transactions
from src.utils import get_spark_session, setup_logging


def main():
    parser = argparse.ArgumentParser(description="Genera datos sintéticos de transacciones")
    parser.add_argument(
        "--num-records", type=int, default=DEFAULT_NUM_RECORDS,
        help=f"Número de transacciones a generar (default: {DEFAULT_NUM_RECORDS:,})",
    )
    parser.add_argument(
        "--output-path", type=str, default=str(DATA_RAW / "transactions"),
        help="Ruta de salida para los datos generados",
    )
    parser.add_argument(
        "--format", type=str, default="parquet", choices=["parquet", "csv"],
        help="Formato de salida (default: parquet)",
    )
    parser.add_argument(
        "--num-partitions", type=int, default=200,
        help="Número de particiones del DataFrame (default: 200)",
    )
    args = parser.parse_args()

    setup_logging()
    spark = get_spark_session("data-generator")

    print(f"\n{'='*60}")
    print(f"Generando {args.num_records:,} transacciones...")
    print(f"Salida: {args.output_path}")
    print(f"Formato: {args.format}")
    print(f"{'='*60}\n")

    start = time.perf_counter()

    # Generar transacciones
    df = generate_transactions(
        spark, num_records=args.num_records, num_partitions=args.num_partitions,
    )

    # Escribir datos
    if args.format == "parquet":
        df.write.mode("overwrite").parquet(args.output_path)
    else:
        df.write.mode("overwrite").option("header", "true").csv(args.output_path)

    elapsed = time.perf_counter() - start

    print(f"\nGeneración completada en {elapsed:.2f} segundos")
    print(f"Registros: {args.num_records:,}")
    print(f"Ruta: {args.output_path}")

    # Generar tablas de referencia
    print("\nGenerando tablas de referencia...")
    merchants_df = generate_reference_tables(spark)
    merchants_path = str(DATA_RAW / "merchants")
    merchants_df.write.mode("overwrite").parquet(merchants_path)
    print(f"Merchants: {merchants_path}")

    spark.stop()


if __name__ == "__main__":
    main()
