# Spécifications par plateforme

Aucune source lue par la compilation n'est une documentation officielle de plateforme. **Toutes les valeurs ci-dessous sont à vérifier dans la documentation officielle** avant d'être codées comme limites dures. Aucune ligne n'en est exemptée : aucune source officielle n'a été lue.

Source de chaque valeur : `social/compilation/s5-production.md`, section 3 (abréviations développées dans `../SOURCES.md`).

## Instagram

| Élément | Valeur | Statut | Source |
|---|---|---|---|
| Reel : format | 1080x1920 (9:16) | à vérifier dans la documentation officielle | IG ig-reel ; RT rt-montage ; MV shorts-codes |
| Reel : encodage | 30 i/s, H.264, AAC 48 kHz, -14 LUFS, crête vraie ≤ -1 dBTP | à vérifier dans la documentation officielle | MV shorts-codes |
| Reel : durée maximale | 3 min selon IG ; 20 min selon RT (contradiction) | à vérifier dans la documentation officielle | IG ig-reel ; RT rt-video |
| Reel : durée de travail | 15 à 45 s ; moins de 45 s conseillé | à vérifier dans la documentation officielle (recommandation de tiers) | IG ig-reel ; MV shorts-codes |
| Reel : zone sûre | IG : y=230 à 1440, 230 px libres à droite. RT : y=230 à 1440, 140 px à droite, 60 px à gauche. MV shorts-codes : x=60 à 940, y=220 à 1500, colonne droite 140 px de y=900 à 1700. MV style : y=170 à 1500, 220 px à droite sous y=1100 | à vérifier dans la documentation officielle | IG ig-reel ; RT rt-video ; MV shorts-codes ; MV style |
| Story : zone sûre | 1080x1920, texte entre y=250 et y=1600 | à vérifier dans la documentation officielle | IG ig-story ; RT rt-story |
| Story : volume | 3 à 7 images par jour | à vérifier dans la documentation officielle (recommandation de tiers) | IG ig-story |
| Carrousel : format | 1080x1350 (4:5), JPEG ou PNG | à vérifier dans la documentation officielle | IG ig-carousel ; RT rt-carrousel |
| Carrousel : nombre | 20 éléments au plus selon IG et RT ; 10 dans notre code ; 6 à 10 recommandés | à vérifier dans la documentation officielle (limite de l'API de publication) | IG ig-carousel ; RT rt-carrousel ; LNS produire.py |
| Carrousel : marges et texte | texte de couverture à plus de 120 px des bords ; texte ≥ 32 px | à vérifier dans la documentation officielle (recommandation de tiers) | IG ig-carousel |
| Post carré, story, couverture | 1080x1080 (fil) ; 1080x1920 (story, couverture de Reel) | à vérifier dans la documentation officielle | KW canva-api |
| Légende | 2 200 caractères ; environ 125 visibles avant « plus » | à vérifier dans la documentation officielle | IG ig-caption ; RT legende.py |
| Hashtags | 5 au plus par post depuis le 18/12/2025 | à vérifier dans la documentation officielle (sources de presse : blogdumoderateur.com, socialmediatoday.com, citées dans `regles.json`) | IG ig-caption ; RT rt-legende ; LNS regles.json |

## TikTok

| Élément | Valeur | Statut | Source |
|---|---|---|---|
| Vidéo : format | 1080x1920 (9:16), même export que le Reel | à vérifier dans la documentation officielle | RT rt-video ; MV shorts-codes |
| Vidéo : durée | 10 min en application ; 20 à 35 s conseillé | à vérifier dans la documentation officielle | RT rt-video |
| Zone sûre | y=230 à 1440, 140 px libres à droite, environ 60 px à gauche | à vérifier dans la documentation officielle | RT rt-video ; RT rendre.py |
| Mode photo | 1080x1920, 35 images au plus, un son par-dessus | à vérifier dans la documentation officielle | RT rt-carrousel |
| Légende | 4 000 caractères ; environ 80 à 100 visibles (90 dans le linter RT) | à vérifier dans la documentation officielle | RT rt-legende ; RT legende.py |
| Hashtags | 5 au plus | à vérifier dans la documentation officielle | RT rt-legende |
| Commentaire | 150 caractères au plus | à vérifier dans la documentation officielle | RT rt-legende |
| Recherche | lit la légende, le texte à l'écran et l'audio transcrit | à vérifier dans la documentation officielle | RT rt-legende |
| Live | seuil d'abonnés (souvent 1 000) et 18 ans | à vérifier dans la documentation officielle | RT rt-story |

## Pinterest

Aucune spécification dans les sources lues. Format d'épingle, durée vidéo, titre et description : à sourcer dans la documentation officielle avant le jalon Pinterest. La mention « PI » dans les règles signifie « règle générique applicable », jamais « spécification Pinterest ».

## Autres formats cités (déclinaisons)

| Élément | Valeur | Statut | Source |
|---|---|---|---|
| Facebook fil | 1200x630 | à vérifier dans la documentation officielle | KW canva-api ; KW calendar |
| LinkedIn | 1200x627 | à vérifier dans la documentation officielle | KW calendar |
| Bloc newsletter | 600x400 ; en-tête e-mail 600x200 | à vérifier dans la documentation officielle | KW calendar ; KW canva-api |

## Valeurs de travail retenues (arbitrages de la compilation)

Ces valeurs sont des choix prudents du système, pas des spécifications : elles restent valables tant que la documentation officielle ne les contredit pas.

| Sujet | Valeur retenue | Origine |
|---|---|---|
| Zone de texte d'un Reel ou d'une vidéo TikTok | x=60 à 940, y=230 à 1440 ; aucun texte au-delà de x=850 entre y=900 et y=1440 | intersection la plus prudente des sources (conflit « zone sûre ») |
| Diapos par carrousel | 10 au plus | code actuel, en attendant la limite officielle de l'API |
| Post de fil | 1080x1350 ; le carré n'est qu'une déclinaison | conflit « format du post de fil » |
| Taille de texte | 32 px minimum sur diapo ; 34 px en vidéo ; sous-titres 72 px minimum si voix | conflit « taille minimale » |
| Durée de Reel | cible 20 à 30 s | S5-19 ; la durée maximale est sans effet |
| Piste audio | piste muette tant qu'il n'y a pas de musique sous licence, en 48 kHz ; avec musique, -14 LUFS | conflit « piste audio » |

## Valeurs codées aujourd'hui (faits du code, pas des spécifications)

| Constante | Valeur | Fichier |
|---|---|---|
| `CAROUSEL` | 1080x1350 | `social/s5_production/visuels.py` |
| `REEL` | 1080x1920 | idem |
| Plan par photo | 2,5 s, 30 i/s, zoom jusqu'à 1,08 | `visuels.render_reel` |
| Encodage | libx264, preset veryfast, crf 20, yuv420p, AAC piste muette 44,1 kHz, `+faststart` | idem |
| `MAX_DIAPOS` | 10 | `social/s5_production/produire.py` |

Le code porte encore les commentaires « à déplacer dans les règles de plateforme de S2 au jalon J3 » : ces dimensions sont propres à Instagram.
