# Les trois boucles de rétroaction

Source : doc d'architecture « Système social média – Love'nSpa puis Stellar Fleet », sections S2 et S8 (cité par `social/README.md`). Aucune des trois boucles n'est codée : toutes sont manuel (à outiller). Le bilan de chaque boucle est écrit dans `social/donnees/<id>/<plateforme>/journal.md`.

## Boucle hebdomadaire : S8 -> S4 (pondérations)

- **Quand** : chaque lundi, sur la semaine complète précédente (lundi à dimanche), avec rappel des 4 dernières semaines.
- **Entrées** : instantané du jour, audit et audit par format, `publies.json`.
- **Sortie** : bilan hebdomadaire, avec par format et par moteur la taille du groupe, le score (médiane des vues du groupe ÷ médiane du compte), les médianes de partages ÷ portée et d'abonnements ÷ portée. Ajouter les pondérations proposées pour la semaine suivante.
- **Règle des pondérations** : rester à l'intérieur de la grille, des moteurs et de la cadence de la stratégie en vigueur. Monter ce qui dépasse 2x sur au moins 3 publications, sans dépasser ce que la grille permet ; ne rien conclure d'un groupe de moins de 3.
- **Effet attendu côté S4** : lire le bilan avant de planifier ; garder la forme de ce qui a marché, changer le sujet (S4-28).
- **Limite actuelle** : `social/s4_planification/planifier.py` n'a pas d'entrée de pondération venant de S8. Ses seuls poids sont ceux des régions, dans la stratégie (propriété de S1, non modifiable par S8). La transmission se fait donc par le journal, à lire par S4 : manuel (à outiller).

Gabarit de bilan :

```
## AAAA-MM-JJ : bilan hebdomadaire S8 -> S4
Source : snapshot-AAAA-MM-JJ.json ; audit-AAAA-MM-JJ.md ; audit-AAAA-MM-JJ-par-format.md
Périmètre : N publications du JJ/MM au JJ/MM (exclues : N de moins de 48 h, N concours à part)
Complétude : views n/N, reach n/N, shares n/N, saved n/N, follows n/N
Par format : FORMAT · n · score · partages/portée · abonnements/portée
Par moteur : MOTEUR · n · score · partages/portée · abonnements/portée (inconnu : n)
Pondérations proposées : …  (dans la grille en vigueur)
Non mesuré : …
```

## Boucle mensuelle : S8 -> S2 (fiches confirmées ou infirmées)

- **Quand** : une fois par mois, au moment de la veille complète (S2-M21).
- **Entrées** : bilans hebdomadaires du mois ; fiche de format (F01…) et formule d'accroche (A01…) de chaque publication, lues dans les paquets S5.
- **Sortie** : pour chaque fiche utilisée, nombre de publications, multiple médian, médianes de partages ÷ portée et d'enregistrements ÷ portée, et verdict :
  - confirmée : au moins 3 publications et multiple médian d'au moins 2x ;
  - infirmée : au moins 3 publications sans surperformance (seuil exact non fixé par la compilation : l'écrire) ;
  - pas assez de données : moins de 3 publications.
- **Effet attendu côté S2** : un format confirmé passe en preuve A ; un format infirmé perd sa priorité, avec la date écrite dans sa fiche (skill `social-veille`).
- Même lecture par formule d'accroche, dès que les paquets portent l'`id` de la formule.

## Boucle trimestrielle : S8 -> S1 (propositions validées par un humain)

- **Quand** : une fois par trimestre.
- **Entrées** : bilans mensuels du trimestre ; objectifs de la stratégie ; indicateurs S1-24 dans leur ordre.
- **Sortie** : propositions écrites. Pour chacune : ce qui change (objectif, moteur, cadence, format, temps fort), les chiffres qui la justifient, leur source (instantané daté, audit), la taille de l'échantillon, et ce qui n'a pas pu être mesuré (S1-25).
- **Validation** : aucune proposition ne s'applique sans validation humaine (skill `social-strategie`, charte « Jamais seul »). S8 ne modifie jamais la stratégie.
- Une proposition refusée n'est pas reproposée sans donnée nouvelle.

## Ce qu'il faut outiller, dans l'ordre

1. Écriture des objets `mesure` à partir de `enrich()`, avec validation par `social/contrats/valider.py`.
2. Exclusions (moins de 48 h, concours, sponsorisés, collaborations, épinglées) et seuil de 3 publications par groupe dans l'audit.
3. Jointure avec `publies.json` pour le score par moteur ; avec les paquets S5 pour la fiche de format et la formule d'accroche.
4. Cible de Reels lue dans la stratégie au lieu de la valeur par défaut du code.
5. Collecte de la durée des vidéos et des métriques de rétention, si l'API les expose (à vérifier dans la documentation officielle).
