import unittest
from unittest import mock

from social.s7_diffusion import page_bio

O1 = {"handle": "a", "nom": "Le Nid - Spa", "ville": "Nantes", "prix_a_partir_de": 225.0, "unite_prix": "la nuit",
      "url": "https://x.fr/products/a"}
O2 = dict(O1, handle="b", nom="Alexis", ville="Toulon", url="https://x.fr/products/b")


def paquet(date, offres, lien):
    return {"case": {"date": date, "offres": offres, "lien": lien}}


class TestPageBio(unittest.TestCase):
    def test_entrees_dedup_and_tracked_links(self):
        e = page_bio.entrees([paquet("2026-11-22", [O1], "https://x.fr/products/a?utm_content=2026-11-22"),
                              paquet("2026-11-20", [], None),
                              paquet("2026-11-17", [O2, O1], "https://x.fr/sel?utm_content=2026-11-17")])
        self.assertEqual([x["nom"] for x in e], ["Le Nid", "Alexis"])
        self.assertTrue(e[0]["lien"].endswith("utm_content=2026-11-22"))
        self.assertEqual(e[1]["lien"], "https://x.fr/products/b?utm_content=2026-11-17")  # sélection : suivi conservé

    def test_html_escaped(self):
        h = page_bio.corps_html([{"nom": "A & <b>", "ville": None, "prix": 99.0, "unite": "la nuit", "lien": 'u"x'}])
        self.assertIn("A &amp; &lt;b&gt;", h)
        self.assertIn('href="u&quot;x"', h)
        self.assertIn("dès 99 € la nuit", h)
        h = page_bio.corps_html([], en_tete=[("Offrir une nuit", "https://x.fr/cc?utm=1")])
        self.assertTrue(h.startswith('<p><a href="https://x.fr/cc?utm=1"><strong>Offrir une nuit'))

    def test_create_unpublished_then_update(self):
        s = mock.Mock()
        s.gql.side_effect = [{"pages": {"nodes": []}},
                             {"pageCreate": {"page": {"id": "P1", "isPublished": False}, "userErrors": []}}]
        page_bio.ecrire_page(s, "instagram", "Instagram", "<p>x</p>")
        self.assertIs(s.gql.call_args_list[1][0][1]["p"]["isPublished"], False)
        s = mock.Mock()
        s.gql.side_effect = [{"pages": {"nodes": [{"id": "P1"}]}},
                             {"pageUpdate": {"page": {"id": "P1"}, "userErrors": []}}]
        page_bio.ecrire_page(s, "instagram", "Instagram", "<p>y</p>")
        self.assertNotIn("isPublished", s.gql.call_args_list[1][0][1]["p"])  # la publication reste une décision humaine

    def test_user_errors_raise(self):
        s = mock.Mock()
        s.gql.side_effect = [{"pages": {"nodes": []}}, {"pageCreate": {"page": None, "userErrors": [{"message": "x"}]}}]
        with self.assertRaises(RuntimeError):
            page_bio.ecrire_page(s, "instagram", "Instagram", "x")


if __name__ == "__main__":
    unittest.main()
