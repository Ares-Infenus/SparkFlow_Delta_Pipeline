# 🤝 Guía de Contribución

Gracias por tu interés en contribuir a **SparkFlow Delta Pipeline**. Esta guía te ayudará a configurar tu entorno y seguir las convenciones del proyecto.

---

## 🚀 Configuración del entorno

### Prerrequisitos

- Python 3.10+
- Java 11+ (para PySpark)
- Docker Desktop con Compose v2
- Git

### Setup local

```bash
# 1. Fork y clonar
git clone https://github.com/<tu-usuario>/SparkFlow-Delta-Pipeline.git
cd SparkFlow-Delta-Pipeline

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# 4. Configurar entorno
cp .env.example .env

# 5. Verificar que todo funcione
make lint
make test-local
```

---

## 📋 Convenciones de código

### Estilo

- **Linter/Formatter:** [ruff](https://docs.astral.sh/ruff/) (configurado en `pyproject.toml`)
- **Line length:** 100 caracteres
- **Target Python:** 3.11
- **Reglas activas:** E, F, I, W, UP, S, B, SIM

```bash
# Ejecutar lint + autoformat
make lint
```

### Estructura de código

- Funciones de transformación van en `src/transformations.py`
- Reglas de fraude van en `src/fraud_rules.py`
- Configuración centralizada en `src/config.py`
- Cada función debe tener type hints y docstring

### Tests

- Framework: **pytest** + **chispa** para DataFrames
- Los tests van en `tests/test_<modulo>.py`
- Usa el fixture `spark` de `conftest.py` para SparkSession

```bash
# Ejecutar tests
make test-local

# Ejecutar un test específico
pytest tests/test_fraud_rules.py::TestFlagHighAmount -v
```

---

## 🔀 Flujo de trabajo

### 1. Crear una rama

```bash
git checkout -b feature/nueva-regla-fraude
# o
git checkout -b fix/corregir-zscore
```

**Convención de nombres:**
- `feature/` — Nueva funcionalidad
- `fix/` — Corrección de bug
- `docs/` — Cambios en documentación
- `refactor/` — Refactorización sin cambio funcional

### 2. Hacer cambios

- Escribe tests para cualquier código nuevo
- Ejecuta `make lint` antes de cada commit
- Ejecuta `make test-local` para verificar que no rompiste nada

### 3. Commit

```bash
git add <archivos-específicos>
git commit -m "feat: agregar regla de detección por geolocalización"
```

**Formato de commit messages:**
- `feat:` — Nueva funcionalidad
- `fix:` — Corrección de bug
- `docs:` — Cambios en documentación
- `test:` — Agregar o modificar tests
- `refactor:` — Refactorización
- `chore:` — Tareas de mantenimiento

### 4. Pull Request

- Título claro y conciso (< 70 caracteres)
- Descripción con: qué cambió, por qué, cómo probarlo
- Asegúrate de que el CI pase (lint + test + docker build)

---

## 💡 Ideas para contribuir

| Área | Idea | Dificultad |
|------|------|-----------|
| 🧠 Reglas | Detección por geolocalización (país de la cuenta vs. país de la compra) | Media |
| 🧠 Reglas | Velocidad de transacción (dos compras en países diferentes en < 1 hora) | Alta |
| 📊 Dashboard | Página de detalle por cuenta individual | Media |
| 📊 Dashboard | Gráfico de red de transacciones sospechosas | Alta |
| ⚡ Performance | Bucketing por account_id para joins más rápidos | Media |
| 🧪 Tests | Tests de integración end-to-end (Bronze → Gold) | Media |
| 📝 Docs | Traducción del README a inglés | Baja |

---

## ❓ ¿Preguntas?

Abre un [issue](https://github.com/<tu-usuario>/SparkFlow-Delta-Pipeline/issues) y te responderemos.
