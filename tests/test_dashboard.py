import json

from dashboard.dashboard import load_data


def test_load_data_returns_none_when_file_missing(tmp_path):
    result, meta = load_data(tmp_path / "missing.json")

    assert result is None
    assert meta is None


def test_load_data_parses_expected_shapes(tmp_path):
    stats_file = tmp_path / "stats.json"
    stats_file.write_text(
        json.dumps(
            {
                "mise_a_jour": "12:00:00",
                "total_commandes": 2,
                "ca_global": 99.5,
                "panier_moyen_global": 49.75,
                "commande_max": 70.0,
                "categories": [
                    {
                        "categorie": "books",
                        "nb_commandes": 2,
                        "ca_total": 99.5,
                        "panier_moyen": 49.75,
                        "ca_max": 70.0,
                    }
                ],
                "evolution": [{"heure": "2017-10-02 10", "nb_commandes": 2, "ca_total": 99.5}],
            }
        ),
        encoding="utf-8",
    )

    result, meta = load_data(stats_file)
    df_cat, df_evo = result

    assert meta["mise_a_jour"] == "12:00:00"
    assert len(df_cat) == 1
    assert len(df_evo) == 1


def test_load_data_handles_invalid_json(tmp_path):
    stats_file = tmp_path / "stats.json"
    stats_file.write_text("{", encoding="utf-8")

    result, meta = load_data(stats_file)
    df_cat, df_evo = result

    assert df_cat.empty
    assert df_evo.empty
    assert meta["mise_a_jour"] == "Calcul en cours..."
