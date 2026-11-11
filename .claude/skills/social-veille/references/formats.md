# Bibliothèque de formats (amorce)

Dix-huit fiches au format du contrat `social/contrats/fiche_format.schema.json` (champs obligatoires : `id`, `nom`, `plateforme`, `objectif`, `structure`, `preuve`, `sources` ; champs supplémentaires permis). Reprises de `social/compilation/s2-connaissance.md`, section 3.

Bilan : 8 fiches en preuve B (F01 à F08, dont F02 biaisée), 10 en preuve C (F09 à F18), aucune en A.

## Comment lire ces fiches

- **Niveaux de preuve.** A : confirmé par nos propres données (aucune à ce jour). B : observé à plus de 3 fois l'engagement médian chez au moins 3 comptes du benchmark. C : signalé par une seule source.
- **Ce que mesure le B.** Le benchmark ne donne que le type de publication, la date, le multiple d'engagement (likes + commentaires ÷ médiane du compte : « surperformance d'interactions », S2-M02) et la première ligne de légende. Le contenu visuel n'a pas été observé. Pour les fiches B, la structure est donc **proposée** à partir des règles des sources, pas relevée. Les durées viennent de sources de niveau C.
- **Benchmark d'amorce (exemple : première marque cliente, Love'nSpa).** `lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md`, copie identique dans `social/donnees/lovenspa/instagram/benchmark-2026-11-11.md`. 37 comptes lus, 3 illisibles, 50 dernières publications par compte. Les comptes cités dans « observe » sont ceux de ce benchmark ; pour une autre marque, refaire le benchmark sur son panel avant de reprendre un niveau B.
- **Biais des concours.** La mécanique d'un concours (commenter, identifier un ami, partager) gonfle les commentaires et donc le multiple d'interactions. Les concours, sponsorisés et collaborations doivent être retirés des médianes et classés à part (S2-M03, S2-R08). Le benchmark d'amorce ne l'a pas fait : F02 reste B mais marquée « biaisée », et les multiples des autres fiches sont calculés sur des médianes qui incluent ces publications.
- **Fenêtre.** Le benchmark mélange des publications de 2024 à 2026 selon les comptes. Les multiples cités sont donc à recalculer sur la fenêtre 7 à 180 jours (S2-M03).
- **Contrat.** `plateforme` et `objectif` n'acceptent qu'une valeur. Les autres plateformes sont dans `transposable`, les objectifs secondaires dans `objectif_secondaire`. Quand l'objectif de la compilation sort de l'énumération du contrat (confiance, commentaires, trafic), il est gardé dans `objectif_compilation` et la valeur du contrat est signalée comme un rangement.
- `{{ }}` = donnée réelle à fournir. Les éléments propres à la première marque sont marqués « exemple ».

## F01. Reel de visite sensorielle d'un logement (B)

```json
{
  "id": "F01",
  "nom": "Reel de visite sensorielle d'un logement",
  "plateforme": "instagram",
  "transposable": ["tiktok"],
  "objectif": "portee",
  "objectif_secondaire": ["conversion"],
  "objectif_note": "Hypothèse : le benchmark ne mesure que l'engagement.",
  "structure": [
    "0-1 s : premier plan déjà en mouvement, dans le lieu (porte qui s'ouvre, vapeur qui monte). Texte à l'écran de 6 mots maximum. Pas de mise en place.",
    "1-8 s : détails sensoriels, plans courts de 0,5 à 1,5 s, coupe franche.",
    "Avant la moitié : l'atout promis est montré (exemple Love'nSpa : le spa rien qu'à deux).",
    "Fin : nom du lieu ou région, appel (lien en bio ou commentaire, voir F09).",
    "Légende : première ligne en suspens (accroche A61)."
  ],
  "structure_statut": "proposée (contenu visuel non observé)",
  "duree": "15 à 30 s (preuve C)",
  "preuve": "B",
  "observe": "8 comptes au-dessus de 3x : Love in Room (50,1x ; 11,2x ; 7,2x ; 4,1x ; 3,6x), Chéri fais tes valises (15,5x ; 7,8x ; 4,5x), Let's go my love (9,9x), Les Cabanes dans les Bois (5,8x ; 3,4x ; 3,2x), Canopy & Stars (4,2x ; 3,4x), Secret de Paris (4,0x ; 3,5x), AbracadaRoom (3,1x), Attrape-Rêves (3,1x).",
  "exemples": [
    "https://www.instagram.com/reel/DcTr2wHI4T9/ (Love in Room, 50,1x)",
    "https://www.instagram.com/reel/Dcd6dG_AdSS/ (Secret de Paris, 4,0x)",
    "https://www.instagram.com/reel/DbtYgFHILBd/ (Les Cabanes dans les Bois, 5,8x)"
  ],
  "limites": [
    "Love in Room n'a que 20 publications : sous le seuil de 10 publications dans la fenêtre si l'on applique S2-M03, à vérifier.",
    "Les succès de Chéri fais tes valises datent de 2025 (dernière publication il y a 177 jours au moment du benchmark).",
    "Multiple d'interactions, pas de vues."
  ],
  "sources": [
    "lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md",
    "instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json (rules)",
    "Melvynx_video-agent-skills@f454292:skills/steal/references/learnings.md (point 4)",
    "nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md (Instagram, durée)",
    "accroche A24 « La révélation »"
  ]
}
```

