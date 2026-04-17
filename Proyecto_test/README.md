# Proyecto Big Data — Análisis E-commerce Olist

Stack: **Hadoop 3.2.1 · Spark 3.0 · PySpark · JupyterLab**  
Dataset: Olist Brasil (sintético, ~100k órdenes)

---

## Requisitos previos

- Docker Desktop instalado y corriendo
- Python 3.8+ (para generar el dataset)
- Al menos 8 GB RAM disponibles
- Terminal: Git Bash (incluido con Git for Windows)

---

## Inicio rápido

Ejecutar todos los comandos desde la carpeta raíz del proyecto (`Proyecto_test/`):

```bash
# 1. Generar dataset sintético
python scripts/generar_dataset.py

# 2. Levantar toda la infraestructura (primera vez tarda ~3 min por el build)
docker-compose up -d --build

# 3. Esperar ~20s a que el datanode se registre, luego subir datos a HDFS
bash scripts/init_hdfs.sh
```

> **Nota Windows / Git Bash:** el script `init_hdfs.sh` incluye `MSYS_NO_PATHCONV=1`
> para evitar que Git Bash convierta rutas `/data/olist` a rutas de Windows.
> Si usas PowerShell, ejecuta el script desde Git Bash.

---

## URLs de acceso

| Servicio        | URL                      | Credencial         |
|----------------|--------------------------|--------------------|
| JupyterLab      | http://localhost:8888    | token: bigdata2024 |
| Spark UI        | http://localhost:18080   | —                  |
| Hadoop HDFS UI  | http://localhost:9870    | —                  |
| Spark Worker 1  | http://localhost:8081    | —                  |
| Spark Worker 2  | http://localhost:8082    | —                  |

> El puerto del Spark UI es **18080** (no 8080) porque ese puerto suele estar
> ocupado por otras aplicaciones en Windows.

---

## Estructura del proyecto

```
Proyecto_test/
├── docker-compose.yml              Orquestación de contenedores
├── hadoop.env                      Variables de entorno Hadoop
├── docker/
│   └── jupyter/
│       ├── Dockerfile              Imagen custom de JupyterLab
│       └── requirements.txt        Dependencias Python
├── scripts/
│   ├── generar_dataset.py          Generador de dataset sintético
│   ├── init_hdfs.sh                Inicialización HDFS + carga de datos
│   └── start.sh                    Script de inicio completo
├── notebooks/
│   ├── 00_setup_carga.ipynb        Verificación y exploración inicial
│   ├── 01_H1_precio_volumen.ipynb
│   ├── 02_H2_envio_calificacion.ipynb
│   ├── 03_H3_revenue_geografico.ipynb
│   ├── 04_H4_metodos_pago.ipynb
│   └── 05_H5_estacionalidad.ipynb
├── data/
│   └── raw/                        Dataset CSV generado
└── outputs/
    └── graficas/                   Gráficas exportadas (.png)
```

---

## Hipótesis analizadas

| # | Hipótesis | Resultado esperado |
|---|-----------|-------------------|
| H1 | Categorías caras tienen menor volumen de ventas | Confirmada |
| H2 | Retrasos de envío bajan la calificación del cliente | Confirmada |
| H3 | Sureste de Brasil concentra >60% del revenue | Confirmada |
| H4 | Pagos en cuotas tienen ticket promedio 3x mayor | Confirmada |
| H5 | Q4 (oct-dic) supera en ventas a todos los trimestres | Confirmada |

---

## Gestión del ambiente

### Pausar y reanudar (conserva todos los datos)
```bash
docker-compose stop       # pausa los contenedores
docker-compose start      # los reanuda tal como estaban
```

### Reiniciar completamente (conserva volúmenes HDFS)
```bash
docker-compose down
docker-compose up -d
```
> No es necesario volver a correr `init_hdfs.sh` — los datos en HDFS se conservan.

### Limpiar todo y empezar desde cero
```bash
docker-compose down -v            # elimina contenedores + volúmenes HDFS
docker-compose up -d              # levanta la infraestructura de nuevo
bash scripts/init_hdfs.sh         # vuelve a subir los CSV a HDFS
```

### Forzar recrear solo el contenedor Jupyter
Necesario cuando se cambian variables de entorno en `docker-compose.yml`:
```bash
docker-compose up -d --force-recreate jupyter
```

### Reconstruir imagen Jupyter (cambios en Dockerfile o requirements.txt)
```bash
docker-compose down -v
docker-compose build --no-cache jupyter
docker-compose up -d
bash scripts/init_hdfs.sh
```

### Resumen rápido

| Necesidad | Comando |
|-----------|---------|
| Pausar sin perder datos | `docker-compose stop` |
| Reanudar | `docker-compose start` |
| Reiniciar contenedores | `docker-compose down` → `up -d` |
| Limpiar HDFS y empezar de cero | `docker-compose down -v` → `up -d` → `init_hdfs.sh` |
| Forzar recrear solo Jupyter | `docker-compose up -d --force-recreate jupyter` |
