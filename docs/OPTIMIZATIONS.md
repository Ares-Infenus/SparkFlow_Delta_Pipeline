# Optimizaciones Aplicadas

## Resumen

Este documento detalla las optimizaciones aplicadas al pipeline y sus resultados medidos.

---

## 1. Adaptive Query Execution (AQE)

**Configuración:**
```
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
spark.sql.adaptive.skewJoin.enabled = true
```

**Impacto:** _Pendiente de benchmark_

---

## 2. Broadcast Joins

**Uso:** Join de transacciones con tabla de merchants (~50K registros).

**Configuración:**
```
spark.sql.autoBroadcastJoinThreshold = 50MB
```

**Impacto:** _Pendiente de benchmark_

---

## 3. Particionamiento por Fecha

**Estrategia:**
- Bronze: `year`, `month`
- Silver: `year`, `month`, `is_fraud`

**Impacto:** _Pendiente de benchmark_

---

## 4. Delta Lake Z-Ordering

**Columnas:** `account_id`

**Impacto:** _Pendiente de benchmark_

---

## 5. Compresión ZSTD

**Configuración:**
```
spark.sql.parquet.compression.codec = zstd
```

**Impacto:** _Pendiente de benchmark_

---

## 6. Caching Estratégico

**DataFrames cacheados:**
- Silver layer (reutilizado en feature engineering y reglas de fraude)

**Impacto:** _Pendiente de benchmark_

---

## Resultados Consolidados

| Etapa | Sin Optimización | Con Optimización | Mejora |
|-------|-----------------|-----------------|--------|
| Ingesta Bronze | - | - | - |
| Transformaciones Silver | - | - | - |
| Feature Engineering | - | - | - |
| Reglas de Fraude | - | - | - |
| Escritura Gold | - | - | - |
| **Total Pipeline** | **-** | **-** | **-** |

> Los benchmarks se completarán tras ejecutar los notebooks con datos a escala completa (100M+ registros).
