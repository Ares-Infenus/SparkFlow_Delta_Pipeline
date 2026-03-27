"""Página de resumen general de transacciones."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.header("Overview de Transacciones")

GOLD_PATH = Path("/app/data/gold")


@st.cache_data
def load_gold_data():
    """Carga datos de la capa Gold (Delta -> Parquet vía deltalake)."""
    try:
        from deltalake import DeltaTable

        dt = DeltaTable(str(GOLD_PATH / "fraud_metrics"))
        return dt.to_pandas()
    except Exception as e:
        st.warning(f"No se pudieron cargar datos Gold: {e}")
        return pd.DataFrame()


df = load_gold_data()

if df.empty:
    st.info(
        "No hay datos disponibles. Ejecuta el pipeline de Spark primero "
        "(Notebooks 01-03) para generar las tablas Gold."
    )
    st.stop()

# === KPIs ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Transacciones", f"{df['total_transactions'].sum():,.0f}")
with col2:
    st.metric("Total Fraudes", f"{df['total_fraud'].sum():,.0f}")
with col3:
    fraud_rate = df["total_fraud"].sum() / df["total_transactions"].sum() * 100
    st.metric("Tasa de Fraude", f"{fraud_rate:.2f}%")
with col4:
    st.metric("Monto Fraude", f"${df['fraud_amount'].sum():,.2f}")

st.markdown("---")

# === Gráficos ===
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Transacciones por Categoría")
    cat_data = (
        df.groupby("merchant_category")
        .agg(
            total=("total_transactions", "sum"),
        )
        .reset_index()
        .sort_values("total", ascending=True)
    )

    fig = px.bar(
        cat_data,
        x="total",
        y="merchant_category",
        orientation="h",
        title="Volumen por Categoría",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Fraude por Mes")
    month_data = (
        df.groupby(["year", "month"])
        .agg(
            fraud=("total_fraud", "sum"),
            total=("total_transactions", "sum"),
        )
        .reset_index()
    )
    month_data["period"] = (
        month_data["year"].astype(str) + "-" + month_data["month"].astype(str).str.zfill(2)
    )

    fig = px.line(
        month_data,
        x="period",
        y="fraud",
        title="Fraudes Detectados por Mes",
        markers=True,
    )
    st.plotly_chart(fig, use_container_width=True)
