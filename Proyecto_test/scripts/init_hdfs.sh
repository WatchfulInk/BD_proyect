#!/bin/bash
# Inicializa directorios en HDFS y sube el dataset.
# Ejecutar desde la raíz del proyecto: bash scripts/init_hdfs.sh
#
# MSYS_NO_PATHCONV=1 evita que Git Bash en Windows convierta rutas
# /data/olist → C:/... dentro de docker exec.

export MSYS_NO_PATHCONV=1

echo "=== Esperando que el Namenode esté listo... ==="
until docker exec namenode hdfs dfsadmin -report > /dev/null 2>&1; do
  echo "  Namenode no disponible, esperando 5s..."
  sleep 5
done

LIVE=$(docker exec namenode hdfs dfsadmin -report 2>/dev/null | grep "Live datanodes" | grep -o '[0-9]*')
echo "  Namenode activo. Datanodes vivos: ${LIVE:-0}"

if [ "${LIVE:-0}" -eq 0 ]; then
  echo "  [AVISO] Sin datanodes activos. Esperando 15s más..."
  sleep 15
  LIVE=$(docker exec namenode hdfs dfsadmin -report 2>/dev/null | grep "Live datanodes" | grep -o '[0-9]*')
  echo "  Datanodes vivos: ${LIVE:-0}"
fi

echo ""
echo "=== Creando estructura de directorios en HDFS ==="
docker exec namenode bash -c "hdfs dfs -mkdir -p /data/olist && hdfs dfs -mkdir -p /outputs && hdfs dfs -chmod 777 /data/olist && hdfs dfs -chmod 777 /outputs"
echo "  Directorios creados."

echo ""
echo "=== Subiendo dataset a HDFS ==="
FILES=(customers.csv sellers.csv products.csv orders.csv order_items.csv order_payments.csv order_reviews.csv)

for f in "${FILES[@]}"; do
  LOCAL="data/raw/$f"
  if [ -f "$LOCAL" ]; then
    echo "  Subiendo $f..."
    docker cp "$LOCAL" "namenode:/tmp/$f"
    docker exec namenode bash -c "hdfs dfs -put -f /tmp/$f /data/olist/$f && rm /tmp/$f"
    echo "    OK"
  else
    echo "  [AVISO] $f no encontrado en data/raw/"
  fi
done

echo ""
echo "=== Verificando archivos en HDFS ==="
docker exec namenode bash -c "hdfs dfs -ls /data/olist/"
echo ""
echo "=== Listo. Dataset disponible en hdfs://namenode:8020/data/olist/ ==="
