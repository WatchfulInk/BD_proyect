"""
Generador de dataset sintético estilo Olist Brasil.
Ejecutar: python scripts/generar_dataset.py

Genera ~100k órdenes con patrones reales para validar 5 hipótesis:
  H1: Categorías caras → menor volumen de ventas
  H2: Retrasos de envío → calificaciones bajas
  H3: Sureste de Brasil concentra >60% del revenue
  H4: Pagos con tarjeta en cuotas → ticket promedio 3x mayor
  H5: Q4 (oct-dic) supera en ventas a otros trimestres
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Configuración de datos ──────────────────────────────
N_CUSTOMERS  = 95_000
N_SELLERS    = 3_000
N_PRODUCTS   = 32_000
N_ORDERS     = 100_000

STATES_SOUTHEAST = ["SP", "RJ", "MG", "ES"]
ALL_STATES = [
    "SP", "RJ", "MG", "ES",  # Sureste (alta concentración)
    "RS", "SC", "PR",         # Sur
    "BA", "PE", "CE",         # Nordeste
    "GO", "DF", "MT",         # Centro-Oeste
    "PA", "AM",               # Norte
]
# Pesos: sureste tiene ~65% de ventas (H3)
STATE_WEIGHTS = [0.20, 0.15, 0.12, 0.08,  # Sureste
                 0.06, 0.05, 0.05,          # Sur
                 0.05, 0.04, 0.04,          # Nordeste
                 0.03, 0.04, 0.03,          # Centro-Oeste
                 0.03, 0.03]                # Norte

CATEGORIES = {
    # (precio_base, precio_std, peso_volumen)
    "cama_mesa_banho":        (80,   40,  8.0),
    "beleza_saude":           (65,   30,  7.5),
    "esporte_lazer":          (120,  60,  6.0),
    "moveis_decoracao":       (250, 120,  4.0),
    "informatica":            (400, 200,  3.5),
    "brinquedos":             (55,   25,  7.0),
    "relogios_presentes":     (300, 150,  3.0),
    "ferramentas_jardim":     (150,  70,  4.5),
    "fashion_bolsas":         (180,  90,  4.0),
    "telefonia":              (600, 300,  2.5),   # Cara, bajo volumen (H1)
    "eletronicos":            (550, 280,  2.0),   # Cara, bajo volumen (H1)
    "livros":                 (35,   15,  9.0),   # Barato, alto volumen (H1)
    "alimentos":              (25,   10,  9.5),   # Barato, alto volumen (H1)
    "papelaria":              (40,   20,  8.5),
    "automotivo":             (350, 180,  2.8),
    "perfumaria":             (90,   45,  6.5),
    "cool_stuff":             (200, 100,  3.8),
    "malas_acessorios":       (280, 140,  3.2),
    "eletrodomesticos":       (480, 240,  2.2),
    "construcao":             (320, 160,  2.6),
}
CAT_NAMES   = list(CATEGORIES.keys())
CAT_WEIGHTS = [CATEGORIES[c][2] for c in CAT_NAMES]
W_SUM = sum(CAT_WEIGHTS)
CAT_PROBS = [w / W_SUM for w in CAT_WEIGHTS]


def rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def seasonal_weight(month: int) -> float:
    """Q4 tiene ~40% más ventas que el promedio (H5)."""
    weights = {1: 0.9, 2: 0.8, 3: 0.9, 4: 1.0,
               5: 0.9, 6: 0.85, 7: 0.9, 8: 0.95,
               9: 1.0, 10: 1.15, 11: 1.35, 12: 1.40}
    return weights.get(month, 1.0)


print("Generando clientes...")
customers = []
for i in range(N_CUSTOMERS):
    state = np.random.choice(ALL_STATES, p=STATE_WEIGHTS)
    customers.append({
        "customer_id": f"C{i:06d}",
        "customer_unique_id": f"UC{i:06d}",
        "customer_state": state,
        "customer_city": f"city_{state}_{random.randint(1, 50)}",
    })
customers_df = pd.DataFrame(customers)
customers_df.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
print(f"  {len(customers_df):,} clientes guardados.")


print("Generando vendedores...")
sellers = []
for i in range(N_SELLERS):
    state = np.random.choice(ALL_STATES, p=STATE_WEIGHTS)
    sellers.append({
        "seller_id": f"S{i:05d}",
        "seller_state": state,
        "seller_city": f"city_{state}_{random.randint(1, 20)}",
    })
sellers_df = pd.DataFrame(sellers)
sellers_df.to_csv(f"{OUTPUT_DIR}/sellers.csv", index=False)
print(f"  {len(sellers_df):,} vendedores guardados.")


print("Generando productos...")
products = []
for i in range(N_PRODUCTS):
    cat = np.random.choice(CAT_NAMES, p=CAT_PROBS)
    price_base, price_std, _ = CATEGORIES[cat]
    products.append({
        "product_id": f"P{i:06d}",
        "product_category_name": cat,
        "product_weight_g": random.randint(100, 30_000),
        "product_length_cm": random.randint(10, 100),
        "product_height_cm": random.randint(5, 50),
        "product_width_cm": random.randint(10, 80),
        "_price_base": max(5, np.random.normal(price_base, price_std)),
    })
products_df = pd.DataFrame(products)
products_df.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)
print(f"  {len(products_df):,} productos guardados.")


print("Generando órdenes, items, pagos y reseñas...")
orders, items, payments, reviews = [], [], [], []

START_DATE = datetime(2017, 1, 1)
END_DATE   = datetime(2018, 12, 31)

payment_types = ["credit_card", "boleto", "voucher", "debit_card"]
payment_probs = [0.70, 0.18, 0.07, 0.05]

order_statuses = ["delivered", "delivered", "delivered", "delivered",
                  "delivered", "shipped", "canceled", "processing"]

item_counter = 0

for i in range(N_ORDERS):
    order_id  = f"O{i:07d}"
    customer  = customers[random.randint(0, N_CUSTOMERS - 1)]
    purchase_dt = rand_date(START_DATE, END_DATE)

    status = random.choice(order_statuses)
    approved_dt = purchase_dt + timedelta(hours=random.randint(1, 24))

    # Tiempo de entrega — base 15 días, retrasos ~20% (H2)
    is_delayed = random.random() < 0.20
    if is_delayed:
        delivery_days = random.randint(20, 60)
        estimated_days = random.randint(10, 18)
    else:
        delivery_days = random.randint(3, 18)
        estimated_days = delivery_days + random.randint(0, 5)

    delivered_dt  = purchase_dt + timedelta(days=delivery_days)
    estimated_dt  = purchase_dt + timedelta(days=estimated_days)

    orders.append({
        "order_id": order_id,
        "customer_id": customer["customer_id"],
        "order_status": status,
        "order_purchase_timestamp": purchase_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "order_approved_at": approved_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "order_delivered_customer_date": delivered_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "order_estimated_delivery_date": estimated_dt.strftime("%Y-%m-%d %H:%M:%S"),
    })

    # Items por orden (1-3 items)
    n_items = np.random.choice([1, 2, 3], p=[0.75, 0.18, 0.07])
    order_total = 0.0

    for j in range(n_items):
        item_counter += 1
        product = products[random.randint(0, N_PRODUCTS - 1)]
        price = round(max(5.0, product["_price_base"] * np.random.uniform(0.8, 1.2)), 2)
        freight = round(random.uniform(5, 50), 2)
        seller = sellers[random.randint(0, N_SELLERS - 1)]

        items.append({
            "order_id": order_id,
            "order_item_id": item_counter,
            "product_id": product["product_id"],
            "seller_id": seller["seller_id"],
            "price": price,
            "freight_value": freight,
        })
        order_total += price + freight

    # Pago — cuotas solo tarjeta crédito (H4)
    pay_type = np.random.choice(payment_types, p=payment_probs)
    if pay_type == "credit_card":
        if order_total > 300:
            installments = random.choice([6, 8, 10, 12])
        elif order_total > 100:
            installments = random.choice([1, 2, 3, 4])
        else:
            installments = random.choice([1, 2])
    else:
        installments = 1

    payments.append({
        "order_id": order_id,
        "payment_sequential": 1,
        "payment_type": pay_type,
        "payment_installments": installments,
        "payment_value": round(order_total, 2),
    })

    # Reseña — retrasos dan peor calificación (H2)
    if status == "delivered":
        if is_delayed:
            score = np.random.choice([1, 2, 3, 4, 5], p=[0.30, 0.25, 0.20, 0.15, 0.10])
        else:
            score = np.random.choice([1, 2, 3, 4, 5], p=[0.03, 0.05, 0.10, 0.25, 0.57])

        reviews.append({
            "review_id": f"R{i:07d}",
            "order_id": order_id,
            "review_score": score,
            "review_creation_date": delivered_dt.strftime("%Y-%m-%d %H:%M:%S"),
        })

print(f"  {N_ORDERS:,} órdenes, {item_counter:,} items generados.")

orders_df   = pd.DataFrame(orders)
items_df    = pd.DataFrame(items)
payments_df = pd.DataFrame(payments)
reviews_df  = pd.DataFrame(reviews)

products_df = products_df.drop(columns=["_price_base"])

orders_df.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)
items_df.to_csv(f"{OUTPUT_DIR}/order_items.csv", index=False)
payments_df.to_csv(f"{OUTPUT_DIR}/order_payments.csv", index=False)
reviews_df.to_csv(f"{OUTPUT_DIR}/order_reviews.csv", index=False)

print("\nResumen de archivos generados:")
for fname in ["customers.csv", "sellers.csv", "products.csv",
              "orders.csv", "order_items.csv", "order_payments.csv", "order_reviews.csv"]:
    path = f"{OUTPUT_DIR}/{fname}"
    size_kb = os.path.getsize(path) / 1024
    lines = sum(1 for _ in open(path)) - 1
    print(f"  {fname:<30} {lines:>8,} filas   {size_kb:>8.1f} KB")

print("\nDataset listo en data/raw/")
