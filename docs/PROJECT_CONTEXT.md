# PROJECT_CONTEXT.md — Big Data Analytics con PySpark

---

## 1. Resumen Ejecutivo

### Objetivo
Construir un pipeline de Big Data end-to-end para la detección de patrones de fraude en transacciones bancarias, procesando 100M+ registros (~10-20GB) usando Apache Spark en un entorno local dockerizado. El proyecto demuestra dominio de procesamiento distribuido, optimización avanzada de Spark y almacenamiento con Delta Lake.

### Problema de negocio
Las instituciones financieras procesan millones de transacciones diarias. Identificar patrones anómalos y potencialmente fraudulentos a esta escala es inviable con herramientas in-memory como Pandas. Se requiere un enfoque distribuido que permita:
- Procesar 6+ meses de transacciones en tiempos razonables (<15 min para el pipeline completo)
- Aplicar reglas de detección de anomalías sobre ventanas temporales
- Generar reportes agregados y dashboards consumibles por analistas de fraude

### Métricas de éxito

| Métrica | Objetivo |
|---------|----------|
| Volumen procesado | ≥10GB / 100M+ filas sin OOM |
| Tiempo total del pipeline | <15 minutos en Spark local (8 cores, 16GB RAM) |
| Mejora con optimizaciones | ≥30% reducción de tiempo vs. pipeline naïve |
| Cobertura de tests | ≥80% en módulos de transformación |
| Reproducibilidad | `docker compose up` → pipeline funcional en <5 min |

---

## 2. Arquitectura General

### Diagrama de flujo end-to-end

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INFRAESTRUCTURA (Docker Compose)                     │
│                                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Datos    │    │   Spark      │    │  Delta Lake  │    │  Streamlit   │  │
│  │  Crudos   │───▶│  Processing  │───▶│  Storage     │───▶│  Dashboard   │  │
│  │  (CSV/    │    │  (PySpark)   │    │  (Bronze/    │    │  (Viz +      │  │
│  │  Parquet) │    │              │    │  Silver/Gold)│    │  Reportes)   │  │
│  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │
│       │                │                     │                   │          │
│       ▼                ▼                     ▼                   ▼          │
│  data/raw/       Notebooks 1-3         data/delta/         localhost:8501   │
│                  (JupyterLab)          ├── bronze/                          │
│                  localhost:8888        ├── silver/                          │
│                                       └── gold/                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Arquitectura de datos: Medallion (Bronze → Silver → Gold)

```
BRONZE (Raw)                SILVER (Clean)              GOLD (Business)
─────────────              ──────────────              ───────────────
• Ingesta cruda            • Deduplicación             • Métricas de fraude
• Schema enforcement       • Tipado correcto           • Agregaciones por
• Partición por fecha      • Filtros de calidad          merchant/categoría
• Sin transformaciones     • Joins enriquecidos        • Features para reglas
                           • Partición optimizada      • Tablas para dashboard
```

### Flujo de notebooks

```
Notebook 01: Ingesta & Bronze Layer
    ├── Carga de datos crudos (CSV/Parquet)
    ├── Schema validation
    ├── Escritura Delta (bronze) con partición por fecha
    └── Benchmark: sin optimización vs. con optimización

Notebook 02: Transformaciones & Silver/Gold Layers
    ├── Lectura Delta bronze
    ├── Limpieza y deduplicación
    ├── Window functions (rolling aggregations por cuenta)
    ├── Feature engineering para detección de anomalías
    ├── Broadcast joins con tablas de referencia
    ├── Escritura Delta silver + gold
    └── Benchmark: AQE, caching, broadcast

Notebook 03: Análisis, Reglas de Fraude & Reportes
    ├── Lectura Delta gold
    ├── Reglas basadas en umbrales y z-scores
    ├── Spark SQL: consultas complejas de análisis
    ├── Export de resultados para dashboard
    ├── Time travel: comparación temporal
    └── Z-ordering y OPTIMIZE
```

---

## 3. Stack Tecnológico

