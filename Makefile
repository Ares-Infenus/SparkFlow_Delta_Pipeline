.PHONY: help up down build test lint clean generate-data

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Docker ===
up: ## Levantar todos los servicios
	docker compose up -d

down: ## Detener todos los servicios
	docker compose down

build: ## Reconstruir imágenes Docker
	docker compose build --no-cache

logs: ## Ver logs de todos los servicios
	docker compose logs -f

# === Desarrollo ===
lint: ## Ejecutar linter (ruff)
	ruff check src/ tests/ dashboard/ --fix
	ruff format src/ tests/ dashboard/

test: ## Ejecutar tests
	docker compose exec spark-jupyter pytest tests/ -v

test-local: ## Ejecutar tests localmente (requiere Spark instalado)
	pytest tests/ -v

# === Datos ===
generate-data: ## Generar datos sintéticos (100M+ registros)
	docker compose exec spark-jupyter python scripts/generate_data.py \
		--num-records 100000000 \
		--output-path data/raw/transactions

download-data: ## Descargar dataset seed de Kaggle
	bash scripts/download_data.sh

# === Limpieza ===
clean: ## Limpiar datos generados y caches de Spark
	rm -rf data/raw/*.parquet data/raw/*.csv
	rm -rf data/delta/bronze/* data/delta/silver/* data/delta/gold/*
	rm -rf /tmp/spark/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null || true

clean-all: clean down ## Limpieza total (datos + contenedores)
	docker compose down -v --rmi local
