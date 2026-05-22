import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from confluent_kafka import Consumer, KafkaError

BOOTSTRAP = "localhost:9092"
TOPIC = "ecommerce-orders"
OUTPUT = Path(__file__).resolve().parents[1] / "output" / "stats.json"
FLUSH_EVERY = 50


def make_category_stats() -> defaultdict:
    return defaultdict(
        lambda: {
            "nb_commandes": 0,
            "ca_total": 0.0,
            "ca_max": 0.0,
        }
    )


def make_hour_stats() -> defaultdict:
    return defaultdict(
        lambda: {
            "nb_commandes": 0,
            "ca_total": 0.0,
        }
    )


def parse_message(payload: bytes) -> dict:
    return json.loads(payload.decode("utf-8"))


def extract_hour(timestamp: str) -> str:
    return timestamp[:13] if timestamp else "inconnu"


def process_order(
    data: dict,
    stats_cat: defaultdict,
    stats_hour: defaultdict,
    totals: dict,
) -> None:
    """Update in-memory aggregates from one decoded Kafka message."""
    category = data.get("category", "autre")
    total = float(data.get("total", 0.0))
    hour = extract_hour(data.get("timestamp", ""))

    stats_cat[category]["nb_commandes"] += 1
    stats_cat[category]["ca_total"] += total
    if total > stats_cat[category]["ca_max"]:
        stats_cat[category]["ca_max"] = total

    stats_hour[hour]["nb_commandes"] += 1
    stats_hour[hour]["ca_total"] += total

    totals["total_traite"] += 1
    totals["ca_global"] += total
    if total > totals["commande_max"]:
        totals["commande_max"] = total


def build_output_payload(
    stats_cat: defaultdict,
    stats_hour: defaultdict,
    totals: dict,
) -> dict:
    categories = [
        {
            "categorie": category,
            "nb_commandes": values["nb_commandes"],
            "ca_total": round(values["ca_total"], 2),
            "panier_moyen": round(values["ca_total"] / values["nb_commandes"], 2),
            "ca_max": round(values["ca_max"], 2),
        }
        for category, values in sorted(
            stats_cat.items(),
            key=lambda item: -item[1]["ca_total"],
        )
    ]

    evolution = [
        {
            "heure": hour,
            "nb_commandes": values["nb_commandes"],
            "ca_total": round(values["ca_total"], 2),
        }
        for hour, values in sorted(stats_hour.items())
    ]

    total_orders = totals["total_traite"]
    revenue = totals["ca_global"]
    return {
        "mise_a_jour": datetime.now().strftime("%H:%M:%S"),
        "total_commandes": total_orders,
        "ca_global": round(revenue, 2),
        "panier_moyen_global": round(revenue / total_orders, 2) if total_orders else 0,
        "commande_max": round(totals["commande_max"], 2),
        "categories": categories,
        "evolution": evolution,
    }


def save_stats(
    stats_cat: defaultdict,
    stats_hour: defaultdict,
    totals: dict,
    output_path: Path = OUTPUT,
) -> dict:
    """Write the current aggregates to disk and return the serialized payload."""
    payload = build_output_payload(stats_cat, stats_hour, totals)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    print(f"[SAVE] {totals['total_traite']} orders - total revenue: R${totals['ca_global']:,.2f}")
    return payload


def create_consumer(bootstrap: str = BOOTSTRAP, topic: str = TOPIC) -> Consumer:
    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap,
            "group.id": "processeur-ecommerce",
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([topic])
    return consumer


def run_consumer(
    consumer: Consumer,
    output_path: Path = OUTPUT,
    flush_every: int = FLUSH_EVERY,
) -> None:
    stats_cat = make_category_stats()
    stats_hour = make_hour_stats()
    totals = {
        "total_traite": 0,
        "ca_global": 0.0,
        "commande_max": 0.0,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Processor started - listening on {TOPIC} - Ctrl+C to stop")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"[ERROR] {msg.error()}")
                continue

            process_order(parse_message(msg.value()), stats_cat, stats_hour, totals)

            if totals["total_traite"] % flush_every == 0:
                save_stats(stats_cat, stats_hour, totals, output_path)

    except KeyboardInterrupt:
        print("\n[INFO] Processor stopping - final save...")
        save_stats(stats_cat, stats_hour, totals, output_path)
    finally:
        consumer.close()
        print("[INFO] Consumer closed.")


def main() -> None:
    consumer = create_consumer()
    run_consumer(consumer)


if __name__ == "__main__":
    main()
