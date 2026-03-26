"""Script para generar las imágenes del README programáticamente."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_data_flow():
    """Genera el diagrama de flujo de datos Bronze → Silver → Gold → Dashboard."""
    fig = go.Figure()

    # Configuración del canvas
    fig.update_layout(
        width=1200,
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(range=[0, 10], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 5], showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=60, b=20),
        title=dict(
            text="Flujo de Datos — De la Transacción al Dashboard",
            font=dict(size=22, color="#1a1a2e"),
            x=0.5,
        ),
        font=dict(family="Arial, sans-serif"),
    )

    # === Bloques principales ===
    blocks = [
        {"x": 1.2, "y": 2.8, "w": 1.6, "h": 2.0, "color": "#E8EAF6", "border": "#3F51B5",
         "icon": "📥", "title": "Generación", "sub": "100M+ transacciones\nsintéticas con\nFaker + PySpark"},
        {"x": 3.4, "y": 2.8, "w": 1.6, "h": 2.0, "color": "#FFF3E0", "border": "#CD7F32",
         "icon": "🥉", "title": "Bronze", "sub": "Datos crudos\nPartición por fecha\nDelta Lake + ZSTD"},
        {"x": 5.6, "y": 2.8, "w": 1.6, "h": 2.0, "color": "#F5F5F5", "border": "#9E9E9E",
         "icon": "🥈", "title": "Silver", "sub": "Dedup + limpieza\nWindow functions\nBroadcast joins"},
        {"x": 7.8, "y": 2.8, "w": 1.6, "h": 2.0, "color": "#FFFDE7", "border": "#FFC107",
         "icon": "🥇", "title": "Gold", "sub": "5 reglas de fraude\nScore combinado\nMétricas agregadas"},
    ]

    for b in blocks:
        # Rectángulo
        fig.add_shape(
            type="rect",
            x0=b["x"] - b["w"] / 2, y0=b["y"] - b["h"] / 2,
            x1=b["x"] + b["w"] / 2, y1=b["y"] + b["h"] / 2,
            fillcolor=b["color"],
            line=dict(color=b["border"], width=2.5),
            layer="below",
        )
        # Icono
        fig.add_annotation(
            x=b["x"], y=b["y"] + 0.6, text=b["icon"],
            font=dict(size=28), showarrow=False,
        )
        # Título
        fig.add_annotation(
            x=b["x"], y=b["y"] + 0.15, text=f"<b>{b['title']}</b>",
            font=dict(size=15, color="#1a1a2e"), showarrow=False,
        )
        # Subtítulo
        fig.add_annotation(
            x=b["x"], y=b["y"] - 0.45, text=b["sub"],
            font=dict(size=10, color="#555"), showarrow=False,
            align="center",
        )

    # === Bloque Dashboard (más ancho, abajo a la derecha) ===
    fig.add_shape(
        type="rect",
        x0=6.8, y0=0.1, x1=9.2, y1=1.3,
        fillcolor="#FFEBEE", line=dict(color="#FF4B4B", width=2.5),
        layer="below",
    )
    fig.add_annotation(x=8.0, y=0.95, text="📊", font=dict(size=28), showarrow=False)
    fig.add_annotation(
        x=8.0, y=0.55, text="<b>Streamlit Dashboard</b>",
        font=dict(size=14, color="#1a1a2e"), showarrow=False,
    )
    fig.add_annotation(
        x=8.0, y=0.25, text="localhost:8501",
        font=dict(size=10, color="#FF4B4B"), showarrow=False,
    )

    # === Flechas entre bloques ===
    arrows = [
        {"x0": 2.0, "x1": 2.6, "y": 2.8, "label": ""},
        {"x0": 4.2, "x1": 4.8, "y": 2.8, "label": ""},
        {"x0": 6.4, "x1": 7.0, "y": 2.8, "label": ""},
    ]

    for a in arrows:
        fig.add_annotation(
            x=a["x1"], y=a["y"],
            ax=a["x0"], ay=a["y"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=3, arrowsize=1.5, arrowwidth=2.5,
            arrowcolor="#3F51B5",
        )

    # Flecha Gold → Dashboard (curva hacia abajo)
    fig.add_annotation(
        x=8.0, y=1.3,
        ax=7.8, ay=1.8,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=3, arrowsize=1.5, arrowwidth=2.5,
        arrowcolor="#FF4B4B",
    )

    # === Etiquetas de proceso entre flechas ===
    labels = [
        {"x": 2.3, "y": 3.45, "text": "Delta Lake"},
        {"x": 4.5, "y": 3.45, "text": "Dedup + Cast\n+ Features"},
        {"x": 6.7, "y": 3.45, "text": "Fraud Rules\n+ Aggregate"},
    ]

    for lbl in labels:
        fig.add_annotation(
            x=lbl["x"], y=lbl["y"], text=lbl["text"],
            font=dict(size=9, color="#666"),
            showarrow=False, align="center",
            bgcolor="rgba(255,255,255,0.8)",
        )

    path = OUTPUT_DIR / "data_flow.png"
    fig.write_image(str(path), scale=2)
    print(f"✅ Generado: {path}")


def generate_benchmarks():
    """Genera el gráfico comparativo de rendimiento."""
    etapas = [
        "Ingesta\nBronze",
        "Transformaciones\nSilver",
        "Feature\nEngineering",
        "Reglas de\nFraude",
        "Escritura\nGold",
    ]
    sin_opt = [5.11, 3.95, 0.23, 0.14, 4.41]
    con_opt = [2.82, 3.95, 0.23, 0.14, 4.41]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Sin Optimización",
        x=etapas, y=sin_opt,
        marker_color="#BDBDBD",
        marker_line=dict(color="#757575", width=1),
        text=[f"{v:.2f}s" for v in sin_opt],
        textposition="outside",
        textfont=dict(size=12, color="#555"),
    ))

    fig.add_trace(go.Bar(
        name="Con Optimización",
        x=etapas, y=con_opt,
        marker_color="#4CAF50",
        marker_line=dict(color="#2E7D32", width=1),
        text=[f"{v:.2f}s" for v in con_opt],
        textposition="outside",
        textfont=dict(size=12, color="#2E7D32"),
    ))

    # Anotación de mejora en Ingesta Bronze
    fig.add_annotation(
        x="Ingesta\nBronze", y=5.5,
        text="<b>⚡ 45% más rápido</b>",
        font=dict(size=13, color="#D32F2F"),
        showarrow=True, arrowhead=2,
        ax=50, ay=-30,
        bgcolor="rgba(255,235,238,0.9)",
        bordercolor="#D32F2F",
        borderwidth=1,
    )

    fig.update_layout(
        title=dict(
            text="Benchmark: Tiempo de Ejecución por Etapa (100K registros)",
            font=dict(size=18, color="#1a1a2e"),
            x=0.5,
        ),
        yaxis=dict(
            title="Tiempo (segundos)",
            gridcolor="#E0E0E0",
            range=[0, 7],
        ),
        xaxis=dict(title=""),
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        width=1000,
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(size=13),
        ),
        margin=dict(l=60, r=40, t=100, b=80),
        font=dict(family="Arial, sans-serif"),
    )

    path = OUTPUT_DIR / "benchmarks.png"
    fig.write_image(str(path), scale=2)
    print(f"✅ Generado: {path}")


def generate_fraud_rules_diagram():
    """Genera diagrama visual de las 5 reglas de fraude y cómo se combinan."""
    fig = go.Figure()

    fig.update_layout(
        width=1100,
        height=550,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(range=[0, 11], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 6], showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=10, r=10, t=60, b=10),
        title=dict(
            text="Sistema de Detección de Fraude — 5 Reglas Combinadas",
            font=dict(size=20, color="#1a1a2e"),
            x=0.5,
        ),
        font=dict(family="Arial, sans-serif"),
    )

    # Reglas (lado izquierdo)
    rules = [
        {"y": 5.0, "icon": "💰", "name": "Monto Alto", "detail": "> $5,000", "weight": "25%", "color": "#E3F2FD"},
        {"y": 4.0, "icon": "📈", "name": "Z-Score Alto", "detail": "> 3.0σ", "weight": "30%", "color": "#E8F5E9"},
        {"y": 3.0, "icon": "🔄", "name": "Alta Frecuencia", "detail": "> 20/día", "weight": "15%", "color": "#FFF3E0"},
        {"y": 2.0, "icon": "🌙", "name": "Horario Nocturno", "detail": "22:00-05:00", "weight": "10%", "color": "#F3E5F5"},
        {"y": 1.0, "icon": "⚠️", "name": "Comercio Riesgoso", "detail": "risk=high", "weight": "20%", "color": "#FFEBEE"},
    ]

    for r in rules:
        # Caja de regla
        fig.add_shape(
            type="rect",
            x0=0.3, y0=r["y"] - 0.35, x1=4.5, y1=r["y"] + 0.35,
            fillcolor=r["color"], line=dict(color="#BDBDBD", width=1),
        )
        fig.add_annotation(
            x=0.6, y=r["y"], text=r["icon"], font=dict(size=20), showarrow=False,
        )
        fig.add_annotation(
            x=1.6, y=r["y"] + 0.05,
            text=f"<b>{r['name']}</b>",
            font=dict(size=12, color="#1a1a2e"), showarrow=False, xanchor="left",
        )
        fig.add_annotation(
            x=3.3, y=r["y"] + 0.05,
            text=r["detail"],
            font=dict(size=11, color="#666"), showarrow=False,
        )
        fig.add_annotation(
            x=4.2, y=r["y"] + 0.05,
            text=f"<b>{r['weight']}</b>",
            font=dict(size=11, color="#D32F2F"), showarrow=False,
        )
        # Flecha hacia combinador
        fig.add_annotation(
            x=5.5, y=3.0,
            ax=4.5, ay=r["y"],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1.5,
            arrowcolor="#9E9E9E",
        )

    # Caja combinadora
    fig.add_shape(
        type="rect",
        x0=5.5, y0=2.2, x1=7.3, y1=3.8,
        fillcolor="#FFF9C4", line=dict(color="#F9A825", width=2.5),
    )
    fig.add_annotation(x=6.4, y=3.35, text="⚖️", font=dict(size=24), showarrow=False)
    fig.add_annotation(
        x=6.4, y=2.9, text="<b>Score</b>",
        font=dict(size=14, color="#1a1a2e"), showarrow=False,
    )
    fig.add_annotation(
        x=6.4, y=2.5, text="Suma ponderada",
        font=dict(size=10, color="#666"), showarrow=False,
    )

    # Flecha hacia resultado
    fig.add_annotation(
        x=8.0, y=3.0,
        ax=7.3, ay=3.0,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=2.5,
        arrowcolor="#F9A825",
    )

    # Resultados (lado derecho)
    results = [
        {"y": 4.2, "text": "🟢 0.0 — Sin riesgo", "color": "#E8F5E9", "border": "#4CAF50"},
        {"y": 3.2, "text": "🟡 0.01–0.50 — Riesgo bajo/medio", "color": "#FFF9C4", "border": "#FFC107"},
        {"y": 2.2, "text": "🔴 0.51–1.0 — Riesgo alto", "color": "#FFEBEE", "border": "#D32F2F"},
    ]

    for res in results:
        fig.add_shape(
            type="rect",
            x0=8.0, y0=res["y"] - 0.3, x1=10.8, y1=res["y"] + 0.3,
            fillcolor=res["color"], line=dict(color=res["border"], width=2),
        )
        fig.add_annotation(
            x=9.4, y=res["y"],
            text=f"<b>{res['text']}</b>",
            font=dict(size=11, color="#1a1a2e"), showarrow=False,
        )

    # Etiqueta "Resultado"
    fig.add_annotation(
        x=9.4, y=4.9, text="<b>Clasificación</b>",
        font=dict(size=14, color="#1a1a2e"), showarrow=False,
    )

    path = OUTPUT_DIR / "fraud_rules_diagram.png"
    fig.write_image(str(path), scale=2)
    print(f"✅ Generado: {path}")


if __name__ == "__main__":
    print("Generando imágenes para el README...\n")
    generate_data_flow()
    generate_benchmarks()
    generate_fraud_rules_diagram()
    print(f"\n📁 Imágenes guardadas en: {OUTPUT_DIR}")
    print("\n⚠️  Imágenes que debes tomar manualmente (screenshots del navegador):")
    print("   1. docs/images/dashboard_overview.png  → localhost:8501 página Overview")
    print("   2. docs/images/fraud_heatmap.png       → localhost:8501 página Fraud Analysis")
    print("   3. docs/images/notebook_execution.png  → localhost:8888 notebook 01 ejecutado")
