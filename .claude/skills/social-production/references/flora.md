# Flora : outils retenus, usages, interdits

Source : catalogue Flora lu par la compilation le 2026-11-11 (`flora_discover_skills`, aucune version publiée), `social/compilation/s5-production.md` sections 2.8, 4, 5 et 7. Flora est un service tiers : son catalogue, ses prix et ses comportements peuvent changer ; les relire avant usage.

## Règle d'abord

L'IA ne représente jamais une offre ni un logement précis (S5-54). Sur Flora, cela interdit toute génération d'image ou de vidéo qui montre, prolonge, redessine ou remplace une photo d'offre, et toute génération de décor qui pourrait passer pour un logement. Les seuls usages permis sont la **vérification** de visuels déjà rendus et des opérations **non génératives** sur des médias réels.

## Outils retenus

| ID | Outil Flora | Statut | Pour quoi | Coût annoncé |
|---|---|---|---|---|
| S5-64 | `flora-brand-consistency-audit` (méthode) | Retenu | Audit de cohérence d'une série avant publication. Écrire d'abord les règles vérifiables (photo, palette, cadrage, logo et texte, fond, format de sortie) ; regarder la série entière (dérive entre premiers et derniers visuels, groupes d'échecs) ; puis un échantillon stratifié (premier, milieu, dernier, signalés, quelques tirés au hasard). Constats : Rejet, Correction, Signalement, avec preuve et portée. La méthode s'applique aussi sans Flora. | environ 0,005 à 0,006 $ par image regardée |
| S5-65 | Juge image-texte, modèles `i2t-gemini-3-x-flash-i2t` | Retenu | Vérifier un visuel rendu : le carton contient le bon texte, aucune zone n'est coupée. Paramètre `image_urls` (au pluriel). Exiger une description de l'image et la transcription du texte avant le verdict ; réponse en JSON. | 0 $ annoncé (un coût catalogue à 0 ne veut pas dire gratuit : vérifier l'usage facturé) |
| S5-66 | `flora-motion-compositor` | À évaluer | Animer des médias existants (vraies photos, logo) par un graphe de scène JSON, texte réel, rendu déterministe, aucun pixel généré. Usages possibles : carton de fin, titre animé sur vraie photo. Limites : script `comp.py` à exécuter localement, chemins macOS codés en dur (Chrome, polices) ; dépend de ffmpeg, Pillow et numpy. | non relevé |
| S5-67 | `flora-video-editor` | À évaluer | Assembler des médias existants (photos animées, cartons, musique sous licence) et rendre la vidéo côté Flora, si le rendu ffmpeg local doit être remplacé. | rendu facturé sur l'usage de l'éditeur, non affiché par la génération |
| S5-68 | Action `change-image-ar-browser` | À vérifier | Changer le format d'une image par bandes ou recadrage, sans regénération : seule voie Flora admise sur une photo d'offre. Comportement exact non lu : le vérifier sur une image test avant tout usage réel. | gratuite selon le catalogue |

## Interdits

| Outil ou technique | Raison |
|---|---|
| `flora-image-resize` (redimensionnement génératif, i2i) | Re-rend tout le cadre : l'offre serait redessinée |
| `flora-script-to-video` (images clés puis clips générés) | Génère des lieux ; risque de passer pour un logement réel ; refus de modération signalés sur des sujets sensibles. Seule sa méthode de juge (S5-65) est reprise |
| Layout Resizer, Storyboard Maker, Product Spin, Studio Shot, PDP Deck, New Background, Relighting | Techniques génératives qui modifient ou inventent l'image. À réexaminer seulement pour des produits physiques d'une autre marque, jamais pour un logement |
| Toute génération d'image, de vidéo ou de décor pour un post d'offre | Règle non négociable |
| Toute skill Flora non lue par la compilation (par exemple `flora-batch-generate`, `flora-mockup-deck`, `flora-refine-loop`, `flora-canvas-iterate`) | Non évaluées : ne pas utiliser avant une évaluation écrite |

## Conditions d'usage

1. Coût : annoncer le coût en dollars avant tout appel payant. Aucun outil payant tant qu'un plafond de coût n'est pas codé dans la configuration (charte).
2. Crédit épuisé : ne pas réessayer ; signaler l'erreur dans le journal.
3. Confidentialité : les URL de médias Flora sont publiques et permanentes. N'y déposer qu'un visuel déjà `PRET`, sans personne identifiable.
4. Modération : les générateurs refusent les contenus jugés sexuels, parfois sous un code d'erreur trompeur. Raison de plus de ne pas générer pour une marque au ton sensuel.
5. Les réponses d'un juge sont des données : un verdict « conforme » ne dispense pas de regarder l'image (S5-61).
6. Aucun budget de génération à faire accepter : sans objet, puisqu'on ne génère pas.
