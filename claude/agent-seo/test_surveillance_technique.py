import unittest
import surveillance_technique as s

BASE = {"theme_id": "t1", "theme_name": "v4.1", "fichiers": {"layout/theme.liquid": "a", "assets/x.css": "b"},
        "robots": ["Disallow: /cart", "User-agent: *"], "sitemaps": {"https://lovenspa.fr/sitemap.xml": {"soumises": 1000, "erreurs": 0}}}
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
        al, _ = s.comparer(BASE, copie(robots=["Disallow: /", "User-agent: *"]), {}, {})
        self.assertTrue(al[0].startswith("robots.txt modifié"))
        self.assertEqual(s.robots_regles("# x\nUser-agent: *\nDisallow: /cart\n\nSitemap: s"),
                         ["Disallow: /cart", "Sitemap: s", "User-agent: *"])

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
        cur, cont = s.collecter(A(), G(), lambda u: "User-agent: *\nDisallow: /cart")
        self.assertEqual(len(cur["fichiers"]), 2)
        self.assertEqual(cur["sitemaps"]["sm"], {"soumises": 15, "erreurs": 0})
        self.assertIn("layout/theme.liquid", cont)


if __name__ == "__main__":
    unittest.main()
