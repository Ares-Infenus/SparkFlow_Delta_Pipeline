# 📋 Changelog

Todos los cambios notables de este proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

---

## [1.0.0] - 2026-03-26

### ✨ Agregado
- Pipeline completo Bronze → Silver → Gold con Delta Lake
- Generador de datos sintéticos escalable a 100M+ transacciones
- 5 reglas de detección de fraude con score ponderado combinado
  - Monto alto (> $5,000)
  - Z-Score alto (> 3.0σ)
  - Alta frecuencia (> 20 txns/día)
  - Horario nocturno (22:00-05:00)
  - Comercio de alto riesgo
- Window functions para rolling stats por cuenta (7 días)
- Broadcast join con tabla de merchants (50K registros)
- Dashboard Streamlit con 3 páginas: Overview, Fraud Analysis, Optimizations
- 28 tests automatizados con pytest + chispa
- CI/CD con GitHub Actions (lint + test + docker build)
- Docker Compose para levantar todo el stack con un comando
- 3 Jupyter notebooks documentados con benchmarks
- Configuración optimizada de Spark: AQE, KryoSerializer, ZSTD, particionamiento

### 🛠️ Infraestructura
- Dockerfile para Spark + JupyterLab + Delta Lake
- Dockerfile para Streamlit dashboard
- Makefile con 12 comandos de utilidad
- Configuración de ruff para linting/formatting
- `.env.example` con todas las variables documentadas

### 📖 Documentación
- README profesional con secciones para audiencia técnica y no técnica
- PROJECT_CONTEXT.md con plan de ejecución detallado
- OPTIMIZATIONS.md con técnicas aplicadas
- CONTRIBUTING.md con guía de contribución
- Guía de imágenes necesarias para el README
