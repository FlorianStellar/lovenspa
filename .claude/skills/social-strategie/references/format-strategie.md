# Fichier de stratégie : `marques/<id>/strategie_<plateforme>.json`

Contrat : `social/contrats/strategie.schema.json`. Lu par S4 (`social/s4_planification/planifier.py`), S5, S6, S7, S8. Toute modification de ce fichier est « Jamais seul » : proposition écrite, validation humaine.

## Champs requis par le contrat

| Champ | Type | Lu par | Rôle |
|---|---|---|---|
| `plateforme` | `instagram`, `tiktok` ou `pinterest` | S4 | Plateforme de la stratégie, recopiée dans chaque case. |
| `objectifs_31_05_2027` | objet | S8 | Objectifs chiffrés à l'échéance. |
| `semaine` | liste de `{jour, moteur, format}` | S4 | Grille hebdomadaire. `jour` : 0 = lundi … 6 = dimanche. `moteur` : `lieu`, `selection`, `couple` (le contrat `case` admet aussi `concours`). `format` : `REELS`, `CAROUSEL`, `IMAGE`, `STORY`, `PIN`, `TIKTOK`. |
| `heure_publication` | `HH:MM` | S4, S7 | Heure unique de toutes les cases. |
| `rotation_logement_jours` | entier | S4 | Délai minimal avant de republier un même produit. |
| `ambiances_autorisees` | liste d'entiers | S4, S6 | Niveaux d'ambiance citables. |
| `regions_poids` | objet région -> poids | S4 | Pondération de la région des cases « lieu ». |
| `equipements_phares` | liste | S4 | Un produit éligible en a au moins un ; plus il en a, mieux il est classé. |
| `selections` | liste de `{titre, filtre}` | S4 | Thèmes de sélection, tournés chaque semaine. `titre` accepte `{n}`, `{region}`, `{prix}`. `filtre` : `region` (booléen), `prix_max`, `equipement`, `type`. |
| `couple` | liste de chaînes | S4 | Thèmes du moteur couple, tournés chaque semaine. |
| `temps_forts` | liste de `{debut, fin, theme, concours}` | S4 | Dates `MM-JJ`. Une période peut chevaucher le Nouvel An. `concours` : `MM-JJ`, liste de `MM-JJ` ou `null`. |
| `utm` | chaîne | S4 | Gabarit de lien tracé, avec `{moteur}` et `{date}`. |
| `liens` | objet | S4 | Chemins de la boutique pour `selection` et `couple`. |

## Champs lus par S4 sans être requis par le contrat

| Champ | Rôle |
|---|---|
| `taille_selection` | Nombre de produits d'une sélection. Absent : le planificateur échoue. |

## Champs libres

`note` (lien vers le document de stratégie validé, date de validation), `*_source` (provenance de chaque valeur chiffrée, par exemple `regions_poids_source`, `ambiances_source`). Toute valeur chiffrée porte sa source.

## Exemple (lovenspa)

`social/marques/lovenspa/strategie_instagram.json` : 5 cases (Reels « lieu » lundi, jeudi, dimanche ; carrousel « sélection » mardi ; carrousel « couple » vendredi), 18:30, rotation de 56 jours, ambiances 1 et 2, 8 sélections de 6 logements, 8 thèmes couple, 7 temps forts, objectifs au 31/05/2027 (20 000 abonnés, 70 % de portée hors abonnés, 1 % de partages par portée hors concours, 7 s de visionnage moyen des Reels).

## Avant d'appliquer une modification validée

1. Vérifier que chaque champ requis existe et garde son type (fonction `erreurs(objet, "strategie")` de `social/contrats/valider.py` ; pas de commande dédiée : manuel (à outiller)).
2. Lancer `python3 -m unittest discover -s social/tests -t .`.
3. Générer un plan d'essai : `python3 -m social.s4_planification.planifier --marque <id> --plateforme <p> --out <fichier temporaire>` et lire ses alertes.
