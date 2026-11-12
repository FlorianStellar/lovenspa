"""Tests demandés par le contrôle qualité de J2 : fonctions sans test direct, nouveaux contrôles,
chaîne de bout en bout S4 -> S5 -> S6 -> S7 en simulation."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime
from unittest import mock

from PIL import Image

from social.connecteurs.instagram import IGClient, IGError
from social.contrats.valider import erreurs
from social.marque import Marque, charger
from social.s3_catalogue import offres
from social.s4_planification import planifier
from social.s5_production import produire, visuels
from social.s6_controle import controle
from social.s7_diffusion import instagram as diffusion
from social.tests.test_ig_client import FakeResp, FakeSession

M = charger("lovenspa")
PHOTO = Image.new("RGB", (1024, 756), (90, 60, 120))


class TestMarque(unittest.TestCase):
    def test_accessors(self):
        self.assertTrue(M.site.startswith("https://"))
        self.assertEqual(M.couleur("accent"), (0xE8, 0x3F, 0x4E))
        self.assertTrue(os.path.exists(M.police("titre")))
        self.assertEqual(M.compte("instagram")["username"], "lovenspa.fr")
        self.assertIn("abracadaroom", M.comptes_reference("instagram"))
        self.assertIn("couleurs", M.kit)

    def test_env_first_found(self):
        with mock.patch.dict(os.environ, {"B": "2"}, clear=True):
            self.assertEqual(M.env(["A", "B"]), "2")
            self.assertIsNone(M.env("A"))

    def test_donnees_creates_folder(self):
        with tempfile.TemporaryDirectory() as d, mock.patch("social.marque.DONNEES", d):
            p = M.donnees("instagram", "plans")
            self.assertTrue(os.path.isdir(p))
            f = M.donnees("instagram", "x.json")
            self.assertTrue(os.path.isdir(os.path.dirname(f)))

    def test_unknown_brand_and_no_default(self):
        with self.assertRaises(FileNotFoundError):
            Marque("inexistante")
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(ValueError):
            charger(None)


class TestCatalogueHelpers(unittest.TestCase):
    def test_champs_gql(self):
        q = offres.champs_gql(M)
        self.assertIn('ambiance: metafield(namespace: "custom", key: "spicy_level")', q)
        self.assertEqual(offres._champ_gql("x", {"tag": "ville"}), "")

    def test_valeur(self):
        node = {"tags": ["region|Bretagne"], "a": {"value": " 3 "}, "b": {"value": "x"}}
        self.assertEqual(offres._valeur(node, "r", {"metafield": "n.k", "repli_tag": "region"}), "Bretagne")
        self.assertEqual(offres._valeur(node, "a", {"metafield": "n.k", "type": "int"}), 3)
        self.assertIsNone(offres._valeur(node, "b", {"metafield": "n.k", "type": "int"}))

    def test_toutes_paginates(self):
        node = {"handle": "a", "title": "A", "status": "ACTIVE", "tags": []}
        pages = [{"products": {"pageInfo": {"hasNextPage": True, "endCursor": "c"}, "nodes": [node]}},
                 {"products": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [dict(node, handle="b")]}}]
        con = mock.Mock(gql=mock.Mock(side_effect=pages))
        res = offres.Catalogue(M, connecteur=con).toutes(pause=0)
        self.assertEqual([r["handle"] for r in res], ["a", "b"])
        self.assertEqual(con.gql.call_args_list[1].args[1], {"a": "c"})

    def test_images(self):
        data = {"products": {"nodes": [{"handle": "a", "media": {"nodes": [{"image": {"url": "u1"}}, {}, {"image": {"url": "u2"}}]}}]}}
        cat = offres.Catalogue(M, connecteur=mock.Mock(gql=mock.Mock(return_value=data)))
        self.assertEqual(cat.images("a"), ["u1", "u2"])
        self.assertEqual(cat.images("z"), [])


class TestPlanHelpers(unittest.TestCase):
    def test_score_prefers_more_flagship_equipment(self):
        strat = M.strategie("instagram")
        a = {"handle": "a", "equipements": ["Spa", "Sauna", "Hammam"]}
        b = {"handle": "b", "equipements": ["Spa"]}
        self.assertGreater(planifier.score(a, strat, 1), planifier.score(b, strat, 1))

    def test_load_json_default(self):
        self.assertEqual(planifier.load_json("/nonexistent.json", []), [])


class TestProductionHelpers(unittest.TestCase):
    def test_lieu_and_nom(self):
        self.assertEqual(produire.lieu_txt({"ville": "Tréméreuc", "ville_reference": "Saint-Malo"}), "Tréméreuc · près de Saint-Malo")
        self.assertEqual(produire.lieu_txt({"ville": "Vannes", "ville_reference": "Vannes"}), "Vannes")
        self.assertEqual(produire.nom_court({"nom": "Le Nid - Spa"}), "Le Nid")

    def test_text_block_advances(self):
        visuels.appliquer_kit(M)
        im = Image.new("RGB", (1080, 1350))
        y = visuels.text_block(im, [("Un titre", visuels.font("Bold", 60))], 80, 100, 900)
        self.assertGreater(y, 160)


class TestNewChecks(unittest.TestCase):
    BASE = "Spa privatif à Vannes : Le Nid, dès 150 € la nuit.\n\nEnregistrez ce post.\n\n#lovenspa"
    OFFRE = {"nom": "Le Nid - Spa", "ville": "Vannes", "ville_reference": None, "prix_a_partir_de": 150.0,
             "equipements": ["Spa"], "equipements_non_citables": [], "ambiance": 1}

    def codes(self, r):
        return {x["code"] for x in r["resultats"]}

    def test_explicite_blocks(self):
        r = controle.check(self.BASE.replace("Spa privatif", "Soirée érotique et spa"), self.OFFRE, [], M.regles)
        self.assertIn("EXPLICITE", self.codes(r))
        self.assertEqual(r["statut"], "REFUSE")

    def test_emoji_warns(self):
        r = controle.check(self.BASE.replace("Enregistrez", "🌹🫧 Enregistrez"), self.OFFRE, [], M.regles)
        self.assertIn("EMOJI", self.codes(r))
        self.assertEqual(controle.emojis_in("❤️ ok 🌹"), 2)

    def test_ambiance_blocks_in_verdict(self):
        case = {"date": "2026-11-16", "heure": "18:30", "plateforme": "instagram", "moteur": "lieu", "format": "REELS",
                "statut": "A_PRODUIRE", "offres": [dict(self.OFFRE, ambiance=3)]}
        v = controle.verdict({"case": case, "legende": self.BASE, "medias": ["a"]}, M.regles, [], [1, 2])
        self.assertEqual(v["statut"], "REFUSE")
        self.assertTrue(any("ambiance" in b for b in v["bloquants"]))


class TestDiffusionHelpers(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(diffusion.time, "sleep", lambda s: None)
        p.start()
        self.addCleanup(p.stop)

    def test_echeance_paris(self):
        e = diffusion.echeance({"date": "2026-11-16", "heure": "18:30"})
        self.assertEqual((e.hour, e.minute, str(e.tzinfo)), (18, 30, "Europe/Paris"))

    def test_attendre_conteneur(self):
        seq = [FakeResp(200, {"status_code": "IN_PROGRESS"}), FakeResp(200, {"status_code": "FINISHED"})]
        ig = IGClient("1", session=FakeSession([(lambda u, p: True, lambda u, p: seq.pop(0))]), version="")
        diffusion.attendre_conteneur(ig, "c1")
        ig2 = IGClient("1", session=FakeSession([(lambda u, p: True, FakeResp(200, {"status_code": "EXPIRED"}))]), version="")
        with self.assertRaises(IGError):
            diffusion.attendre_conteneur(ig2, "c1")

    def test_quota(self):
        ok = FakeResp(200, {"data": [{"quota_usage": 3, "config": {"quota_total": 100}}]})
        full = FakeResp(200, {"data": [{"quota_usage": 100, "config": {"quota_total": 100}}]})
        self.assertTrue(diffusion.quota_ok(IGClient("1", session=FakeSession([(lambda u, p: True, ok)]), version="")))
        self.assertFalse(diffusion.quota_ok(IGClient("1", session=FakeSession([(lambda u, p: True, full)]), version="")))

    def test_charger_pret(self):
        with tempfile.TemporaryDirectory() as d:
            for n, o in (("paquet.json", {"case": {}, "legende": "L", "medias": ["m"]}),
                         ("verdict.json", {"statut": "REFUSE", "bloquants": ["x"], "controle": {"resultats": []}})):
                with open(os.path.join(d, n), "w") as f:
                    json.dump(o, f)
            p = diffusion.charger_pret(d)
        self.assertEqual((p["statut"], p["bloquants"], p["legende"]), ("REFUSE", ["x"], "L"))


class TestConnecteurInstagram(unittest.TestCase):
    def test_ensure_user_uses_brand_account(self):
        pages = {"data": [{"instagram_business_account": {"id": "9", "username": "lovenspa.fr"}}]}
        c = IGClient(session=FakeSession([(lambda u, p: u.endswith("me/accounts"), FakeResp(200, pages))]),
                     version="", marque=M)
        c.user_id = None
        self.assertEqual(c.ensure_user(), "9")


class TestBoutEnBoutSimulation(unittest.TestCase):
    """S4 plan -> S5 paquet -> S6 verdict -> S7 refus (moteur non validé, J4) puis simulation une fois validé."""

    def test_chain(self):
        strat = M.strategie("instagram")
        nodes = [{"handle": f"o{i}", "title": f"Le Refuge {i} - Spa", "status": "ACTIVE", "productType": "Gîte",
                  "onlineStoreUrl": None, "tags": ["Equipements|Spa", "Equipements|Sauna", f"region|{r}", "ville|Ville"],
                  "priceRangeV2": {"minVariantPrice": {"amount": "150.0", "currencyCode": "EUR"}},
                  "mediaCount": {"count": 6}, "ville": {"value": "Ville"}, "ambiance": {"value": "1"}}
                 for i, r in enumerate(list(strat["regions_poids"]) * 8)]
        cat = [offres.offre(n, M) for n in nodes]
        plan = planifier.plan_week(date(2026, 11, 16), cat, [], strat, site=M.site)
        self.assertEqual(erreurs(plan, "plan"), [])
        case = next(c for c in plan["cases"] if c["moteur"] == "lieu")
        o = case["offres"][0]
        legende = (f"Spa et sauna à {o['ville']} : {produire.nom_court(o)}, dès 150 € la nuit.\n\n"
                   "Un gîte pour deux, le spa rien qu'à vous et le sauna qui chauffe pendant le dîner. "
                   "Vous arrivez quand vous voulez et la soirée vous appartient du début à la fin, sans voisins.\n\n"
                   "Enregistrez ce post pour votre prochain week-end.\n\n#lovenspa")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "contenu.json"), "w", encoding="utf-8") as f:
                json.dump({"case": case, "legende": legende, "reel_lignes": ["a", "b", "c"]}, f)
            catm = mock.Mock(images=mock.Mock(return_value=["u1", "u2", "u3"]))
            with mock.patch.object(visuels, "fetch", return_value=PHOTO), \
                    mock.patch.object(visuels, "render_reel", side_effect=lambda fr, out, **k: out), \
                    mock.patch.object(visuels, "probe", return_value={"streams": [{"codec_type": "video", "width": 1080,
                                                                                      "height": 1920}],
                                                                         "format": {"duration": "7.5"}}):
                paquet, verdict = produire.produce(d, marque=M, catalogue=catm)
                # sans revue visuelle : refusé ; revue inscrite sur cette version du contenu : prêt
                self.assertEqual(verdict["statut"], "REFUSE")
                with open(os.path.join(d, "contenu.json"), encoding="utf-8") as f:
                    contenu = json.load(f)
                contenu["revue_visuelle"] = {"statut": "OK", "empreinte": controle.empreinte(contenu)}
                with open(os.path.join(d, "contenu.json"), "w", encoding="utf-8") as f:
                    json.dump(contenu, f)
                paquet, verdict = produire.produce(d, marque=M, catalogue=catm)
            self.assertEqual(verdict["statut"], "PRET", verdict["bloquants"])
            marque = mock.Mock(donnees=mock.Mock(return_value=d), strategie=mock.Mock(return_value=strat))
            now = datetime(2026, 11, 16, 19, tzinfo=diffusion.PARIS)
            with mock.patch.dict(os.environ, {"IG_PUBLICATION_ACTIVE": "1"}):
                r = diffusion.traiter(d, marque, go=False, now=now)
                self.assertTrue(any("J4" in x for x in r["raisons"]))
                marque.strategie.return_value = dict(strat, moteurs_valides=["lieu"])
                r = diffusion.traiter(d, marque, go=False, now=now)
            self.assertEqual(r["raisons"], ["simulation (--go absent)"])


class TestMains(unittest.TestCase):
    def test_offres_main_one(self):
        with mock.patch.object(offres.Catalogue, "une", return_value={"handle": "x"}), \
                mock.patch.object(offres, "Shopify"), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(offres.main(["x", "--marque", "lovenspa"]), 0)
        self.assertIn('"handle": "x"', out.getvalue())

    def test_diffusion_main_dues_stops_without_switch(self):
        with redirect_stdout(io.StringIO()) as out:
            code = diffusion.main(["--dues", "--marque", "lovenspa"])
        self.assertEqual(code, 0)
        self.assertTrue(all('"publie": false' in l for l in out.getvalue().splitlines() if l))


if __name__ == "__main__":
    unittest.main()
