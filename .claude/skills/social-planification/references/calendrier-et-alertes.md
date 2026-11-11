# Calendrier permanent, horizons, rotation et alertes (S4)

Contient des éléments de knowledge-work-plugins (Apache-2.0) : calendrier permanent (S4-02), horizons (S4-03), contrôle du plan (S4-17), lecture du bilan (S4-28), produits disponibles (S4-16), modifiés et traduits en français par Stellar Projects, 2026. Provenance : `../SOURCES.md`.

État : tout ce fichier est manuel (à outiller), sauf les lignes marquées « codé ».

## Calendrier permanent (S4-02)

À chaque exécution, ouvre le calendrier existant et affiche d'abord trois lignes :

1. Publiés depuis la dernière exécution (`publies.json`).
2. Encore programmés.
3. Premier jour sans contenu.

Puis étends à partir de ce trou. Ne reconstruis jamais un calendrier depuis zéro.

Aujourd'hui : un fichier de plan par semaine (`plans/plan-<lundi>.json`), sans fichier de calendrier. À faire à la main : lister les plans existants, `publies.json`, et ne jamais régénérer une semaine dont une case est déjà produite.

## Trois horizons (S4-03)

| Horizon | Durée | État |
|---|---|---|
| Plan détaillé | La semaine | codé (`planifier.py`) |
| Horizon visible | 30 jours ; 60 ou 90 jours seulement pour une raison datée (temps fort, lancement) | manuel : lancer `planifier.py` avec `--semaine` sur les lundis suivants et `--out` vers un fichier d'essai |
| File programmée | Une à deux semaines | S7 |

Laisse des trous pour le spontané : une réaction à l'actualité se publie en direct, pas en file.

## Rotation (S4-18)

| Objet | Règle | État |
|---|---|---|
| Produit | Rotation de la stratégie (`rotation_logement_jours` ; exemple (lovenspa) : 56 jours) | codé |
| Produit dans la semaine | Un produit au plus une fois par plan | codé |
| Thème ou angle | Pas repris dans les quinze jours | manuel (à outiller) ; les thèmes de sélection et de couple tournent par numéro de semaine, sans lecture de l'historique |
| Contenu permanent qui a bien marché | Peut revenir après trois à six mois, rafraîchi | manuel (à outiller) |

## Produits (S4-16)

| Critère | État |
|---|---|
| Éligibilité de la stratégie (actif, prix, médias, lieu, ambiance, équipements) | codé |
| Disponible sur la période (dates d'un temps fort) | manuel (à outiller) ; donnée absente : le signaler dans les alertes |
| Stock faible : ne pas pousser, proposer un équivalent | manuel (à outiller) |
| Priorité aux produits « à pousser » du brief mensuel S1, exclusion des produits « en pause » | manuel (à outiller) |

## Alertes (S4-17)

| Alerte | État |
|---|---|
| Aucun logement éligible pour une case `lieu` | codé |
| Aucune sélection possible | codé |
| Logement du partenaire de concours introuvable | codé |
| Concours prévu sans partenaire volontaire : sélection publiée à la place | codé |
| Deux publications le même jour pour le même produit | manuel (à outiller) ; dans un même plan, un produit n'est pris qu'une fois |
| Une offre qui tombe un jour férié | manuel (à outiller) |
| Une publication de vente après la fin de la vente | manuel (à outiller) |
| Un horaire déjà passé | manuel (à outiller) |
| Un thème déjà publié dans les quinze derniers jours | manuel (à outiller) |
| Plus de 20 % d'offres (S4-11) | manuel (à outiller) |
| Deux types identiques d'affilée (S4-09) | manuel (à outiller) |

## Bilan avant planification (S4-28)

Lis le bilan de la période précédente (dernier `audit-*.md`, journal). Garde la forme de ce qui a marché, change le sujet. N'invente pas une nouvelle stratégie pour « en faire plus » : tout changement de grille passe par la skill social-strategie.