## F02. Concours, carrousel ou Reel (B, biaisée)

```json
{
  "id": "F02",
  "nom": "Concours (carrousel ou Reel)",
  "plateforme": "instagram",
  "objectif": "abonnes",
  "objectif_secondaire": ["portee"],
  "structure": [
    "Titre en capitales « CONCOURS ».",
    "Lot chiffré (« 2 nuits », « une nuitée »).",
    "Souvent un partenaire co-organisateur.",
    "Après le tirage : mention « terminé » ajoutée au titre."
  ],
  "structure_statut": "observée dans les légendes seulement ; contenu des diapositives non observé",
  "preuve": "B",
  "biais": "La mécanique (commenter, identifier un ami) gonfle les commentaires. Ces publications devraient être retirées des médianes et classées à part (S2-M03, S2-R08). Le multiple ne prouve donc pas une préférence du public pour le format.",
  "observe": "9 comptes au-dessus de 3x : Weekendesk (152,2x ; 56,7x), Coucoo Cabanes (55,2x ; 50,1x), Smartbox (39,4x), Explore France (31,8x), Staycation (31,3x), YESforLOV (8,3x), Let's go my love (7,8x ; 6,1x ; 5,8x), Amoureux du monde (7,4x ; 6,0x ; 5,1x ; 3,2x), Passage du Désir (6,9x).",
  "exemples": [
    "https://www.instagram.com/p/DeMCq8tEV3j/ (Coucoo Cabanes, 55,2x)",
    "https://www.instagram.com/p/DfPDpKzjUxR/ (Let's go my love, 7,8x)"
  ],
  "limites": [
    "Biais de mécanique : multiple non comparable aux autres formats ; comparer un concours à d'autres concours seulement.",
    "À valider hors sources : règlement de jeu-concours et règles Meta sur les promotions (aucune source compilée ne les couvre)."
  ],
  "sources": [
    "lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md",
    "Melvynx_video-agent-skills@f454292:skills/insta-audit/references/workflow.md (point 6, concours à séparer)"
  ]
}
```

## F03. Carrousel sélection ou guide d'adresses (B)

```json
{
  "id": "F03",
  "nom": "Carrousel sélection ou guide d'adresses",
  "plateforme": "instagram",
  "transposable": ["pinterest"],
  "transposable_note": "Version épingle multipage sur Pinterest (F16).",
  "objectif": "enregistrement",
  "objectif_secondaire": ["partage"],
  "structure": [
    "Diapo 1 : couverture forte, promesse chiffrée (exemple : « {{N}} logements avec spa à moins de {{durée}} de {{ville}} »).",
    "Diapos 2 à N : un lieu par diapositive, une photo réelle, une ligne d'atout.",
    "Une diapositive « favori » annoncée dès la couverture.",
    "Dernière diapo : appel à enregistrer ou à partager."
  ],
  "structure_statut": "proposée",
  "nombre_diapos": "5 à 10 (preuve C) ; 7 éléments maximum dans la liste",
  "preuve": "B",
  "observe": "6 comptes au-dessus de 3x : Hipcamp (9,6x), Le Bonbon (8,6x), Millesvoyages (7,1x), Explore France (6,5x ; 3,4x), Staycation (4,9x), Mr & Mrs Smith (4,6x ; 3,2x).",
  "exemples": [
    "https://www.instagram.com/p/Dd4K8BxjgEG/ (Staycation, 4,9x)",
    "https://www.instagram.com/p/DcgYiaZoMGi/ (Mr & Mrs Smith, 4,6x)"
  ],
  "limites": ["Multiple d'interactions : l'objectif enregistrement n'est pas mesuré par le benchmark (hypothèse à confirmer par S8)."],
  "sources": [
    "lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md",
    "nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md",
    "instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=11 (piège : 7 éléments maximum)",
    "accroche A11"
  ]
}
```

