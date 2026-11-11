# Gabarits de case et de brief (S4)

Contient des éléments de knowledge-work-plugins (Apache-2.0) : ligne de calendrier (S4-13), règles de prix et d'allégations (S4-15), modifiés et traduits en français par Stellar Projects, 2026. Provenance : `../SOURCES.md`.

## Créneau : un angle, pas un sujet (S4-12)

Chaque créneau porte : le thème, l'angle précis tiré du réel, le format, la ou les plateformes, le numéro et le nom de la formule d'accroche (bibliothèque S2).

- « Les spas » n'est pas un plan.
- « Ce logement à {ville} où le spa est dans la chambre » est une vidéo.

## Ligne de calendrier (S4-13)

| Champ | Codé dans le contrat `case` |
|---|---|
| ID | non (clé de fait : date + moteur, utilisée par S7) |
| Date | oui (`date`) |
| Heure par plateforme | une seule heure (`heure`) |
| Plateformes | une seule (`plateforme`) |
| Moteur | oui (`moteur`) |
| Format | oui (`format`) |
| Temps fort | oui (`temps_fort`) |
| Thème | oui (`theme`, sélection et couple) |
| Angle | non |
| Produits (identifiant boutique) | oui (`offres[].handle`) |
| Prix lu et date de lecture | prix oui (`offres[].prix_a_partir_de`) ; date de lecture : `genere_le` du plan |
| Formule d'accroche | non |
| Demande unique et lien tracé | lien oui (`lien`) |
| Déclinaisons prévues | non |
| Source si recyclage | non |
| Étiquette « contenu IA » (oui ou non) | non |
| À faire à la main | non |
| Statut | oui (`statut`, deux valeurs) |

Une déclinaison porte la référence de la ligne d'origine, pour ne jamais refaire un visuel existant. Les champs « non » sont à remplir à la main : manuel (à outiller). Le contrat `case` accepte des champs en plus (`additionalProperties`).

## Brief de production d'un créneau vidéo (S4-14)

| Partie | Contenu |
|---|---|
| En-tête | Plateforme, durée, format. |
| Accroche (0 à 3 s) | Image, son, texte à l'écran : les trois dès la première seconde. |
| Corps | Repères de temps et ce qui se passe. |
| Demande (3 à 5 dernières secondes) | Oral, texte, action. |
| Notes | Son, médias du catalogue à utiliser, graphismes. |

Structures au choix : problème-solution, liste, tutoriel, arc d'histoire, point de vue.

## Prix et allégations (S4-15)

- Le prix est copié tel que le catalogue le renvoie, relu à chaque brief, jamais repris d'une session précédente.
- « Avant, maintenant » seulement si un prix barré existe et dépasse le prix.
- Jamais « plus que quelques dates » sans donnée.
- Prix absent : la case passe en `BLOQUE`, sans estimation.
- Exemple (lovenspa) : prix « à partir de » par nuit.

## Statuts d'un créneau (S4-26)

| Statut | Sens | Contrat `case` |
|---|---|---|
| A_PRODUIRE | Case prête pour S5. | oui |
| BROUILLON | Texte ou visuel en cours (S5). | non |
| CONTROLE | En contrôle S6. | non |
| PRET | Contrôle S6 passé, dans la charte. | non |
| PROGRAMME | Programmé par S7. | non |
| PUBLIE | Publié (S7, `publies.json`). | non |
| MESURE | Mesuré (S8). | non |
| BLOQUE | Donnée manquante, avec une alerte qui dit laquelle. | oui |
| REJETE | Terminal. | non |

Le passage de CONTROLE à PRET dépend du contrôle S6 et de la charte d'autonomie, pas d'un accord. Les statuts absents du contrat ne sont pas suivis dans le plan : manuel (à outiller).

## Exemple (lovenspa) : case réelle

Lue dans `social/donnees/lovenspa/instagram/plans/plan-2026-11-16.json` : `date` 2026-11-16, `heure` 18:30, `plateforme` instagram, `moteur` lieu, `format` REELS, `temps_fort` « Offrir une nuit… », `region` Île-de-France, une offre, `lien` tracé, `statut` A_PRODUIRE.
