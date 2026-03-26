#!/bin/bash
# Script para descargar datasets seed de Kaggle
# Requiere: KAGGLE_USERNAME y KAGGLE_KEY configurados en .env

set -euo pipefail

DATA_DIR="data/raw"
SEED_DIR="data/seed"

echo "================================================="
echo " Descarga de datasets seed de Kaggle"
echo "================================================="

# Verificar que kaggle CLI está instalado
if ! command -v kaggle &> /dev/null; then
    echo "Instalando kaggle CLI..."
    pip install kaggle --quiet
fi

# Verificar credenciales
if [ -z "${KAGGLE_USERNAME:-}" ] || [ -z "${KAGGLE_KEY:-}" ]; then
    echo "WARN: KAGGLE_USERNAME y/o KAGGLE_KEY no configurados."
    echo "      Configura las variables en el archivo .env"
    echo "      O descarga manualmente desde Kaggle."
    exit 1
fi

mkdir -p "$DATA_DIR" "$SEED_DIR"

# Opción 1: IEEE-CIS Fraud Detection
echo ""
echo "Descargando IEEE-CIS Fraud Detection dataset..."
kaggle competitions download -c ieee-fraud-detection -p "$DATA_DIR" --quiet || {
    echo "WARN: No se pudo descargar IEEE-CIS. Intentando alternativa..."
}

# Opción 2: PaySim (Synthetic Financial Dataset)
echo ""
echo "Descargando PaySim dataset..."
kaggle datasets download -d ealaxi/paysim1 -p "$DATA_DIR" --quiet --unzip || {
    echo "WARN: No se pudo descargar PaySim."
}

# Crear muestra seed para tests
echo ""
echo "Creando muestra seed para tests..."
if ls "$DATA_DIR"/*.csv &> /dev/null; then
    head -1001 "$(ls "$DATA_DIR"/*.csv | head -1)" > "$SEED_DIR/sample_transactions.csv"
    echo "Muestra creada en $SEED_DIR/sample_transactions.csv"
fi

echo ""
echo "================================================="
echo " Descarga completada"
echo "================================================="
ls -lh "$DATA_DIR"/