## F04. Carrousel d'un lieu unique, en reportage photo (B)

```json
{
  "id": "F04",
  "nom": "Carrousel d'un lieu unique, en reportage photo",
  "plateforme": "instagram",
  "objectif": "portee",
  "objectif_secondaire": ["enregistrement"],
  "structure": [
    "Diapo 1 : la plus belle vue du logement.",
    "Diapos suivantes : détails (exemple Love'nSpa : spa, lit, lumière du soir).",
    "Dernière diapo : localisation."
  ],
  "structure_statut": "proposée ; contenu exact des diapositives non observé",
  "preuve": "B",
  "observe": "5 comptes au-dessus de 3x : Bruno Maltor (65,7x ; 12,8x ; 5,1x, légende réduite au nom du lieu), Plum Guide (5,5x), Canopy & Stars (4,3x ; 3,7x), Les Plus Beaux Villages de France (4,3x), Secret de Paris (3,9x).",
  "exemples": [
    "https://www.instagram.com/p/Dehf8O5Fy68/ (Plum Guide, 5,5x)",
    "https://www.instagram.com/p/De3l2XJl7hv/ (Canopy & Stars, 4,3x)"
  ],
  "limites": ["Structure non observée : à confirmer par visionnage (S2-M05)."],
  "sources": ["lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md"]
}
```

## F05. Annonce de nouveauté ou de partenariat (B)

```json
{
  "id": "F05",
  "nom": "Annonce de nouveauté ou de partenariat",
  "plateforme": "instagram",
  "objectif": "portee",
  "objectif_secondaire": ["abonnes"],
  "structure": [
    "Diapo 1 : « Nouveau » et la photo qui montre l'atout.",
    "Diapo 2 : ce que ça change.",
    "Diapos suivantes : détails.",
    "Dernière diapo : quand et où réserver."
  ],
  "structure_statut": "proposée (formule A24 « La révélation »)",
  "preuve": "B",
  "observe": "4 comptes au-dessus de 3x, surtout en carrousel : YESforLOV (53,1x, artiste partenaire), Coucoo Cabanes (6,8x, nouveau domaine), Canopy & Stars (6,8x), Staycation (4,0x ; 3,6x ; 3,0x, collaborations et événements).",
  "exemples": [
    "https://www.instagram.com/p/DdmVvBFjWUG/ (Canopy & Stars, 6,8x)",
    "https://www.instagram.com/p/DbDQNKeCHRc/ (Coucoo Cabanes, 6,8x)"
  ],
  "limites": ["Les partenariats et collaborations sont à classer à part dans les médianes (S2-M03) : même biais que F02, à un degré inconnu."],
  "sources": [
    "lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md",
    "instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=24"
  ]
}
```

## F06. Contenu saisonnier ou daté (B)

```json
{
  "id": "F06",
  "nom": "Contenu saisonnier ou daté",
  "plateforme": "instagram",
  "objectif": "portee",
  "objectif_secondaire": ["partage"],
  "structure": [
    "Accroche avec la date ou la saison (formule A19 « La date limite »).",
    "Plans du lieu dans l'ambiance de saison.",
    "Information pratique datée.",
    "Appel avant la date. L'urgence doit être vraie."
  ],
  "structure_statut": "proposée",
  "preuve": "B",
  "observe": "5 comptes au-dessus de 3x, en Reel et en carrousel : Beautiful Destinations (35,6x ; 34,3x ; 33,8x, Noël), Le Bonbon (30,8x, événement), Hipcamp (14,2x, Perséides avec dates), Sortir à Paris (10,4x ; 5,7x ; 4,4x ; 3,4x), Weekendesk (3,0x).",
  "exemples": [
    "https://www.instagram.com/reel/DfPEcFqMawt/ (Sortir à Paris, 10,4x)",
    "https://www.instagram.com/reel/DfPywy5GBl3/ (Weekendesk, 3,0x)"
  ],
  "limites": ["Effet de saison : un multiple de décembre ne se compare qu'à un multiple de décembre."],
  "sources": [
    "lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md",
    "instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=19",
    "nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md (Step 3, calendrier saisonnier)"
  ]
}
```