| Componente | Tecnología | Versión | Justificación |
|------------|-----------|---------|---------------|
| Motor de procesamiento | Apache Spark (PySpark) | 3.5.x | Estándar de la industria para Big Data. Soporte nativo para Delta Lake y SQL. |
| Formato de almacenamiento | Delta Lake | 3.2.x | ACID transactions, time travel, schema evolution, Z-ordering. Supera a Parquet puro. |
| Entorno de desarrollo | JupyterLab | 4.x | Ideal para exploración iterativa. Integración nativa con PySpark. |
| Orquestación local | Docker Compose | v2 | Reproduce el entorno completo en cualquier máquina. Un solo `docker compose up`. |
| Dashboard | Streamlit | 1.x | Rápido de construir, Python nativo, ideal para portafolio. Plotly para gráficos interactivos. |
| Visualización | Plotly | 5.x | Gráficos interactivos que se integran con Streamlit. Mejor que matplotlib para dashboards. |
| Testing | pytest + chispa | - | `pytest` para lógica Python, `chispa` para comparación de DataFrames Spark. |
| Linting | ruff | - | Reemplaza flake8+isort+black. Extremadamente rápido. |
| CI/CD | GitHub Actions | - | Gratis para repos públicos. Lint + test + build Docker en cada push. |
| Datos sintéticos | Faker + PySpark | - | Generación de datos realistas a escala cuando Kaggle no cubra el volumen. |

### Datasets candidatos (Kaggle/UCI)

| Dataset | Registros | Tamaño | Notas |
|---------|-----------|--------|-------|
| [IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection) | ~590K | ~1.5GB | Se escalará sintéticamente a 100M+ |
| [Synthetic Financial Datasets (PaySim)](https://www.kaggle.com/datasets/ealaxi/paysim1) | 6.3M | ~500MB | Transacciones simuladas con fraude etiquetado |
| [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) | 284K | ~150MB | PCA features, útil como seed para generación |

**Estrategia de escala**: Se usará un dataset público como semilla (schema real y distribuciones estadísticas) y se amplificará con Faker + PySpark hasta alcanzar 100M+ registros (~10-20GB en Parquet).

---

## 4. Gobernanza y Seguridad

### Clasificación del proyecto
- **Tipo**: Proyecto Open Source para portafolio público
- **Datos**: 100% sintéticos o públicos. No se manejan datos reales de clientes.
- **Riesgo PII**: NINGUNO. Los datos generados no contienen información personal real.

### Manejo de credenciales y secretos

| Elemento | Estrategia |
|----------|-----------|
| Variables de entorno | Archivo `.env` (excluido de git via `.gitignore`) |
| Secrets en CI/CD | GitHub Secrets para cualquier token |
| Contraseñas hardcodeadas | PROHIBIDO. Se usa `python-dotenv` o variables de entorno |
| `.env.example` | Incluido en el repo como plantilla (sin valores reales) |

### Reproducibilidad

```bash
# Cualquier persona con Docker puede ejecutar el proyecto completo:
git clone https://github.com/<user>/bigdata-fraud-pyspark.git
cd bigdata-fraud-pyspark
cp .env.example .env
docker compose up -d

# Acceder a:
# - JupyterLab:  http://localhost:8888
# - Streamlit:   http://localhost:8501
```

### Compliance y licencias
- Todos los datos son públicos (Kaggle) o sintéticos
- Dependencias: licencias Apache 2.0 / MIT / BSD (verificadas)
- Licencia del proyecto: MIT

---

## 5. Plan de ejecución (4 semanas, dedicación parcial)

### Semana 1: Setup + Ingesta (Bronze)
- [ ] Configurar Docker Compose (Spark + JupyterLab + Streamlit)
- [ ] Descargar dataset seed de Kaggle
- [ ] Construir generador de datos sintéticos (escalar a 100M+)
- [ ] Notebook 01: Ingesta y capa Bronze con Delta Lake
- [ ] Documentar benchmarks de ingesta

### Semana 2: Transformaciones + Optimizaciones (Silver/Gold)
- [ ] Notebook 02: Limpieza, deduplicación, feature engineering
- [ ] Implementar window functions (rolling stats por cuenta)
- [ ] Broadcast joins con tablas de referencia
- [ ] Comparar rendimiento: sin optimización vs. con AQE + caching + particionamiento
- [ ] Escritura Delta silver y gold

### Semana 3: Análisis + Dashboard
- [ ] Notebook 03: Reglas de detección de fraude (z-scores, umbrales)
- [ ] Consultas SQL complejas sobre tablas Delta
- [ ] Time travel y Z-ordering demos
- [ ] Construir dashboard Streamlit con Plotly
- [ ] Documento de optimizaciones aplicadas

### Semana 4: CI/CD + Pulido + Documentación
- [ ] Tests unitarios con pytest + chispa
- [ ] GitHub Actions: lint (ruff) + test + build Docker
- [ ] README.md profesional con badges, screenshots, instrucciones
- [ ] Revisar y pulir notebooks (narrativa clara, outputs limpios)
- [ ] Documento final de optimizaciones (benchmarks before/after)
