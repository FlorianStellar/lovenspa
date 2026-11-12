import unittest

from social.s6_controle import controle

OFFRE = {"nom": "Le Nid de l'Erdre", "description": "Piscine intérieure chauffée à 32 °C, lit 180 cm", "equipements": ["Spa"],
         "ville": "Nantes"}


class TestFaits(unittest.TestCase):
    def test_numbers_must_be_sourced(self):
        self.assertEqual(controle.chiffres_non_sources(["Une piscine à 32 °C", "Un lit de 180 cm"], [OFFRE]), [])
        self.assertEqual(controle.chiffres_non_sources(["Un écran de 3 mètres", "à 20 min de Nantes"], [OFFRE]),
                         ["3 mètres", "20 min"])

    def test_temps_fort(self):
        theme = "Offrir une nuit : la carte cadeau qui ne finit pas dans un tiroir"
        self.assertTrue(controle.evoque_temps_fort(theme, ["Une nuit à offrir avant Noël"]))
        self.assertFalse(controle.evoque_temps_fort(theme, ["Une piscine rien qu'à vous"]))
        self.assertTrue(controle.evoque_temps_fort(None, ["x"]))
        self.assertTrue(controle.evoque_temps_fort(theme, ["La carte cadeau est sur notre site"]))

    def test_verdict_status_coherent_and_theme_amount(self):
        o = dict(OFFRE, prix_a_partir_de=225.0, nom="Le Nid")
        case = {"moteur": "selection", "offres": [o], "theme": "6 nuits avec spa à moins de 150 €"}
        leg = ("6 nuits jusqu'à 150 €.\n\nLe Nid, dès 225 € la nuit. Un gîte au bord de l'eau, piscine et sauna. "
               "Une adresse pour deux, au calme, à deux pas de la ville et du fleuve.\n\nEnregistrez ce post.\n\n#lovenspa")
        v = controle.verdict({"case": case, "legende": leg, "medias": ["a"]})
        self.assertFalse(any(r["code"] == "AUTRE_MONTANT" for r in v["controle"]["resultats"]))
        leg2 = leg.replace("6 nuits jusqu'à 150 €.", "Dès 30 € par mois.")
        v = controle.verdict({"case": dict(case, theme=""), "legende": leg2, "medias": ["a"], "sources_montants": {"30": "https://x"}})
        self.assertFalse(any(r["code"] == "AUTRE_MONTANT" for r in v["controle"]["resultats"]))
        v = controle.verdict({"case": {"moteur": "recrutement", "offres": [o]}, "legende": "x", "medias": ["a"]})
        self.assertEqual(v["statut"] == "PRET", v["controle"]["statut"] != "REFUSE")

    def test_empreinte_ignores_review(self):
        c = {"legende": "a"}
        self.assertEqual(controle.empreinte(c), controle.empreinte({**c, "revue_visuelle": {"statut": "OK"}}))
        self.assertNotEqual(controle.empreinte(c), controle.empreinte({"legende": "b"}))

    def test_verdict_blocks_unsourced_figure(self):
        case = {"moteur": "lieu", "offres": [dict(OFFRE, prix_a_partir_de=225.0)]}
        v = controle.verdict({"case": case, "legende": "Le Nid de l'Erdre, dès 225 € la nuit. Lien en bio.",
                              "medias": ["a"], "textes_ecran": ["Un écran de 3 mètres"]})
        self.assertTrue(any("3 mètres" in b for b in v["bloquants"]))
        v = controle.verdict({"case": dict(case, moteur="couple"), "legende": "Le Nid de l'Erdre. Lien en bio.",
                              "medias": ["a"], "textes_ecran": ["Un message à 15 h"]})
        self.assertFalse(any("15 h" in b for b in v["bloquants"]))


if __name__ == "__main__":
    unittest.main()