## F07. Carrousel texte « qui parle » : phrase, mème, prise de position (B, ton à adapter)

```json
{
  "id": "F07",
  "nom": "Carrousel texte « qui parle » (phrase, mème, prise de position)",
  "plateforme": "instagram",
  "objectif": "partage",
  "objectif_compilation": "partage et commentaires",
  "structure": [
    "Diapo 1 : une phrase courte qui se suffit.",
    "Diapos suivantes : développement en 2 à 4 phrases.",
    "Dernière diapo : question ouverte au public."
  ],
  "structure_statut": "proposée",
  "preuve": "B",
  "observe": "5 comptes au-dessus de 3x : Je m'en bats le clito (20,4x ; 17,1x ; 14,3x), Madmoizelle (19,1x ; 10,4x), Gang du clito (8,1x ; 6,5x ; 6,3x), Passage du Désir (4,5x), Coucoo Cabanes (3,5x).",
  "exemples": [
    "https://www.instagram.com/p/DbdrcbKjEbg/ (Passage du Désir, 4,5x)",
    "https://www.instagram.com/p/DbF5S6oDZnf/ (Coucoo Cabanes, 3,5x)"
  ],
  "limites": [
    "La plupart des succès sont militants ou d'actualité sociale : le ton doit être adapté à la marque.",
    "Exemple Love'nSpa : complicité de couple, humour tendre, jamais militant ni explicite."
  ],
  "sources": ["lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md"]
}
```

## F08. Reel incarné en série, vlog (B, peu transposable)

```json
{
  "id": "F08",
  "nom": "Reel incarné en série (vlog)",
  "plateforme": "instagram",
  "transposable_note": "Avec renvoi vers YouTube.",
  "objectif": "portee",
  "objectif_secondaire": ["abonnes"],
  "structure": [
    "Une personne à l'écran, épisodes numérotés.",
    "Fin d'épisode : renvoi vers la suite (« la suite sur YouTube »)."
  ],
  "structure_statut": "observée dans les légendes seulement",
  "preuve": "B",
  "observe": "4 comptes au-dessus de 3x : Ben N'co (62,2x ; 14,4x ; 9,7x ; 9,2x ; 6,1x), Millesvoyages (49,0x ; 6,9x), Madmoizelle (27,8x), Bruno Maltor (3,9x).",
  "exemples": ["https://www.instagram.com/reel/DcL4im-ti9E/ (Ben N'co, 62,2x)"],
  "limites": [
    "Repose sur une personne à l'écran. Exemple Love'nSpa : publie sans visage à ce stade.",
    "Élément transposable sans visage : la série à épisodes."
  ],
  "sources": ["lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md"]
}
```

## F09. Reel avec appel « commentez pour recevoir le lien » (C)

```json
{
  "id": "F09",
  "nom": "Reel avec appel « commentez pour recevoir le lien »",
  "plateforme": "instagram",
  "objectif": "conversion",
  "objectif_compilation": "conversion et commentaires",
  "structure": [
    "Reel de visite (F01).",
    "Légende ouverte par l'appel : le premier mot est l'appel (accroche A63).",
    "Réponse automatique en message privé après le commentaire."
  ],
  "regle": "Réponse automatique uniquement via les outils officiels ou des partenaires agréés (S2-R03, à vérifier dans la documentation officielle).",
  "preuve": "C",
  "observe": "Un seul compte : AbracadaRoom (3,5x ; 3,2x).",
  "exemples": ["https://www.instagram.com/reel/DdDowLuOgdv/ (AbracadaRoom, 3,5x)"],
  "limites": ["Un seul compte : seuil B non atteint.", "Le multiple de commentaires est gonflé par la mécanique de l'appel, comme pour F02."],
  "sources": [
    "lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md",
    "Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md (Hand off)",
    "instagram-agent-skill@d03c56b:README.md (The fine print)"
  ]
}
```

