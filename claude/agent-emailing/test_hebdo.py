import json
from hebdo import libelle_nuits, prix_min, construire
from render import render
def test_libelle(): assert libelle_nuits({"2026-11-14": 1, "2026-11-13": 1}) == "Libre vendredi 13 et samedi 14"
def test_prix_min(): assert prix_min({"a": 31900, "b": 25850}) == 258
def test_construire_et_rendu(tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"dates": ["2026-11-13", "2026-11-14"], "choix": [
        {"titre": f"R{i}", "ville": "V", "handle": f"h{i}", "image": "https://x/i.jpg?v=1", "libres": {"2026-11-13": 10000}} for i in range(6)]}))
    e = construire(str(p), "mardi 10 novembre à 10 h")
    h = render(e)
    assert h.count("€ la nuit") == 6 and "Libre vendredi 13" in h and "{% unsubscribe_link %}" in h and "width=480" in h
def test_cta_apres_les_rooms(tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"dates": ["2026-11-13", "2026-11-14"], "choix": [
        {"titre": f"R{i}", "ville": "V", "handle": f"h{i}", "image": "x", "libres": {"2026-11-13": 10000}} for i in range(6)]}))
    h = render(construire(str(p), "x"))
    assert h.index("R5") < h.index("Voir toutes les dispos") and h.count("Voir toutes les dispos") == 1
