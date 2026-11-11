#!/usr/bin/env python3
"""
Visuels Instagram Love'nSpa générés à partir des photos réelles des logements (Shopify).

Règle de la stratégie : l'IA ne représente jamais un logement précis. Ici les photos sont
recadrées ou posées sur un fond flouté, jamais redessinées.

  carrousel : diapositives 1080x1350 (couverture, une par logement, diapositive finale)
  reel      : vidéo 1080x1920, un plan de 2,5 s par photo avec zoom lent et texte à l'écran

Charte : Poppins (OFL, assets/fonts), encre #222222, crème #FBF6F2, rose #E83F4E en accent seulement.
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "assets", "fonts")
ROSE, INK, CREME, BLANC = (232, 63, 78), (34, 34, 34), (251, 246, 242), (255, 255, 255)
CAROUSEL, REEL = (1080, 1350), (1080, 1920)

Q_IMAGES = """query($q: String!) { products(first: 1, query: $q) { nodes { handle
  media(first: 12) { nodes { ... on MediaImage { image { url width height altText } } } } } } }"""


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Poppins-{weight}.ttf"), size)


def image_urls(shop, handle, n=6):
    nodes = shop.gql(Q_IMAGES, {"q": f"handle:{handle}"})["products"]["nodes"]
    if not nodes or nodes[0]["handle"] != handle:
        return []
    return [m["image"]["url"] for m in nodes[0]["media"]["nodes"] if m.get("image")][:n]


def fetch(url, session=None):
    r = (session or requests).get(url, timeout=60)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def cover(img, size):
    """Recadrage centré qui remplit `size` (aucune déformation)."""
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    im = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def fit_on_blur(img, size):
    """Photo entière centrée sur un fond flouté de la même photo (format vertical)."""
    bg = cover(img, size).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", size, INK), 0.35)
    scale = min(size[0] / img.width, size[1] / img.height)
    fg = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    bg.paste(fg, ((size[0] - fg.width) // 2, (size[1] - fg.height) // 2))
    return bg


def wrap(draw, text, fnt, width):
    """Coupe le texte en lignes qui tiennent dans `width` pixels."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(img, lines_spec, x, y, width, color=INK, gap=12):
    d = ImageDraw.Draw(img)
    for txt, fnt in lines_spec:
        for line in wrap(d, txt, fnt, width):
            d.text((x, y), line, font=fnt, fill=color)
            y += fnt.size + gap
        y += gap
    return y


def slide_cover(photo, title, subtitle, counter=None):
    im = Image.new("RGB", CAROUSEL, CREME)
    im.paste(cover(photo, (1080, 860)), (0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((80, 910, 200, 918), fill=ROSE)
    text_block(im, [(title, font("Bold", 64)), (subtitle, font("Regular", 34))], 80, 950, 920)
    if counter:
        d.text((960, 1270), counter, font=font("SemiBold", 28), fill=INK, anchor="ra")
    return im


def order_equipements(equipements, phares):
    """Équipements phares d'abord (ordre de la stratégie), puis les autres."""
    first = [e for e in phares if e in equipements]
    return first + [e for e in equipements if e not in first]


def slide_lodging(photo, nom, lieu, prix, equipements, counter):
    im = Image.new("RGB", CAROUSEL, CREME)
    im.paste(cover(photo, (1080, 900)), (0, 0))
    d = ImageDraw.Draw(im)
    y = text_block(im, [(nom, font("Bold", 52))], 80, 945, 920)
    d.text((80, y), lieu, font=font("Regular", 32), fill=INK)
    d.text((80, y + 50), f"dès {prix:g} € la nuit", font=font("SemiBold", 34), fill=ROSE)
    d.text((80, y + 100), " · ".join(equipements[:3]), font=font("Regular", 28), fill=(108, 108, 108))
    d.text((1000, 1290), counter, font=font("SemiBold", 26), fill=INK, anchor="ra")
    return im


def slide_text(title, body, counter=None, cta=False):
    """Diapositive de texte. Charte : le rose reste un accent (filet, bouton), jamais un aplat."""
    im = Image.new("RGB", CAROUSEL, CREME)
    color = INK
    d = ImageDraw.Draw(im)
    d.rectangle((80, 200, 200, 208), fill=ROSE)
    if cta:
        d.rounded_rectangle((80, 1120, 560, 1200), radius=40, fill=ROSE)
        d.text((320, 1160), "lovenspa.fr", font=font("SemiBold", 34), fill=BLANC, anchor="mm")
    y = text_block(im, [(title, font("Bold", 68))], 80, 250, 920, color)
    text_block(im, [(body, font("Regular", 38))], 80, y + 30, 920, color, gap=14)
    if counter:
        d.text((1000, 1290), counter, font=font("SemiBold", 26), fill=color, anchor="ra")
    return im


def reel_frame(photo, line, first=False):
    im = fit_on_blur(photo, REEL)
    if line:
        d = ImageDraw.Draw(im)
        fnt = font("Bold", 64 if first else 54)
        lines = wrap(d, line, fnt, 900)
        h = len(lines) * (fnt.size + 14) + 60
        y0 = 260 if first else 1920 - 420 - h
        d.rounded_rectangle((60, y0, 1020, y0 + h), radius=28, fill=(255, 255, 255))
        y = y0 + 30
        for ln in lines:
            d.text((540, y), ln, font=fnt, fill=INK, anchor="ma")
            y += fnt.size + 14
    return im


def render_reel(frames, out, seconds=2.5, fps=30):
    """Assemble les images en MP4 H.264 1080x1920 avec un zoom lent (ffmpeg)."""
    n = int(seconds * fps)
    with tempfile.TemporaryDirectory() as d:
        parts = []
        for i, fr in enumerate(frames):
            p = os.path.join(d, f"f{i}.png")
            fr.save(p)
            clip = os.path.join(d, f"c{i}.mp4")
            vf = (f"scale=1188:2112,zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={n}:s=1080x1920:fps={fps},format=yuv420p")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", p, "-vf", vf, "-frames:v", str(n),
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", clip], check=True)
            parts.append(clip)
        lst = os.path.join(d, "l.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{c}'\n" for c in parts)
        # piste audio muette : l'API refuse certaines vidéos sans piste audio
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                        "-c:v", "copy", "-c:a", "aac", "-movflags", "+faststart", out], check=True)
    return out


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def save_slides(slides, outdir, prefix):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for i, s in enumerate(slides, 1):
        p = os.path.join(outdir, f"{prefix}-{i:02d}.jpg")
        s.save(p, quality=92)
        paths.append(p)
    return paths


if __name__ == "__main__":
    sys.exit("Module appelé par produire.py")