## F10. Contenu éducatif sur le couple, avec une experte (C)

```json
{
  "id": "F10",
  "nom": "Contenu éducatif sur le couple, avec une experte",
  "plateforme": "instagram",
  "objectif": "enregistrement",
  "objectif_secondaire": ["partage"],
  "structure": [
    "Reel avec une experte, ou carrousel « N façons de… ».",
    "Statistique toujours sourcée (accroche A23)."
  ],
  "garde_fou": "Exemple Love'nSpa : ton romantique et sensuel, jamais explicite ; sujets possibles : complicité, temps à deux, rituels.",
  "preuve": "C",
  "observe": "2 comptes seulement (seuil B non atteint) : YESforLOV (17,7x, Reel avec sexologue ; 10,8x, carrousel « 5 façons… »), Le Bonbon (5,3x, statistique sur les couples).",
  "limites": ["Deux comptes : un de plus au-dessus de 3x suffirait pour le niveau B."],
  "sources": ["lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md"]
}
```

## F11. Avant / après à l'écran (C)

```json
{
  "id": "F11",
  "nom": "Avant / après à l'écran",
  "plateforme": "instagram",
  "transposable": ["tiktok"],
  "objectif": "portee",
  "structure": [
    "Plan 1 : l'avant (exemple Love'nSpa : chambre en journée).",
    "Coupe franche.",
    "Plan 2 : l'après (exemple : bougies, spa allumé).",
    "Une phrase sur un seul levier."
  ],
  "duree": "non précisée par la source",
  "preuve": "C",
  "exemples": ["accroche A13"],
  "limites": ["Aucune mesure publiée par les sources."],
  "sources": [
    "instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=13",
    "Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json#id=13",
    "nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md (format Transformation)"
  ]
}
```

## F12. Démonstration à froid (C)

```json
{
  "id": "F12",
  "nom": "Démonstration à froid",
  "plateforme": "instagram",
  "transposable": ["tiktok"],
  "objectif": "portee",
  "structure": [
    "La vidéo commence au milieu du geste (exemple : couvercle qu'on soulève, eau qui se met à bouillonner).",
    "Résultat visible tout de suite.",
    "Si le résultat tarde : couper jusqu'à lui et montrer l'attente après."
  ],
  "preuve": "C",
  "exemples": ["accroche A18"],
  "limites": ["Aucune mesure publiée par les sources."],
  "sources": [
    "instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=18",
    "Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json#id=18"
  ]
}
```

## F13. POV, point de vue (C)

```json
{
  "id": "F13",
  "nom": "POV (point de vue)",
  "plateforme": "tiktok",
  "transposable": ["instagram"],
  "objectif": "portee",
  "structure": [
    "Texte à l'écran « POV : vous… » dès la première image.",
    "Caméra subjective qui avance dans le logement.",
    "Arrivée sur l'atout (exemple Love'nSpa : le spa)."
  ],
  "structure_statut": "proposée",
  "preuve": "C",
  "exemples": ["accroche A48"],
  "limites": ["Aucune mesure publiée par les sources."],
  "sources": [
    "rediumvex_viral-hooks-skill@e26b339:hooks-database.md#068",
    "nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md (Hook Strategies)",
    "nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md (TikTok, Best formats)"
  ]
}
```

## F14. Adaptation d'une tendance, son ou format du moment (C)

```json
{
  "id": "F14",
  "nom": "Adaptation d'une tendance (son ou format du moment)",
  "plateforme": "tiktok",
  "transposable": ["instagram"],
  "objectif": "portee",
  "structure": [
    "Début du son ou du format tendance.",
    "« Moi : situation qu'on reconnaît. »",
    "« Aussi moi : la solution. »",
    "Démonstration.",
    "Appel discret."
  ],
  "regles": [
    "Vérifier que le son est dans la bibliothèque commerciale si le compte est entreprise (S2-R06, à vérifier dans la documentation officielle).",
    "Écarter les tendances qui ne collent pas à la marque (S2-M18)."
  ],
  "preuve": "C",
  "exemples": ["accroche A60"],
  "limites": ["Une tendance est très locale et courte : à revérifier le jour de la production."],
  "sources": [
    "nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md (Template 3)",
    "Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md"
  ]
}
```

