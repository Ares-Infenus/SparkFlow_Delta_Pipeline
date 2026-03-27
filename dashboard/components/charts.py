"""Funciones de Plotly reutilizables para el dashboard."""

import plotly.express as px
import plotly.graph_objects as go


def create_kpi_indicator(value, title, reference=None, prefix="", suffix=""):
    """Crea un indicador KPI con Plotly."""
    fig = go.Figure(
        go.Indicator(
            mode="number+delta" if reference else "number",
            value=value,
            title={"text": title},
            delta={"reference": reference} if reference else None,
            number={"prefix": prefix, "suffix": suffix},
        )
    )
    fig.update_layout(height=200, margin=dict(t=50, b=0, l=20, r=20))
    return fig


def create_time_series(df, x, y, title, color=None, markers=True):
    """Crea un gráfico de serie temporal."""
    fig = px.line(df, x=x, y=y, color=color, title=title, markers=markers)
    fig.update_layout(xaxis_title="", yaxis_title=y, hovermode="x unified")
    return fig


def create_category_bar(df, x, y, title, color=None, orientation="v"):
    """Crea un gráfico de barras por categoría."""
    fig = px.bar(df, x=x, y=y, color=color, title=title, orientation=orientation)
    fig.update_layout(xaxis_title="", yaxis_title=y if orientation == "v" else x)
    return fig


def create_heatmap(df_pivot, title, color_scale="Reds"):
    """Crea un heatmap desde un DataFrame pivotado."""
    fig = px.imshow(
        df_pivot,
        title=title,
        aspect="auto",
        color_continuous_scale=color_scale,
    )
    return fig


def create_distribution(df, x, title, nbins=50, color=None):
    """Crea un histograma de distribución."""
    fig = px.histogram(df, x=x, title=title, nbins=nbins, color=color)
    fig.update_layout(xaxis_title=x, yaxis_title="Frecuencia")
    return fig
