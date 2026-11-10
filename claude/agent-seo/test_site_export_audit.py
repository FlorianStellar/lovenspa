import csv
import tempfile
import unittest
from pathlib import Path

import site_audit as sa
import site_export as se


class TestExportParsing(unittest.TestCase):
    def test_to_path(self):
        self.assertEqual(se.to_path("https://www.lovenspa.fr/collections/love-room/"), "/collections/love-room")
        self.assertEqual(se.to_path("/collections/paris/products/la-suite"), "/products/la-suite")
        self.assertEqual(se.to_path("/pages/guide%C2%A0"), "/pages/guide ")
        self.assertIsNone(se.to_path("https://autre.fr/x"))
        self.assertIsNone(se.to_path("mailto:a@b.c"))
        self.assertIsNone(se.to_path("/cart"))
        self.assertIsNone(se.to_path("relative/path"))
        self.assertEqual(se.to_path("https://lovenspa.myshopify.com/pages/a"), "/pages/a")

    def test_body_links_and_words(self):
        html = '<p>Voir <a href="/collections/love-room">love room</a> et <a href="https://x.com">x</a></p>'
        self.assertEqual(se.body_links(html), [("/collections/love-room", "love room")])
        self.assertEqual(se.word_count(html), 5)
        self.assertEqual(se.body_links(""), [])

    def test_split_bulk(self):
        roots, ch = se.split_bulk([{"id": "c1"}, {"id": "p1", "__parentId": "c1"}, {"id": "p2", "__parentId": "c1"}])
        self.assertEqual([r["id"] for r in roots], ["c1"])
        self.assertEqual(len(ch["c1"]), 2)

    def test_menu_links(self):
        m = [{"handle": "main", "items": [{"title": "Love rooms", "url": "/collections/love-room",
                                           "items": [{"title": "Paris", "url": "https://lovenspa.fr/collections/paris"}]}]}]
        self.assertEqual([x["cible"] for x in se.menu_links(m)], ["/collections/love-room", "/collections/paris"])

    def test_page_row(self):
        r = se.page_row("product", {"handle": "a", "title": "A", "status": "ACTIVE", "onlineStoreUrl": "https://x",
                                     "descriptionHtml": "<p>un deux</p>", "seo": {"title": "T", "description": None}})
        self.assertEqual((r["url"], r["publie"], r["seo_title"], r["seo_description"], r["mots"]), ("/products/a", True, "T", "", 2))
        r = se.page_row("collection", {"handle": "c", "title": "C", "onlineStore": False, "descriptionHtml": ""})
        self.assertFalse(r["publie"])
        r = se.page_row("article", {"handle": "b", "title": "B", "isPublished": False, "blog": {"handle": "magazine"}, "body": ""})
        self.assertEqual((r["url"], r["publie"]), ("/blogs/magazine/b", False))


class TestResolve(unittest.TestCase):
    PUB = {"/collections/paris", "/products/a"}
    ALL = PUB | {"/products/brouillon"}
    RED = {"/collections/love-room-paris": "/collections/paris", "/a": "/b", "/b": "/a"}

    def r(self, t):
        return sa.resolve(t, self.PUB, self.ALL, self.RED, {"magazine"})

    def test_cases(self):
        self.assertEqual(self.r("/products/a"), ("ok", "/products/a"))
        self.assertEqual(self.r("/collections/love-room-paris"), ("redirection", "/collections/paris"))
        self.assertEqual(self.r("/products/brouillon")[0], "non_publiee")
        self.assertEqual(self.r("/products/supprimee")[0], "introuvable")
        self.assertEqual(self.r("/blogs/magazine/tagged/couple")[0], "ok")
        self.assertEqual(self.r("/policies/x")[0], "hors_perimetre")
        self.assertEqual(self.r("/collections/all")[0], "ok")
        self.assertEqual(self.r("/collections/paris/Equipements|Spa")[0], "ok")
        self.assertEqual(self.r("/collections/inconnue/tag")[0], "introuvable")
        self.assertEqual(self.r("/Products/A"), ("ok", "/products/a"))
        self.assertEqual(self.r("/a")[0], "hors_perimetre")  # boucle de redirection bornée


def write(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


class TestAuditE2E(unittest.TestCase):
    COLS = ["type", "handle", "url", "publie", "statut_shopify", "titre", "seo_title", "seo_description", "gabarit", "maj", "mots", "hash_body"]

    def page(self, url, typ, pub=True, title="", desc="", mots=500, h="x"):
        return {"type": typ, "handle": url.split("/")[-1], "url": url, "publie": pub, "statut_shopify": "", "titre": "T",
                "seo_title": title, "seo_description": desc, "gabarit": "", "maj": "", "mots": mots, "hash_body": h}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.new, self.old = d / "new", d / "old"
        for x in (self.new, self.old):
            x.mkdir()
        desc = "Une description assez longue pour passer le seuil minimal de soixante-dix caracteres sans souci."
        pages = [self.page("/collections/paris", "collection", title="Love room Paris", desc=desc, mots=50),
                 self.page("/products/a", "product", title="Doublon", desc=desc),
                 self.page("/products/b", "product", title="Doublon", desc=desc),
                 self.page("/pages/guide", "page", title="Guide", desc="")]
        write(self.new / "pages.csv", pages, self.COLS)
        write(self.old / "pages.csv", pages[:2] + [{**pages[3], "hash_body": "y"}], self.COLS)
        write(self.new / "liens.csv", [
            {"source": "/pages/guide", "cible": "/collections/love-room-paris", "ancre": "love room Paris", "emplacement": "body"},
            {"source": "/pages/guide", "cible": "/products/disparue", "ancre": "ici", "emplacement": "body"},
            {"source": "menu:main", "cible": "/pages/guide", "ancre": "Guide", "emplacement": "menu"}],
              ["source", "cible", "ancre", "emplacement"])
        write(self.new / "collection_produits.csv", [{"collection": "/collections/paris", "produit": "/products/a"}], ["collection", "produit"])
        write(self.new / "redirections.csv", [{"depuis": "/collections/love-room-paris", "vers": "/collections/paris"}], ["depuis", "vers"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_audit(self):
        s = sa.audit(str(self.new), str(self.old))
        self.assertEqual(s["liens_a_corriger"], {"redirection": 1, "introuvable": 1})
        self.assertEqual(s["sans_lien_entrant_par_type"], {"product": 1})  # /products/b
        self.assertEqual(s["metas"]["title_duplique"], 2)
        self.assertEqual(s["metas"]["description_absente"], 1)
        self.assertEqual(s["contenu_mince_par_type"], {"collection": 1})
        self.assertEqual(s["ancres_generiques"], 1)
        self.assertEqual(s["diff"], {"ajoutee": 1, "modifiee": 1})
        with open(self.new / "audit" / "liens_a_corriger.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual({(r["source"], r["verdict"], r["vers"]) for r in rows},
                         {("/pages/guide", "redirection", "/collections/paris"), ("/pages/guide", "introuvable", "")})


if __name__ == "__main__":
    unittest.main()
