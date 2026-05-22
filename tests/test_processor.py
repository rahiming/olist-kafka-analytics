import json

from processor.processor import (
    build_output_payload,
    extract_hour,
    make_category_stats,
    make_hour_stats,
    process_order,
    save_stats,
)


def test_process_order_updates_all_aggregates():
    stats_cat = make_category_stats()
    stats_hour = make_hour_stats()
    totals = {
        "total_traite": 0,
        "ca_global": 0.0,
        "commande_max": 0.0,
    }

    process_order(
        {
            "category": "books",
            "total": 42.5,
            "timestamp": "2017-10-02 10:56:33",
        },
        stats_cat,
        stats_hour,
        totals,
    )

    assert stats_cat["books"]["nb_commandes"] == 1
    assert stats_cat["books"]["ca_total"] == 42.5
    assert stats_cat["books"]["ca_max"] == 42.5
    assert stats_hour["2017-10-02 10"]["nb_commandes"] == 1
    assert totals == {
        "total_traite": 1,
        "ca_global": 42.5,
        "commande_max": 42.5,
    }


def test_extract_hour_handles_missing_timestamp():
    assert extract_hour("") == "inconnu"


def test_save_stats_writes_json_file(tmp_path):
    stats_cat = make_category_stats()
    stats_hour = make_hour_stats()
    totals = {
        "total_traite": 0,
        "ca_global": 0.0,
        "commande_max": 0.0,
    }

    process_order(
        {
            "category": "books",
            "total": 42.5,
            "timestamp": "2017-10-02 10:56:33",
        },
        stats_cat,
        stats_hour,
        totals,
    )

    output_file = tmp_path / "stats.json"
    payload = save_stats(stats_cat, stats_hour, totals, output_file)

    persisted = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload == persisted
    assert payload["categories"][0]["categorie"] == "books"


def test_build_output_payload_uses_zero_when_no_orders():
    payload = build_output_payload(
        make_category_stats(),
        make_hour_stats(),
        {
            "total_traite": 0,
            "ca_global": 0.0,
            "commande_max": 0.0,
        },
    )

    assert payload["panier_moyen_global"] == 0
