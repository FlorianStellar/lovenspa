# Indicateurs, mécanismes et sources (S1)

## Ordre de lecture (S1-24)

| Rang | Indicateur | Source | Outil |
|---|---|---|---|
| 1 | Rétention à 3 s | API de la plateforme | non mesuré par l'instantané actuel : manuel (à outiller) |
| 1 | Visionnage moyen des vidéos | API Instagram | instantané et audit S8 |
| 2 | Partages par portée | API Instagram | audit S8 (`partages_portee`) |
| 3 | Enregistrements par portée | API Instagram | audit S8 (`enregistrements_portee`) |
| 4 | Abonnements par portée | API Instagram | audit S8 (`abonnements_portee`) |
| 5 | Clics tracés | liens UTM, statistiques de la boutique | manuel (à outiller) |
| 6 | Part de portée hors abonnés | API Instagram (portée par type d'abonné) | instantané S8 |
| — | « J'aime » | API | ne sert pas à décider |

Commandes : `python3 -m social.s8_mesure.instantane --marque <id>`, puis `python3 -m social.s8_mesure.audit social/donnees/<id>/<plateforme>/snapshot-AAAA-MM-JJ.json --par-format --md <sortie.md>`.

Une métrique absente d'une publication est exclue du calcul et comptée dans la complétude de l'audit : jamais remplacée par zéro ni estimée.

## Mécanisme et indicateur avancé (S1-22)

Chaque action écrite dans la stratégie porte :

| Rubrique | Exemple de forme |
|---|---|
| Action | Ce qui change dans la grille, le moteur ou l'angle. |
| Mécanisme | Pourquoi cela devrait marcher. |
| Indicateur avancé | Ce qui bouge en premier (rétention à 3 s, partages par portée…). |
| Indicateur final | Objectif de la stratégie concerné. |
| Critère d'arrêt | « Si [indicateur] reste sous [seuil] après [durée], alors [action]. » |

Sans mécanisme nommable, c'est une expérience : elle porte un critère d'arrêt. « Publier plus et espérer » n'est pas une action.

## Indicateur non mesurable (S1-25)

Écrire : indicateur, pourquoi il n'est pas mesurable aujourd'hui, travail de mesure à faire, qui le porte. Il reste une décision ouverte dans le journal jusqu'à ce que la mesure existe.
