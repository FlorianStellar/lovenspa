import json
import os
import tempfile
import unittest
from unittest import mock

from PIL import Image, ImageDraw

from social.s5_production import produire
from social.s5_production import visuels
from social.marque import charger

MARQUE = charger("lovenspa")
visuels.appliquer_kit(MARQUE)

PHOTO = Image.new("RGB", (1024, 756), (120, 80, 160))


class TestImaging(unittest.TestCase):
    def test_cover_size_no_distortion(self):
        im = visuels.cover(PHOTO, (1080, 1350))
        self.assertEqual(im.size, (1080, 1350))

    def test_fit_on_blur_keeps_whole_photo(self):
        im = visuels.fit_on_blur(PHOTO, visuels.REEL)
        self.assertEqual(im.size, visuels.REEL)
        # la photo entière tient en largeur : 1080 x 797 au centre
        self.assertEqual(im.getpixel((540, 960)), (120, 80, 160))

    def test_wrap(self):
        d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        lines = visuels.wrap(d, "un deux trois quatre cinq six sept huit neuf dix", visuels.font("Bold", 60), 300)
        self.assertGreater(len(lines), 1)
        self.assertEqual(" ".join(lines), "un deux trois quatre cinq six sept huit neuf dix")

    def test_order_equipements(self):
        self.assertEqual(visuels.order_equipements(["Animaux", "Sauna", "Spa"], ["Spa", "Sauna"]), ["Spa", "Sauna", "Animaux"])

    def test_slides_sizes(self):
        for s in (visuels.slide_cover(PHOTO, "Titre", "Sous-titre", "1/3"),
                  visuels.slide_lodging(PHOTO, "Nom", "Ville", 150.0, ["Spa"], "2/3"),
                  visuels.slide_text("Titre", "Texte", "3/3", cta=True)):
            self.assertEqual(s.size, visuels.CAROUSEL)

    def test_text_is_dark_on_cream(self):
        """Régression J4 : titres de couverture et noms de logement étaient blancs sur fond crème."""
        def sombres(im, box):
            return sum(1 for p in im.crop(box).getdata() if sum(p) < 200)
        c = visuels.slide_cover(PHOTO, "Titre de couverture", "Sous-titre", "1/3")
        self.assertGreater(sombres(c, (80, 950, 1000, 1030)), 500)
        l = visuels.slide_lodging(PHOTO, "Nom du logement", "Ville", 150.0, ["Spa"], "2/3")
        self.assertGreater(sombres(l, (80, 945, 1000, 1000)), 500)

    def test_cta_slide_is_not_pink_flat(self):
        s = visuels.slide_text("T", "", cta=True)
        self.assertEqual(s.getpixel((1000, 100)), visuels.CREME)

    def test_reel_render(self):
        frames = [visuels.reel_frame(PHOTO, "Accroche", first=True), visuels.reel_frame(PHOTO, "")]
        with tempfile.TemporaryDirectory() as d:
            out = visuels.render_reel(frames, os.path.join(d, "r.mp4"), seconds=1.0)
            info = visuels.probe(out)
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        self.assertEqual((v["width"], v["height"]), (1080, 1920))
        self.assertTrue(any(s["codec_type"] == "audio" for s in info["streams"]))
        self.assertAlmostEqual(float(info["format"]["duration"]), 2.0, delta=0.2)

    def test_reel_text_inside_safe_zone(self):
        im = visuels.reel_frame(Image.new("RGB", (1024, 756), (0, 0, 0)), "Texte de fin assez long pour deux lignes")
        # sous la zone sûre, plus aucun pixel blanc du cartouche de texte
        bas = im.crop((0, visuels.ZONE_SURE_BAS + 2, 1080, 1920))
        self.assertNotIn((255, 255, 255), [p for p in bas.getdata()][::50])
        for x0 in (0, 1080 - visuels.MARGE_LATERALE + 1):  # marges latérales vides
            cote = im.crop((x0, 0, x0 + visuels.MARGE_LATERALE - 1, 1920))
            self.assertNotIn((255, 255, 255), list(cote.getdata())[::50])
        haut = visuels.reel_frame(Image.new("RGB", (1024, 756), (0, 0, 0)), "Accroche", first=True)
        self.assertNotIn((255, 255, 255), list(haut.crop((0, 0, 1080, visuels.ZONE_SURE_HAUT - 1)).getdata())[::50])

    def test_safe_zone_values(self):
        self.assertEqual((visuels.ZONE_SURE_HAUT, visuels.ZONE_SURE_BAS, visuels.MARGE_LATERALE), (270, 1248, 65))

    def test_min_text_size_in_code(self):
        import re
        src = open(visuels.__file__, encoding="utf-8").read()
        tailles = [int(x) for x in re.findall(r'font\("\w+", (\d+)\)', src)]
        self.assertTrue(tailles and min(tailles) >= visuels.TAILLE_TEXTE_MIN, tailles)

    def test_save_slides(self):
        with tempfile.TemporaryDirectory() as d:
            paths = visuels.save_slides([PHOTO, PHOTO], d, "x")
            self.assertEqual([os.path.basename(p) for p in paths], ["x-01.jpg", "x-02.jpg"])
            with Image.open(paths[0]) as im:
                self.assertEqual(im.format, "JPEG")

    def test_save_slides_rejects_api_ratio(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
            visuels.save_slides([Image.new("RGB", (1080, 1440))], d, "x")  # 3:4 refusé par l'API
        with tempfile.TemporaryDirectory() as d:
            visuels.save_slides([Image.new("RGB", visuels.CAROUSEL)], d, "x")  # 4:5 accepté


FICHE = {"handle": "le-nid", "nom": "Le Nid - Spa", "ville": "Vannes", "ville_reference": None, "region": "Bretagne",
         "prix_a_partir_de": 150.0, "equipements": ["Spa", "Sauna"], "equipements_non_citables": [],
         "url": "https://www.lovenspa.fr/products/le-nid", "actif": True, "ambiance": 1}
BASE = {"date": "2026-11-16", "heure": "18:30", "plateforme": "instagram", "statut": "A_PRODUIRE"}
CAPTION = ("Spa et sauna à Vannes : Le Nid, dès 150 € la nuit.\n\nUn gîte pour deux, le spa rien qu'à vous et le sauna "
           "qui chauffe pendant le dîner. Vous arrivez quand vous voulez, vous repartez sans vous presser, et la soirée "
           "vous appartient du début à la fin.\n\nEnregistrez ce post pour votre prochain week-end.\n\n#lovenspa #vannes")


class TestProduire(unittest.TestCase):
    def run_case(self, contenu, fetch=True):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "contenu.json"), "w", encoding="utf-8") as f:
                json.dump(contenu, f)
            cat = mock.Mock(images=mock.Mock(return_value=["u1", "u2", "u3", "u4"]))
            with (mock.patch.object(visuels, "fetch", return_value=PHOTO) if fetch else mock.MagicMock()), \
                    mock.patch.object(visuels, "render_reel", side_effect=lambda fr, out, **k: out), \
                    mock.patch.object(visuels, "probe", return_value={"streams": [{"codec_type": "video", "width": 1080,
                                                                                      "height": 1920}],
                                                                         "format": {"duration": "10.0"}}):
                paquet, verdict = produire.produce(d, marque=MARQUE, catalogue=cat)
                return {**paquet, **verdict}

    def test_lieu_ready(self):
        p = self.run_case({"case": {**BASE, "moteur": "lieu", "format": "REELS", "offres": [FICHE]}, "legende": CAPTION,
                           "reel_lignes": ["a", "b", "c"]})
        self.assertEqual(p["statut"], "PRET", p["bloquants"])

    def test_reel_photos_chosen_per_line(self):
        vus = []
        with mock.patch.object(visuels, "fetch", side_effect=lambda u, s=None: vus.append(u) or PHOTO):
            p = self.run_case({"case": {**BASE, "moteur": "lieu", "format": "REELS", "offres": [FICHE]},
                                                 "legende": CAPTION, "reel_lignes": ["a", "b", "c"], "reel_photos": [4, 1, 2]}, fetch=False)
        self.assertEqual(vus, ["u4", "u1", "u2"])
        self.assertNotIn("ordre de la boutique", " ".join(p["notes"]))

    def test_cover_photo_choice(self):
        vus = []
        with mock.patch.object(visuels, "fetch", side_effect=lambda u, s=None: vus.append(u) or PHOTO):
            self.run_case({"case": {**BASE, "moteur": "selection", "format": "CAROUSEL", "offres": [FICHE]},
                           "legende": CAPTION, "couverture": {"titre": "T", "sous_titre": "S", "photo": 4},
                           "fin": {"titre": "F", "texte": "x"}}, fetch=False)
        self.assertEqual(vus[0], "u4")

    def test_reel_photos_out_of_range(self):
        with self.assertRaises(RuntimeError):
            self.run_case({"case": {**BASE, "moteur": "lieu", "format": "REELS", "offres": [FICHE]}, "legende": CAPTION,
                           "reel_lignes": ["a", "b"], "reel_photos": [1, 9]})
        with self.assertRaises(RuntimeError):
            self.run_case({"case": {**BASE, "moteur": "lieu", "format": "REELS", "offres": [FICHE]}, "legende": CAPTION,
                           "reel_lignes": ["a", "b"], "reel_photos": [1]})

    def test_wrong_price_refused(self):
        p = self.run_case({"case": {**BASE, "moteur": "lieu", "format": "REELS", "offres": [FICHE]},
                           "legende": CAPTION.replace("150", "99"), "reel_lignes": ["a", "b", "c"]})
        self.assertEqual(p["statut"], "REFUSE")

    def test_selection_slide_count(self):
        p = self.run_case({"case": {**BASE, "moteur": "selection", "format": "CAROUSEL", "offres": [FICHE]},
                           "legende": CAPTION, "couverture": {"titre": "T", "sous_titre": "S"},
                           "fin": {"titre": "F", "texte": "x"}})
        self.assertEqual(len(p["medias"]), 3)

    def test_couple_needs_no_lodging(self):
        p = self.run_case({"case": {**BASE, "moteur": "couple", "format": "CAROUSEL", "offres": []},
                           "legende": CAPTION, "couple": {"titre": "T", "diapos": [{"titre": "a", "texte": "b"}], "cta": "c"}})
        self.assertEqual(p["statut"], "PRET", p["bloquants"])

    def test_too_many_slides(self):
        with self.assertRaises(RuntimeError):
            self.run_case({"case": {**BASE, "moteur": "couple", "format": "CAROUSEL", "offres": []}, "legende": CAPTION,
                           "couple": {"titre": "T", "diapos": [{"titre": "a", "texte": "b"}] * 9, "cta": "c"}})


if __name__ == "__main__":
    unittest.main()
