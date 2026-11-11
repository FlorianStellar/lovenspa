import unittest
import surveillance_technique as s

BASE = {"theme_id": "t1", "theme_name": "v4.1", "fichiers": {"layout/theme.liquid": "a", "assets/x.css": "b"},
        "robots": ["* | disallow: /cart"], "html": {}, "sitemaps": {"https://lovenspa.fr/sitemap.xml": {"soumises": 1000, "erreurs": 0}}}
HEAD = '<link rel="canonical" href="x"><meta name="description" content="d"><script type="application/ld+json">{}</script>'


def copie(**kw):
    import copy
    d = copy.deepcopy(BASE); d.update(kw); return d


class T(unittest.TestCase):
    def test_sensibles(self):
        for f in ("layout/theme.liquid", "snippets/lovenspa-article-jsonld.liquid", "snippets/meta-tags.liquid", "templates/robots.txt.liquid"):
            self.assertTrue(s.SENSIBLES.match(f), f)
        for f in ("assets/x.css", "sections/footer.liquid", "snippets/icon-cart.liquid", "snippets/header-icons.liquid", "snippets/host-heading.liquid"):
            self.assertFalse(s.SENSIBLES.match(f), f)
        for f in ("sections/footer.liquid", "templates/product.json", "config/settings_data.json"):
            self.assertTrue(s.SURVEILLES.match(f), f)

    def test_rien(self):
        self.assertEqual(s.comparer(BASE, copie(), {}, {}), ([], []))

    def test_asset_modifie_info_seulement(self):
        cur = copie(fichiers={"layout/theme.liquid": "a", "assets/x.css": "c"})
        al, inf = s.comparer(BASE, cur, {}, {})
        self.assertEqual(al, []); self.assertEqual(inf, ["modifié : assets/x.css"])

    def test_noindex_ajoute_et_canonical_retire(self):
        cur = copie(fichiers={"layout/theme.liquid": "z", "assets/x.css": "b"})
        al, _ = s.comparer(BASE, cur, {"layout/theme.liquid": HEAD},
                           {"layout/theme.liquid": '<meta name="robots" content="noindex"><meta name="description" content="d"><script type="application/ld+json">{}</script>'})
        self.assertIn("modifié : layout/theme.liquid", al)
        self.assertTrue(any("noindex ajouté" in a for a in al))
        self.assertTrue(any("canonical retiré" in a for a in al))

    def test_changement_theme_live(self):
        al, _ = s.comparer(BASE, copie(theme_id="t2", theme_name="v5"), {}, {})
        self.assertEqual(al, ["thème live changé : v4.1 → v5"])

    def test_robots(self):
        al, _ = s.comparer(BASE, copie(robots=["* | disallow: /"]), {}, {})
        self.assertTrue(al[0].startswith("robots.txt modifié"))
        txt = "# x\nUser-agent: *\nDisallow: /cart\n\nUser-agent: Googlebot\nUser-agent: Bingbot\nDisallow: /x\nSitemap: s"
        self.assertEqual(s.robots_regles(txt), ["* | Sitemap: s", "* | disallow: /cart", "Bingbot | disallow: /x", "Googlebot | disallow: /x"])
        # même règle déplacée d'un groupe à l'autre = détectée
        self.assertNotEqual(s.robots_regles("User-agent: *\nDisallow: /x"), s.robots_regles("User-agent: Googlebot\nDisallow: /x"))

    def test_robots_non_lu_info(self):
        al, inf = s.comparer(BASE, copie(robots=None), {}, {})
        self.assertEqual(al, []); self.assertTrue(inf[0].startswith("robots.txt non lu"))

    def test_section_surveillee_motifs_seulement(self):
        prec = copie(fichiers={**BASE["fichiers"], "sections/main.liquid": "1", "templates/product.json": "1"})
        cur = copie(fichiers={**BASE["fichiers"], "sections/main.liquid": "2", "templates/product.json": "2"})
        al, inf = s.comparer(prec, cur, {"sections/main.liquid": HEAD, "templates/product.json": "{}"},
                             {"sections/main.liquid": HEAD, "templates/product.json": '{"x":"noindex"}'})
        self.assertEqual(al, ["templates/product.json: noindex ajouté (0→1)"])
        self.assertEqual(len(inf), 2)

    def test_sitemap_retire(self):
        al, _ = s.comparer(BASE, copie(sitemaps={}), {}, {})
        self.assertEqual(al, ["sitemap retiré de GSC : https://lovenspa.fr/sitemap.xml"])

    def test_lire_html_et_comparaison(self):
        h = s.lire_html('<meta name="robots" content="index,follow">' + HEAD, {}, 200)
        self.assertEqual((h["canonical"], h["ld_json"], h["description"]), ("x", 1, True))
        n = s.lire_html('<meta name="robots" content="noindex">', {"X-Robots-Tag": ""}, 200)
        prec, cur = copie(html={"u": h}), copie(html={"u": n})
        al, _ = s.comparer(prec, cur, {}, {})
        self.assertEqual(len(al), 4)  # noindex, canonical, JSON-LD, description
        al, inf = s.comparer(prec, copie(html={"u": None}), {}, {})
        self.assertEqual((al, inf), ([], ["HTML non lu : u"]))
        self.assertTrue(any("HTTP 301" in a for a in s.comparer(prec, copie(html={"u": {**h, "statut": 301}}), {}, {})[0]))

    def test_page_get_anti_robot(self):
        import requests
        from unittest import mock
        class R:
            def __init__(self, t, c=200): self.text, self.status_code, self.headers = t, c, {}
        seq = [R("Just a moment..."), R("", 429), R("User-agent: *\nDisallow: /cart")]
        with mock.patch.object(requests, "get", side_effect=seq), mock.patch("time.sleep"):
            self.assertEqual(s.http_get("u"), "User-agent: *\nDisallow: /cart")
        with mock.patch.object(requests, "get", side_effect=requests.ConnectionError()), mock.patch("time.sleep"):
            self.assertIsNone(s.http_get("u"))

    def test_sitemap_baisse_et_erreurs(self):
        al, _ = s.comparer(BASE, copie(sitemaps={"https://lovenspa.fr/sitemap.xml": {"soumises": 800, "erreurs": 2}}), {}, {})
        self.assertEqual(len(al), 2)

    def test_collecter_pagination(self):
        class A:
            def gql(self, q, v=None):
                if "roles" in q: return {"themes": {"nodes": [{"id": "t", "name": "n"}]}}
                if "filenames" in q: return {"theme": {"files": {"nodes": [{"filename": "layout/theme.liquid", "body": {"content": HEAD}}]}}}
                if v.get("after") is None:
                    return {"theme": {"files": {"nodes": [{"filename": "layout/theme.liquid", "checksumMd5": "a"}], "pageInfo": {"hasNextPage": True, "endCursor": "c"}}}}
                return {"theme": {"files": {"nodes": [{"filename": "assets/x.css", "checksumMd5": "b"}], "pageInfo": {"hasNextPage": False, "endCursor": None}}}}
        class G:
            def list_sitemaps(self): return [{"path": "sm", "errors": "0", "contents": [{"submitted": "10"}, {"submitted": "5"}]}]
        cur, cont = s.collecter(A(), G(), lambda u: "User-agent: *\nDisallow: /cart", ["p"], lambda u: (HEAD, {}, 200))
        self.assertEqual(cur["html"]["p"]["ld_json"], 1)
        self.assertEqual(len(cur["fichiers"]), 2)
        self.assertEqual(cur["sitemaps"]["sm"], {"soumises": 15, "erreurs": 0})
        self.assertIn("layout/theme.liquid", cont)


if __name__ == "__main__":
    unittest.main()