## F15. Avis client ou contenu client repris (C)

```json
{
  "id": "F15",
  "nom": "Avis client ou contenu client repris",
  "plateforme": "instagram",
  "transposable": ["tiktok"],
  "objectif": "conversion",
  "objectif_compilation": "conversion (preuve sociale)",
  "structure": [
    "L'avant : le besoin du client (exemple Love'nSpa : le besoin du couple).",
    "L'expérience.",
    "L'après.",
    "Nom et accord du client."
  ],
  "preuve": "C",
  "exemples": ["accroches A25, A44"],
  "limites": [
    "L'accord du client est obligatoire avant reprise.",
    "« 2 fois par semaine » dans la source est un exemple, pas une mesure."
  ],
  "sources": [
    "nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-branding/SKILL.md (Customer Transformation)",
    "nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-social-media-marketing/SKILL.md (UGC)",
    "nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md (UGC Repost)"
  ]
}
```

## F16. Épingle Pinterest verticale (C)

```json
{
  "id": "F16",
  "nom": "Épingle Pinterest verticale",
  "plateforme": "pinterest",
  "objectif": "conversion",
  "objectif_compilation": "trafic vers le site (recherche) ; rangé en « conversion », l'énumération du contrat n'ayant pas de valeur « trafic »",
  "structure": [
    "Visuel vertical 2:3, texte en surimpression, couleurs vives (S2-R09, à vérifier).",
    "Mots-clés dans le titre, la description et le nom du tableau.",
    "Variante multipage pour les tutoriels pas à pas (« Idea Pins » dans la source, nom de format à vérifier)."
  ],
  "preuve": "C",
  "limites": ["Seule source Pinterest du corpus ; aucune mesure."],
  "sources": ["nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md (Pinterest)"]
}
```

## F17. Face à face, comparatif tranché (C)

```json
{
  "id": "F17",
  "nom": "Face à face (comparatif tranché)",
  "plateforme": "instagram",
  "transposable": ["tiktok"],
  "objectif": "partage",
  "objectif_compilation": "commentaires ; rangé en « partage », l'énumération du contrat n'ayant pas de valeur « commentaires »",
  "structure": [
    "Annonce des deux options.",
    "Critères montrés.",
    "Verdict net, jamais « les deux ont du bon »."
  ],
  "preuve": "C",
  "exemples": ["accroche A17"],
  "limites": ["Aucune mesure publiée par les sources."],
  "sources": [
    "instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=17",
    "Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json#id=17"
  ]
}
```

## F18. Coulisses (C)

```json
{
  "id": "F18",
  "nom": "Coulisses",
  "plateforme": "instagram",
  "transposable": ["tiktok"],
  "transposable_note": "Stories et Reels sur Instagram.",
  "objectif": "conversion",
  "objectif_compilation": "confiance ; rangé en « conversion », l'énumération du contrat n'ayant pas de valeur « confiance »",
  "structure": [
    "Préparation réelle avant l'arrivée d'un client (exemple Love'nSpa : préparation d'un logement).",
    "Aucun visage nécessaire."
  ],
  "structure_statut": "proposée",
  "preuve": "C",
  "exemples": ["accroche A59"],
  "limites": ["Aucune mesure publiée par les sources."],
  "sources": [
    "nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-social-media-marketing/SKILL.md (Behind-the-Scenes Content)",
    "rediumvex_viral-hooks-skill@e26b339:hooks-database.md#100"
  ]
}
```

## Tenir la bibliothèque à jour

- Une fiche nouvelle entre en C, avec au moins une source au format `dépôt@commit:chemin` ou le chemin d'un fichier de `social/donnees/<id>/`.
- Passage en B : relever les comptes et multiples dans `observe`, après hygiène S2-M03.
- Passage en A ou déclassement : ajouter un champ `mesures` (date de l'audit S8, nombre de publications, multiple médian) et une ligne au journal.
- Valider chaque fiche modifiée contre le contrat : `social/contrats/valider.py`, fonction `erreurs(fiche, "fiche_format")`.
