# 📸 Imágenes necesarias para el README

Este documento lista cada imagen referenciada en el README, qué debe mostrar y cómo crearla.

---

## 1. `dashboard_overview.png`

**Qué debe mostrar:** La página principal del dashboard de Streamlit (Overview).

**Cómo crearla:**
1. Ejecuta los 3 notebooks para generar datos en la capa Gold
2. Abre `http://localhost:8501` en tu navegador
3. Navega a la página "Overview"
4. Toma un screenshot completo de la página (incluyendo las 4 tarjetas KPI y los 2 gráficos)
5. Resolución recomendada: 1920x1080

**Elementos clave que deben verse:**
- 4 KPI cards arriba (Total Transacciones, Total Fraudes, Tasa de Fraude, Monto Fraude)
- Gráfico de barras horizontales (Volumen por Categoría)
- Gráfico de línea (Fraudes Detectados por Mes)

---

## 2. `data_flow.png`

**Qué debe mostrar:** Diagrama del flujo de datos desde la generación hasta el dashboard.

**Cómo crearla:**
- **Opción A (recomendada):** Usa [Excalidraw](https://excalidraw.com/) o [draw.io](https://app.diagrams.net/)
- **Opción B:** Exporta el diagrama Mermaid del README usando [mermaid.live](https://mermaid.live/)

**Elementos que debe incluir:**
- 4 bloques principales: Generación → Bronze → Silver → Gold → Dashboard
- Flechas con etiquetas explicando qué pasa entre cada paso
- Colores: Bronce (#CD7F32), Plata (#C0C0C0), Oro (#FFD700), Rojo (#FF4B4B)
- Iconos simples: base de datos, filtro, lupa, gráfico
- Texto debajo de cada bloque explicando en lenguaje simple

**Resolución:** 1200x400 px (formato panorámico)

---

## 3. `fraud_heatmap.png`

**Qué debe mostrar:** La página de Fraud Analysis del dashboard, con el heatmap visible.

**Cómo crearla:**
1. Abre `http://localhost:8501`
2. Navega a la página "Fraud Analysis"
3. Asegúrate de que todas las categorías estén seleccionadas en el filtro lateral
4. Toma screenshot del heatmap de "Tasa de Fraude por Categoría y Mes"
5. Incluye también la tabla de datos detallados debajo

**Elementos clave:**
- Heatmap con escala de colores de blanco a rojo
- Filas: 15 categorías de comercio
- Columnas: meses 1-6
- Las celdas más rojas deberían ser insurance y home_improvement

**Resolución:** 1920x1080

---

## 4. `benchmarks.png`

**Qué debe mostrar:** Comparación de rendimiento antes/después de optimizaciones.

**Cómo crearla:**
- **Opción A:** Crea un gráfico de barras en Python/Plotly con estos datos:

```python
import plotly.graph_objects as go

etapas = ["Ingesta Bronze", "Transformaciones Silver", "Feature Engineering", "Reglas de Fraude", "Escritura Gold"]
sin_opt = [5.11, 3.95, 0.23, 0.14, 4.41]
con_opt = [2.82, 3.95, 0.23, 0.14, 4.41]

fig = go.Figure(data=[
    go.Bar(name="Sin Optimización", x=etapas, y=sin_opt, marker_color="#9E9E9E"),
    go.Bar(name="Con Optimización", x=etapas, y=con_opt, marker_color="#4CAF50"),
])
fig.update_layout(
    title="Benchmark: Tiempo de Ejecución por Etapa (100K registros)",
    yaxis_title="Tiempo (segundos)",
    barmode="group",
    width=1000, height=500,
)
fig.write_image("docs/images/benchmarks.png")
```

- **Opción B:** Crea el gráfico en Excel/Google Sheets y exporta como imagen

**Resolución:** 1000x500

---

## 5. `notebook_execution.png`

**Qué debe mostrar:** El notebook 01 ejecutándose en JupyterLab con outputs visibles.

**Cómo crearla:**
1. Abre `http://localhost:8888` y abre el notebook `01_ingesta_bronze.ipynb`
2. Ejecuta todas las celdas
3. Haz scroll para que se vean:
   - La celda de generación de datos con el benchmark ("completado en X.XX segundos")
   - La tabla de muestra con `.show(5)` mostrando las primeras transacciones
   - El schema del DataFrame
4. Toma un screenshot largo (puedes usar extensión de navegador para captura de scroll)

**Elementos clave:**
- Código Python visible
- Output con tiempos de ejecución
- Tabla de datos con columnas: transaction_id, account_id, amount, is_fraud
- Barra lateral de JupyterLab con los 3 notebooks

**Resolución:** 1920x1200 (puede ser más alto si incluyes scroll)

---

## Resumen

| # | Archivo | Tipo | Herramienta sugerida |
|---|---------|------|---------------------|
| 1 | `dashboard_overview.png` | Screenshot | Navegador |
| 2 | `data_flow.png` | Diagrama | Excalidraw / draw.io |
| 3 | `fraud_heatmap.png` | Screenshot | Navegador |
| 4 | `benchmarks.png` | Gráfico | Plotly / Excel |
| 5 | `notebook_execution.png` | Screenshot | Navegador + extensión de scroll |

**Nota:** Todas las imágenes deben guardarse en la carpeta `docs/images/` para que los links del README funcionen correctamente.
