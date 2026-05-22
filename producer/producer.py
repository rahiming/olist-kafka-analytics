import json
import time
from pathlib import Path

import pandas as pd
from confluent_kafka import Producer

BOOTSTRAP = "localhost:9092"
TOPIC = "ecommerce-orders"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DELAY = 0.05


def load_source_data(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load source CSV files from the data directory."""
    orders = pd.read_csv(data_dir / "olist_orders_dataset.csv")
    items = pd.read_csv(data_dir / "olist_order_items_dataset.csv")
    products = pd.read_csv(data_dir / "olist_products_dataset.csv")
    return orders, items, products


def build_orders_dataframe(
    orders: pd.DataFrame,
    items: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Join, clean and aggregate raw data into one row per order."""
    df = orders.merge(items, on="order_id", how="left")
    df = df.merge(
        products[["product_id", "product_category_name"]],
        on="product_id",
        how="left",
    )

    df = df[df["order_status"] == "delivered"].copy()
    df = df.dropna(subset=["price"])
    df["product_category_name"] = df["product_category_name"].fillna("autre")

    df = (
        df.groupby("order_id")
        .agg(
            {
                "order_purchase_timestamp": "first",
                "customer_id": "first",
                "order_status": "first",
                "product_category_name": "first",
                "price": "sum",
                "freight_value": "sum",
            }
        )
        .reset_index()
    )
    df["total"] = df["price"] + df["freight_value"]
    return df


def row_to_message(row: pd.Series) -> dict:
    """Convert an aggregated order row to the Kafka payload schema."""
    return {
        "order_id": row["order_id"],
        "customer_id": row["customer_id"],
        "status": row["order_status"],
        "category": row["product_category_name"],
        "price": round(float(row["price"]), 2),
        "freight": round(float(row["freight_value"]), 2),
        "total": round(float(row["total"]), 2),
        "timestamp": row["order_purchase_timestamp"],
    }


def on_delivery(err, msg) -> None:
    if err:
        print(f"[ERROR] Delivery failed: {err}")


def publish_dataframe(
    df: pd.DataFrame,
    producer: Producer,
    topic: str = TOPIC,
    delay: float = DELAY,
) -> int:
    """Publish one Kafka message per order."""
    published = 0
    total_rows = len(df)

    for _, row in df.iterrows():
        try:
            producer.produce(
                topic,
                key=str(row["order_id"]),
                value=json.dumps(row_to_message(row)),
                on_delivery=on_delivery,
            )
        except BufferError:
            producer.poll(1)
            producer.produce(
                topic,
                key=str(row["order_id"]),
                value=json.dumps(row_to_message(row)),
                on_delivery=on_delivery,
            )

        producer.poll(0)
        published += 1

        if published % 500 == 0:
            print(f"[SEND] {published}/{total_rows} orders published...")

        if delay > 0:
            time.sleep(delay)

    producer.flush()
    return published


def main() -> None:
    print("[INFO] Loading CSV files...")
    orders, items, products = load_source_data()
    print(f"[INFO] orders   : {len(orders)} rows")
    print(f"[INFO] items    : {len(items)} rows")
    print(f"[INFO] products : {len(products)} rows")

    df = build_orders_dataframe(orders, items, products)
    print(f"[INFO] {len(df)} orders ready to publish")

    producer = Producer({"bootstrap.servers": BOOTSTRAP})
    published = publish_dataframe(df, producer)
    print(f"[INFO] Completed: {published} orders published to {TOPIC}")


if __name__ == "__main__":
    main()
