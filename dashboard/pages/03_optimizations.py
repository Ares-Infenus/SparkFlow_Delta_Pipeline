"""Página de benchmarks y comparaciones de rendimiento."""

import pandas as pd
import streamlit as st

st.header("Benchmarks y Optimizaciones")

st.markdown(
    """
    Esta página muestra las comparaciones de rendimiento entre el pipeline
    sin optimización (naïve) y con las optimizaciones aplicadas.
    """
)

# === Datos de benchmark (se llenarán tras ejecutar los notebooks) ===
st.subheader("Comparación de Tiempos de Ejecución")

benchmark_data = {
    "Etapa": [
        "Ingesta Bronze",
        "Transformaciones Silver",
        "Feature Engineering",
        "Reglas de Fraude",
        "Escritura Gold",
    ],
    "Sin Optimización (s)": [None, None, None, None, None],
    "Con Optimización (s)": [None, None, None, None, None],
}

df_bench = pd.DataFrame(benchmark_data)

st.info(
    "Los datos de benchmark se llenarán después de ejecutar los notebooks. "
    "Edita esta página o exporta resultados desde los notebooks."
)

st.dataframe(df_bench, use_container_width=True)

# === Optimizaciones aplicadas ===
st.subheader("Optimizaciones Aplicadas")

optimizations = [
    {
        "Técnica": "Adaptive Query Execution (AQE)",
        "Descripción": "Optimización dinámica de planes de ejecución en runtime",
        "Impacto esperado": "10-30% mejora en shuffles",
    },
    {
        "Técnica": "Broadcast Joins",
        "Descripción": "Join de tablas pequeñas sin shuffle distribuido",
        "Impacto esperado": "5-15x más rápido en joins con tablas de referencia",
    },
    {
        "Técnica": "Particionamiento por fecha",
        "Descripción": "Partición por year/month para pruning eficiente",
        "Impacto esperado": "Reduce I/O en consultas filtradas por fecha",
    },
    {
        "Técnica": "Delta Lake Z-Ordering",
        "Descripción": "Co-localización de datos por columnas frecuentes",
        "Impacto esperado": "Mejora data skipping en consultas por account_id",
    },
    {
        "Técnica": "Caching estratégico",
        "Descripción": "Cache de DataFrames reutilizados en múltiples operaciones",
        "Impacto esperado": "Elimina re-cómputo de etapas intermedias",
    },
    {
        "Técnica": "Compresión ZSTD",
        "Descripción": "Compresión de Parquet con zstd (mejor ratio que snappy)",
        "Impacto esperado": "20-30% menos espacio en disco",
    },
]

st.dataframe(pd.DataFrame(optimizations), use_container_width=True)
