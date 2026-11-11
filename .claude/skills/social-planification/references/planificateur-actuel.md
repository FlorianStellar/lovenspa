# Planificateur actuel : `social/s4_planification/planifier.py`

Description fidèle du code (fonctions `main`, `plan_week`, `eligible`, `score`, `pick_region`, `match_selection`, `temps_fort`, `concours_dates`, `utm`, `to_markdown`). Ce qui n'est pas écrit ici n'est pas codé.

## Commande

```
python3 -m social.s4_planification.planifier --marque <id> --plateforme <p> [--semaine AAAA-MM-JJ] [--out <fichier.json>]
```

- `--marque` : sinon variable `SOCIAL_MARQUE` ; sans les deux, arrêt (aucune marque par défaut).
- `--plateforme` : `instagram` par défaut. Lit `social/marques/<id>/strategie_<p>.json` ; fichier absent = arrêt.
- `--semaine` : date de départ, ramenée au lundi de sa semaine. Par défaut : lundi de la semaine suivante.
- `--out` : par défaut `social/donnees/<id>/<p>/plans/plan-<lundi>.json`. La vue lisible est écrite à côté (`.md`) et affichée. Un plan existant pour la même semaine est écrasé.
- Le plan est validé contre le contrat `plan` (cases conformes à `case`) avant écriture ; non conforme = arrêt.

## Entrées

| Fichier | Contenu attendu | Absent |
|---|---|---|
| `strategie_<p>.json` | Voir la skill social-strategie, `references/format-strategie.md`. | arrêt |
| Catalogue S3 (`Catalogue(m).toutes()`, Shopify) | Offres (contrat `offre`) avec `actif`, `prix_a_partir_de`, `medias`, `region`, `ville` ou `ville_reference`, `ambiance`, `equipements`, `equipements_non_citables`, `handle`, `url`, `type`. | erreur de connexion |
| `social/donnees/<id>/<p>/publies.json` | Historique écrit par S7 : `date`, `handle`, `region`, `moteur`. | liste vide |
| `social/donnees/<id>/<p>/partenaires.json` | Partenaires : `handle`, `accord_concours`, `nuits_offertes`. | liste vide |

## Algorithme

1. Rotation : sont « récents » les produits publiés à partir de (lundi − `rotation_logement_jours`). Les régions « utilisées » sont celles des publications des 8 dernières semaines.
2. Vivier : produits éligibles, c'est-à-dire tous ces critères à la fois : actif ; prix « à partir de » connu ; au moins 3 médias ; région connue ; ville ou ville de référence connue ; ambiance dans `ambiances_autorisees` ; aucun équipement non citable ; au moins un équipement de `equipements_phares` ; pas récent. Un produit sans prix est exclu, il ne bloque pas une case.
3. Une case par entrée de `semaine`, dans l'ordre : date = lundi + `jour`, heure = `heure_publication`, plateforme, moteur, format, `temps_fort` = thème de la période qui contient la date (dates `MM-JJ`, période à cheval sur le Nouvel An gérée), statut `A_PRODUIRE`.
4. Case `lieu` : région = celle qui maximise poids ÷ (1 + nombre d'utilisations), parmi les régions qui ont encore un produit éligible non pris ; égalité départagée par ordre alphabétique. Produit = celui qui a le plus d'équipements phares ; égalité départagée par un hachage stable de (semaine, handle), donc reproductible. Le produit et la région sont marqués pris. Aucun candidat : `BLOQUE` et alerte « aucun logement éligible ».
5. Case `selection` un jour de semaine de concours : si une date de concours (`temps_forts[].concours`) tombe entre le lundi et le dimanche, et qu'au moins un partenaire a `accord_concours` vrai et `nuits_offertes` > 0, la case devient `concours` : partenaire choisi de façon stable par semaine, son produit cherché dans tout le catalogue (sans contrôle d'éligibilité ni de rotation), lien tracé `concours`. Produit introuvable : `BLOQUE` et alerte. Sans partenaire volontaire : la case reste une sélection et une alerte le signale.
6. Case `selection` : thèmes essayés à partir de l'index (numéro de semaine modulo nombre de thèmes) ; le premier qui réunit `taille_selection` produits éligibles non pris est retenu. Filtres : `region` (région choisie comme en 4, parmi toutes les régions du vivier), `prix_max`, `equipement`, `type`. Produits classés comme en 4. Titre rempli avec `{n}`, `{region}`, `{prix}`. Lien tracé vers `site + liens.selection`. Aucun thème possible : `BLOQUE` et alerte.
7. Case `couple` : thème = `couple[numéro de semaine modulo nombre de thèmes]`, aucune offre, lien tracé vers `site + liens.couple`.
8. Lien tracé : URL + `?` ou `&` + gabarit `utm` rempli avec le moteur et la date de la case.
9. Sortie : `semaine`, `plateforme`, `genere_le`, `catalogue_eligible` (taille du vivier), `cases`, `alertes`.

## Ce que le code ne fait pas

- Ne lit ni le brief mensuel, ni le bilan S8, ni les plans précédents (pas de calendrier permanent).
- Ne contrôle ni jours fériés, ni fin de vente, ni horaire passé, ni thème repris sous quinze jours, ni plafond d'offre, ni alternance des types.
- Ne vérifie ni disponibilité sur les dates, ni stock.
- Ne produit ni angle, ni formule d'accroche, ni brief vidéo, ni déclinaison, ni étiquette « contenu IA ».
- Ne gère que les statuts `A_PRODUIRE` et `BLOQUE` (contrat `case`) et les moteurs `lieu`, `selection`, `concours`, `couple`.
- Une seule heure pour toutes les cases ; pas de stories.
- Le texte de l'alerte de concours cite `data/partenaires.json` ; le fichier lu est `social/donnees/<id>/<p>/partenaires.json`.

## Exemple (lovenspa), semaine du 16/11/2026

`social/donnees/lovenspa/instagram/plans/plan-2026-11-16.md` : 592 offres éligibles après rotation ; lundi Reel « lieu » Île-de-France ; mardi carrousel « 6 nuits avec spa privatif à moins de 150 € » ; jeudi Reel « lieu » Provence-Alpes-Côte d'Azur ; vendredi carrousel couple ; dimanche Reel « lieu » Pays de la Loire ; aucune alerte.
