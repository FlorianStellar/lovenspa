import unittest

from social.marque import charger
from social.s3_catalogue import offres as logements

MARQUE = charger("lovenspa")

class _M:
    """Marque de test : configuration Love'nSpa, règles d'exclusion réduites."""
    def __init__(self):
        self.catalogue = MARQUE.catalogue
        self.site = MARQUE.site
        self.regles = {"equipements_exclus_instagram": ["BDSM", "Sofa tantrique"],
                       "equipements_sans_interet": ["wifi", "ancv"]}


RULES = _M()

NODE = {
    "handle": "escale-spa-dinard", "title": "L'Escale Dinard", "status": "ACTIVE", "productType": "Gîte",
    "onlineStoreUrl": None,
    "tags": ["Equipements|Spa", "Equipements|Sauna", "Equipements|wifi", "Equipements|BDSM", "Equipements|Spa",
             "ville|Saint-Malo", "region|Bretagne", "Dinard"],
    "priceRangeV2": {"minVariantPrice": {"amount": "190.0", "currencyCode": "EUR"}},
    "mediaCount": {"count": 7}, "ville": {"value": " Tréméreuc "}, "region": None, "onAime": {"value": "  "}, "ambiance": {"value": "2"},
}


class TestTagValues(unittest.TestCase):
    def test_prefix_dedup_order(self):
        self.assertEqual(logements.tag_values(NODE["tags"], "Equipements"), ["Spa", "Sauna", "wifi", "BDSM"])

    def test_no_tags(self):
        self.assertEqual(logements.tag_values(None, "ville"), [])


class TestFiche(unittest.TestCase):
    def setUp(self):
        self.f = logements.offre(NODE, RULES)

    def test_excluded_and_noise_removed(self):
        self.assertEqual(self.f["equipements"], ["Spa", "Sauna"])
        self.assertEqual(self.f["equipements_non_citables"], ["BDSM"])

    def test_price_and_places(self):
        self.assertEqual(self.f["prix_a_partir_de"], 190.0)
        self.assertEqual(self.f["ville"], "Tréméreuc")
        self.assertEqual(self.f["ville_reference"], "Saint-Malo")
        self.assertEqual(self.f["region"], "Bretagne")  # repli sur le tag

    def test_ambiance(self):
        self.assertEqual(self.f["ambiance"], 2)
        self.assertEqual(self.f["ambiance_libelle"], "Sensuel")
        self.assertEqual(self.f["medias"], 7)
        self.assertEqual(self.f["unite_prix"], "la nuit")
        self.assertIsNone(logements.offre(dict(NODE, ambiance=None), RULES)["ambiance"])

    def test_empty_on_aime_is_none(self):
        self.assertIsNone(self.f["on_aime"])

    def test_url_fallback(self):
        self.assertEqual(self.f["url"], "https://www.lovenspa.fr/products/escale-spa-dinard")

    def test_no_private_fields(self):
        for k in ("email", "telephone", "adresse", "latitude"):
            self.assertNotIn(k, self.f)

    def test_missing_price(self):
        node = dict(NODE, priceRangeV2=None)
        self.assertIsNone(logements.offre(node, RULES)["prix_a_partir_de"])

    def test_none(self):
        self.assertIsNone(logements.offre(None, RULES))

    def test_real_rules_file_loads(self):
        r = MARQUE.regles
        self.assertIn("BDSM", r["equipements_exclus_instagram"])
        self.assertEqual(r["legende"]["max_hashtags"], 5)


if __name__ == "__main__":
    unittest.main()
