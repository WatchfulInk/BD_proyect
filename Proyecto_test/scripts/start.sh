#!/bin/bash
# Script de inicio completo del proyecto.
# Uso: bash scripts/start.sh

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   Big Data — Olist Analysis                  ║"
echo "║   Hadoop 3.2 + Spark 3.0 + JupyterLab       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# 1. Generar dataset si no existe
if [ ! -f "data/raw/orders.csv" ]; then
  echo "[1/4] Generando dataset sintético..."
  python scripts/generar_dataset.py
else
  echo "[1/4] Dataset ya existe, omitiendo generación."
fi

# 2. Levantar contenedores
echo ""
echo "[2/4] Levantando infraestructura Docker..."
docker-compose up -d --build

# 3. Esperar y subir datos a HDFS
echo ""
echo "[3/4] Inicializando HDFS y subiendo datos (espera 30s)..."
sleep 30
bash scripts/init_hdfs.sh

# 4. Info de acceso
echo ""
echo "[4/4] Todo listo."
echo ""
echo "  URLs de acceso:"
echo "  ─────────────────────────────────────────────────"
echo "  JupyterLab     → http://localhost:8888  (token: bigdata2024)"
echo "  Spark UI       → http://localhost:8080"
echo "  Hadoop HDFS UI → http://localhost:9870"
echo "  Spark Worker 1 → http://localhost:8081"
echo "  Spark Worker 2 → http://localhost:8082"
echo "  ─────────────────────────────────────────────────"
echo ""
echo "  Para detener: docker-compose down"
