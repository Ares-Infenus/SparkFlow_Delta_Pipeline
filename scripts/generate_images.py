"""Script para generar las imágenes del README programáticamente."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _draw_rounded_rect(fig, x0, y0, x1, y1, fill, border, width=2, radius=0.15):
    """Dibuja un rectángulo con esquinas redondeadas usando un path SVG."""
    r = radius
    fig.add_shape(
        type="path",
        path=(
            f"M {x0+r},{y0} "
            f"L {x1-r},{y0} Q {x1},{y0} {x1},{y0+r} "
            f"L {x1},{y1-r} Q {x1},{y1} {x1-r},{y1} "
            f"L {x0+r},{y1} Q {x0},{y1} {x0},{y1-r} "
            f"L {x0},{y0+r} Q {x0},{y0} {x0+r},{y0} Z"
        ),
        fillcolor=fill,
        line=dict(color=border, width=width),
        layer="below",
    )


def generate_data_flow():
    """Genera el diagrama de flujo de datos Bronze → Silver → Gold → Dashboard."""
    fig = go.Figure()

    W = 1400
    H = 700

    fig.update_layout(
        width=W,
        height=H,
        plot_bgcolor="#FAFBFC",
        paper_bgcolor="#FAFBFC",
        xaxis=dict(range=[0, 14], showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        yaxis=dict(range=[0, 8.5], showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        margin=dict(l=15, r=15, t=15, b=15),
        font=dict(family="Arial, sans-serif"),
    )

    # === Fondo sutil para el área de procesamiento ===
    fig.add_shape(
        type="rect",
        x0=0.3, y0=0.3, x1=13.7, y1=8.2,
        fillcolor="white",
        line=dict(color="#E0E4E8", width=1.5, dash="dot"),
        layer="below",
    )
    fig.add_annotation(
        x=7.0, y=8.0,
        text="<b>SPARKFLOW DELTA PIPELINE</b>  —  Arquitectura Medallion",
        font=dict(size=16, color="#4A5568"),
        showarrow=False,
    )

    # =====================================================================
    # FILA PRINCIPAL — Los 5 bloques en línea horizontal con amplio espacio
    # =====================================================================
    main_y = 5.0
    block_h = 2.8
    block_w = 2.1
    gap = 0.7  # espacio entre bloques

    blocks = [
        {
            "x": 1.5, "color": "#EBF0FA", "border": "#4A6FA5",
            "icon": "📥", "title": "GENERACIÓN",
            "line1": "Faker + PySpark",
            "line2": "100M+ registros",
            "line3": "Datos sintéticos",
            "badge": None,
        },
        {
            "x": 4.3, "color": "#FDF0E2", "border": "#C77C3A",
            "icon": "🥉", "title": "BRONZE",
            "line1": "Ingesta cruda",
            "line2": "Partición year/month",
            "line3": "Delta Lake + ZSTD",
            "badge": "RAW",
        },
        {
            "x": 7.1, "color": "#EDF2F7", "border": "#718096",
            "icon": "🥈", "title": "SILVER",
            "line1": "Dedup + Cast + Filter",
            "line2": "Window Functions",
            "line3": "Broadcast Joins",
            "badge": "CLEAN",
        },
        {
            "x": 9.9, "color": "#FEFCE8", "border": "#B7950B",
            "icon": "🥇", "title": "GOLD",
            "line1": "5 Reglas de fraude",
            "line2": "Score combinado",
            "line3": "Métricas agregadas",
            "badge": "BUSINESS",
        },
        {
            "x": 12.5, "color": "#FEE2E2", "border": "#DC2626",
            "icon": "📊", "title": "DASHBOARD",
            "line1": "Streamlit + Plotly",
            "line2": "KPIs interactivos",
            "line3": "localhost:8501",
            "badge": "VIZ",
        },
    ]

    for b in blocks:
        cx = b["x"]
        x0 = cx - block_w / 2
        x1 = cx + block_w / 2
        y0 = main_y - block_h / 2
        y1 = main_y + block_h / 2

        _draw_rounded_rect(fig, x0, y0, x1, y1, b["color"], b["border"], width=2.5, radius=0.12)

        # Badge pequeño arriba a la derecha
        if b["badge"]:
            badge_w = 0.55
            bx0 = x1 - badge_w - 0.08
            bx1 = x1 - 0.08
            by0 = y1 - 0.35
            by1 = y1 - 0.05
            _draw_rounded_rect(fig, bx0, by0, bx1, by1, b["border"], b["border"], width=0, radius=0.06)
            fig.add_annotation(
                x=(bx0 + bx1) / 2, y=(by0 + by1) / 2,
                text=f"<b>{b['badge']}</b>",
                font=dict(size=7, color="white"),
                showarrow=False,
            )

        # Icono grande
        fig.add_annotation(
            x=cx, y=main_y + 0.75,
            text=b["icon"], font=dict(size=30), showarrow=False,
        )

        # Título
        fig.add_annotation(
            x=cx, y=main_y + 0.2,
            text=f"<b>{b['title']}</b>",
            font=dict(size=13, color=b["border"]), showarrow=False,
        )

        # Línea separadora
        fig.add_shape(
            type="line",
            x0=x0 + 0.2, y0=main_y - 0.1, x1=x1 - 0.2, y1=main_y - 0.1,
            line=dict(color=b["border"], width=0.8, dash="dot"),
        )

        # Tres líneas de detalle
        fig.add_annotation(
            x=cx, y=main_y - 0.45,
            text=b["line1"], font=dict(size=10, color="#4A5568"), showarrow=False,
        )
        fig.add_annotation(
            x=cx, y=main_y - 0.75,
            text=b["line2"], font=dict(size=10, color="#4A5568"), showarrow=False,
        )
        fig.add_annotation(
            x=cx, y=main_y - 1.05,
            text=b["line3"], font=dict(size=10, color="#718096"), showarrow=False,
        )

    # =====================================================================
    # FLECHAS entre bloques — con etiquetas descriptivas
    # =====================================================================
    arrow_specs = [
        {"x0": 2.55, "x1": 3.25, "color": "#4A6FA5", "label": "Delta Write"},
        {"x0": 5.35, "x1": 6.05, "color": "#C77C3A", "label": "Transform"},
        {"x0": 8.15, "x1": 8.85, "color": "#718096", "label": "Fraud Rules"},
        {"x0": 10.95, "x1": 11.45, "color": "#B7950B", "label": "Read"},
    ]

    for a in arrow_specs:
        mid_x = (a["x0"] + a["x1"]) / 2

        # Línea de la flecha
        fig.add_annotation(
            x=a["x1"], y=main_y,
            ax=a["x0"], ay=main_y,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=2, arrowsize=1.2, arrowwidth=3,
            arrowcolor=a["color"],
        )

        # Etiqueta sobre la flecha
        fig.add_annotation(
            x=mid_x, y=main_y + 0.35,
            text=f"<i>{a['label']}</i>",
            font=dict(size=8, color=a["color"]),
            showarrow=False,
            bgcolor="white",
            borderpad=2,
        )

    # =====================================================================
    # FILA INFERIOR — Tecnologías y puertos
    # =====================================================================
    tech_y = 1.8
    techs = [
        {"x": 1.5, "text": "PySpark 3.5\nFaker 28.0", "color": "#4A6FA5"},
        {"x": 4.3, "text": "Delta Lake 3.2\nPartición por fecha", "color": "#C77C3A"},
        {"x": 7.1, "text": "Window Functions\nBroadcast Join", "color": "#718096"},
        {"x": 9.9, "text": "Z-Score + Reglas\nScore 0.0 → 1.0", "color": "#B7950B"},
        {"x": 12.5, "text": "Streamlit 1.37\nPlotly 5.22", "color": "#DC2626"},
    ]

    for t in techs:
        _draw_rounded_rect(
            fig,
            t["x"] - 0.9, tech_y - 0.4,
            t["x"] + 0.9, tech_y + 0.4,
            fill="#F7FAFC", border="#E2E8F0", width=1, radius=0.08,
        )
        fig.add_annotation(
            x=t["x"], y=tech_y,
            text=t["text"],
            font=dict(size=8.5, color=t["color"]),
            showarrow=False, align="center",
        )

        # Línea punteada vertical conectando bloque principal con tech
        fig.add_shape(
            type="line",
            x0=t["x"], y0=main_y - block_h / 2,
            x1=t["x"], y1=tech_y + 0.4,
            line=dict(color="#CBD5E0", width=1, dash="dot"),
        )

    # =====================================================================
    # FOOTER — Puertos
    # =====================================================================
    ports = [
        {"x": 4.3, "text": "JupyterLab → localhost:8888", "icon": "📓"},
        {"x": 7.1, "text": "Spark UI → localhost:4040", "icon": "⚡"},
        {"x": 12.5, "text": "Dashboard → localhost:8501", "icon": "🌐"},
    ]

    for p in ports:
        fig.add_annotation(
            x=p["x"], y=0.7,
            text=f"{p['icon']}  {p['text']}",
            font=dict(size=9, color="#718096"),
            showarrow=False,
            bgcolor="#F7FAFC",
            bordercolor="#E2E8F0",
            borderwidth=1,
            borderpad=4,
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
