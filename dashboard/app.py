"""Streamlit dashboard principal para análisis de fraude."""

import streamlit as st

st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Fraud Detection Dashboard")
st.markdown("---")

st.markdown(
    """
    ### Big Data Analytics Pipeline
    Pipeline de detección de fraude en transacciones bancarias procesando 100M+ registros
    con Apache Spark y Delta Lake.

    **Navegación:**
    - **Overview**: Resumen general de transacciones y métricas clave
    - **Fraud Analysis**: Análisis detallado de patrones de fraude
    - **Optimizations**: Benchmarks y comparaciones de rendimiento

    ---
    *Selecciona una página en el menú lateral para explorar los datos.*
    """
)
