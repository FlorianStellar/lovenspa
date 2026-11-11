import json
import os
import tempfile
import unittest
from unittest import mock

from PIL import Image, ImageDraw

import produire
import visuels

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

    def test_save_slides(self):
        with tempfile.TemporaryDirectory() as d:
            paths = visuels.save_slides([PHOTO, PHOTO], d, "x")
            self.assertEqual([os.path.basename(p) for p in paths], ["x-01.jpg", "x-02.jpg"])


FICHE = {"handle": "le-nid", "nom": "Le Nid - Spa", "ville": "Vannes", "ville_reference": None, "region": "Bretagne",
         "prix_a_partir_de": 150.0, "equipements": ["Spa", "Sauna"], "equipements_non_citables": [],
         "url": "https://www.lovenspa.fr/products/le-nid"}
CAPTION = ("Spa et sauna à Vannes : Le Nid, dès 150 € la nuit.\n\nUn gîte pour deux, le spa rien qu'à vous et le sauna "
           "qui chauffe pendant le dîner. Vous arrivez quand vous voulez, vous repartez sans vous presser, et la soirée "
           "vous appartient du début à la fin.\n\nEnregistrez ce post pour votre prochain week-end.\n\n#lovenspa #vannes")


class TestProduire(unittest.TestCase):
    def run_case(self, contenu):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "contenu.json"), "w", encoding="utf-8") as f:
                json.dump(contenu, f)
            with mock.patch.object(visuels, "image_urls", return_value=["u1", "u2", "u3", "u4"]), \
                    mock.patch.object(visuels, "fetch", return_value=PHOTO), \
                    mock.patch.object(visuels, "render_reel", side_effect=lambda fr, out, **k: out), \
                    mock.patch.object(visuels, "probe", return_value={"streams": [{"codec_type": "video", "width": 1080,
                                                                                      "height": 1920}],
                                                                         "format": {"duration": "10.0"}}):
                return produire.produce(d, shop=object())

    def test_lieu_ready(self):
        p = self.run_case({"case": {"moteur": "lieu", "format": "REELS", "logements": [FICHE]}, "legende": CAPTION,
                           "reel_lignes": ["a", "b", "c"]})
        self.assertEqual(p["statut"], "PRET", p["bloquants"])

    def test_wrong_price_refused(self):
        p = self.run_case({"case": {"moteur": "lieu", "format": "REELS", "logements": [FICHE]},
                           "legende": CAPTION.replace("150", "99"), "reel_lignes": ["a", "b", "c"]})
        self.assertEqual(p["statut"], "REFUSE")

    def test_selection_slide_count(self):
        p = self.run_case({"case": {"moteur": "selection", "format": "CAROUSEL", "logements": [FICHE]},
                           "legende": CAPTION, "couverture": {"titre": "T", "sous_titre": "S"},
                           "fin": {"titre": "F", "texte": "x"}})
        self.assertEqual(len(p["medias"]), 3)

    def test_couple_needs_no_lodging(self):
        p = self.run_case({"case": {"moteur": "couple", "format": "CAROUSEL", "logements": []},
                           "legende": CAPTION, "couple": {"titre": "T", "diapos": [{"titre": "a", "texte": "b"}], "cta": "c"}})
        self.assertEqual(p["statut"], "PRET", p["bloquants"])

    def test_too_many_slides(self):
        with self.assertRaises(RuntimeError):
            self.run_case({"case": {"moteur": "couple", "format": "CAROUSEL", "logements": []}, "legende": CAPTION,
                           "couple": {"titre": "T", "diapos": [{"titre": "a", "texte": "b"}] * 9, "cta": "c"}})


if __name__ == "__main__":
    unittest.main()
