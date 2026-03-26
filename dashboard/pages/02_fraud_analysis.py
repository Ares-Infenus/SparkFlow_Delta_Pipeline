"""Página de análisis de fraude detallado."""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.header("Análisis de Fraude Detallado")

GOLD_PATH = Path("/app/data/gold")


@st.cache_data
def load_gold_data():
    try:
        from deltalake import DeltaTable

        dt = DeltaTable(str(GOLD_PATH / "fraud_metrics"))
        return dt.to_pandas()
    except Exception as e:
        st.warning(f"No se pudieron cargar datos: {e}")
        return pd.DataFrame()


df = load_gold_data()

if df.empty:
    st.info("No hay datos disponibles. Ejecuta el pipeline primero.")
    st.stop()

# === Filtros ===
st.sidebar.subheader("Filtros")
categories = st.sidebar.multiselect(
    "Categoría de Merchant",
    options=sorted(df["merchant_category"].unique()),
    default=sorted(df["merchant_category"].unique()),
)

filtered = df[df["merchant_category"].isin(categories)]

# === Heatmap de fraude ===
st.subheader("Tasa de Fraude por Categoría y Mes")
pivot = filtered.pivot_table(
    values="fraud_rate", index="merchant_category",
    columns="month", aggfunc="mean",
).fillna(0)

fig = px.imshow(
    pivot, title="Heatmap de Tasa de Fraude",
    labels=dict(x="Mes", y="Categoría", color="Tasa"),
    aspect="auto", color_continuous_scale="Reds",
)
st.plotly_chart(fig, use_container_width=True)

# === Top categorías por monto de fraude ===
st.subheader("Top Categorías por Monto de Fraude")
fraud_by_cat = (
    filtered.groupby("merchant_category")
    .agg(fraud_amount=("fraud_amount", "sum"), avg_score=("avg_fraud_score", "mean"))
    .reset_index()
    .sort_values("fraud_amount", ascending=False)
)

fig = px.bar(
    fraud_by_cat, x="merchant_category", y="fraud_amount",
    color="avg_score", title="Monto Total de Fraude por Categoría",
    color_continuous_scale="YlOrRd",
)
st.plotly_chart(fig, use_container_width=True)

# === Tabla detallada ===
st.subheader("Datos Detallados")
st.dataframe(filtered.sort_values("fraud_rate", ascending=False), use_container_width=True)
