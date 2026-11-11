# Sources de la skill social-veille

## Provenance directe

| Élément de la skill | Repris de |
|---|---|
| `SKILL.md`, règles, niveaux de preuve, limites | `lovenspa@ec9fede:social/compilation/s2-connaissance.md` (conventions, sections 2, 3 et 4) ; gabarit `social/compilation/GABARIT-SKILL.md` |
| Description du benchmark (ce qu'il calcule) | `lovenspa@ec9fede:social/s2_connaissance/benchmark.py` (fonctions `discover`, `engagement`, `summarize`, `to_markdown`, `main`) ; `social/connecteurs/instagram.py` ; `social/marque.py` (`comptes_reference`, `donnees`) |
| Contrat des fiches | `lovenspa@ec9fede:social/contrats/fiche_format.schema.json` ; validateur `social/contrats/valider.py` |
| `references/formats.md` (F01 à F18) | compilation, section 3 ; benchmark `lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md` (copie identique : `social/donnees/lovenspa/instagram/benchmark-2026-11-11.md`) |
| `references/accroches.md` | `lovenspa@ec9fede:social/compilation/accroches-fr.json` (lu en entier, non recopié) ; compilation S2-M22, S2-M23, section 4.1 ; renvoi à S5-16 de `social/compilation/s5-production.md` |
| `references/regles-plateformes.md` (S2-R01 à S2-R09) | compilation, section 2.2 et conflits (section 4.2) |
| `references/methodes.md` (S2-M01 à S2-M24) | compilation, section 2.1 et conflits (section 4.2) |
| Boucle mensuelle S8 -> S2, niveaux A/B/C | doc d'architecture « Système social média – Love'nSpa puis Stellar Fleet » (sections S2 et S8), cité par `social/README.md` |

## Sources amont citées par la compilation

Toutes lues par la compilation comme données ; aucun de leurs scripts n'a été exécuté, ni pour la compilation ni pour cette skill.

| Dépôt | Commit | Licence | Titulaire du copyright | Usage ici |
|---|---|---|---|---|
| instagram-agent-skill | d03c56b | MIT | Jake Schincariol | Méthodes S2-M01, M04 à M07, M09 à M11, M14, M21 à M23 ; formules A01 à A26 ; règles S2-R01 à R03, R05 ; mesures du score d'accroche (README). |
| Explo38_reels-tiktok-fr | a2281b6 | MIT | Jake Schincariol | Adaptation française du dépôt précédent ; méthodes S2-M01, M03 à M07, M09 à M14, M18, M19, M21, M23 ; règles S2-R01, R02, R05 à R07. |
| rediumvex_viral-hooks-skill | e26b339 | MIT | Roman Knox | Formules A27 à A60 (et rapprochements A01 à A26) ; S2-M23. La base déclare s'inspirer de `jakeolschewski/social-media-hooks-database` (MIT). |
| ScrapeCreators_social-media-research-skills | 64ba7b4 | MIT | ScrapeCreators | Méthodes S2-M03, M15 à M19. Outil payant non repris. |
| Melvynx_video-agent-skills | f454292 | MIT | Melvyn Malherbe | Méthodes S2-M01 à M03, M06, M08 à M10, M15, M20, M21 ; règles S2-R04, R08. Outil Treg, yt-dlp et ffmpeg non repris. |
| nexscope-ai_ecommerce-skills | ee0fb29 | MIT | Nexscope AI | S2-M17, M24 ; règle S2-R09 ; structures de F03, F11, F13 à F16, F18 ; durées (preuve C). Liens promotionnels non repris. |
| Données Love'nSpa (benchmark) | 485c428 | interne | Love'nSpa | Niveaux B des fiches F01 à F08, observations de F09 et F10, formules A61 à A63. Exemple de première marque cliente. |

## Licences

- Les six dépôts amont sont sous licence MIT. Les mentions de copyright ci-dessus sont conservées. Les années de copyright ne figurent pas dans la compilation : les recopier depuis le fichier `LICENSE` de chaque dépôt au commit cité.
- Les fichiers de cette skill adaptent, traduisent et réécrivent ; ils ne reproduisent pas de portion substantielle d'un texte source tel quel. Si un texte source est un jour repris tel quel dans un produit Stellar Fleet, joindre la notice MIT complète du titulaire (« Copyright (c) <année> <titulaire> » et le texte de permission).
- Le benchmark et les accroches maison sont des données internes de la première marque cliente : ne pas les diffuser hors de ses usages.

## Modifications signalées

- Chaque accord humain des sources (validation du panel avant collecte) est remplacé par une ligne de la charte d'autonomie.
- Les fiches de format sont mises au format du contrat `fiche_format` : une seule `plateforme` et un seul `objectif` par fiche. Les objectifs hors énumération (confiance, commentaires, trafic) sont rangés dans la valeur la plus proche et gardés dans `objectif_compilation` (F09, F15, F16, F17, F18, F07).
- Les éléments propres à la première marque sont marqués « exemple ».
- Le seuil d'infirmation d'une fiche n'est pas fixé par la compilation : signalé comme limite, à écrire au journal.
- La compilation situe le benchmark dans `social/s8_mesure/benchmark.py` ; le code est dans `social/s2_connaissance/benchmark.py`. La skill décrit le code tel qu'il est.
- Éléments écartés par la compilation (section 4.1) non repris.
