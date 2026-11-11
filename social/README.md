# Système social média

Système en sous-systèmes, indépendant de la marque et de la plateforme. Architecture validée (J1) :
doc « Système social média – Love'nSpa puis Stellar Fleet » (https://claude.ai/artifact/Jeqa1t5M5XiwiDE1DS3U1f).

| Dossier | Rôle | Entrée → sortie (contrats/) |
|---|---|---|
| `marques/<id>/` | Tout ce qui est propre à une marque : identité et kit, correspondance du catalogue, règles, stratégie par plateforme, comptes de référence | → `kit_marque`, `strategie` |
| `contrats/` | Schémas JSON des objets échangés et validateur | — |
| `connecteurs/` | Accès aux API (Shopify, Instagram), remplaçables par Nango | — |
| `s2_connaissance/` | Veille et bibliothèque (formats, accroches, règles des plateformes) | comptes de référence → `fiche_format` |
| `s3_catalogue/` | Produits de la boutique → offres citables | boutique → `offre` |
| `s4_planification/` | Plan de la semaine | `strategie` + `offre` → `plan` / `case` |
| `s5_production/` | Textes rédigés par l'agent + visuels et vidéos | `case` → `paquet` |
| `s6_controle/` | Contrôle des textes et des faits | `paquet` → `verdict` |
| `s7_diffusion/` | Publication par API, garde-fous | `paquet` + `verdict` → `publication` |
| `s8_mesure/` | Instantanés et audit | API → `mesure` |
| `s9_communaute/` | Messages, modération, repartages (jalon J7) | — |
| `compilation/` | Compilation des skills analysées (jalon J2) | — |
| `donnees/<marque>/<plateforme>/` | Données d'exécution : plans, production, publications, instantanés, journal | — |

Commandes : `python3 -m social.<sous-système>.<module> --marque <id>` depuis la racine du dépôt.
Tests : `python3 -m unittest discover -s social/tests -t .` (dont les contrats et l'absence de données de marque dans le code).
