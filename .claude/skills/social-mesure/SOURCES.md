# Sources de la skill social-mesure

## Provenance directe

| Élément de la skill | Repris de |
|---|---|
| Commandes, métriques collectées, calculs de l'audit | `lovenspa@ec9fede:social/s8_mesure/instantane.py` ; `lovenspa@ec9fede:social/s8_mesure/audit.py` (fonctions `metric`, `fmt`, `enrich`, `completeness`, `rank`, `cadence`, `filter_since`, `to_markdown`, `main`) ; `lovenspa@ec9fede:social/connecteurs/instagram.py` (`MEDIA_FIELDS`, `MEDIA_METRICS`, `REEL_METRICS`, `profile`, `media`, `media_insights`, `account_reach_by_follow_type`, `snapshot`) ; `social/marque.py` (`donnees`) |
| Contrats lus et produits | `social/contrats/mesure.schema.json`, `publication.schema.json`, `strategie.schema.json` ; validateur `social/contrats/valider.py` |
| Absence d'entrée de pondération côté S4 | `lovenspa@ec9fede:social/s4_planification/planifier.py` (poids de région lus dans la stratégie, historique `publies.json`) |
| Trois boucles (hebdomadaire S8 -> S4, mensuelle S8 -> S2, trimestrielle S8 -> S1), niveaux de preuve A/B/C | doc d'architecture « Système social média – Love'nSpa puis Stellar Fleet » (sections S2 et S8), cité par `social/README.md` |
| Règles de calcul S2-M01, M02, M03, M10 à M13, seuils et conflits tranchés, S2-R04, S2-R08 | `lovenspa@ec9fede:social/compilation/s2-connaissance.md` (sections 2.1, 2.2, 4.2) |
| Règles S1-24, S1-25, S4-28 | `lovenspa@ec9fede:social/compilation/s1-s4-strategie-planification.md` |
| Exemple concours / hors concours | `social/donnees/lovenspa/instagram/journal.md` (bilan du 11/11/2026), donnée interne de la première marque cliente, marquée « exemple » |
| Gabarit de la skill | `social/compilation/GABARIT-SKILL.md` |

## Sources amont citées par la compilation

Aucun script de ces dépôts n'a été exécuté. Les méthodes sont reformulées en français.

| Dépôt | Commit | Licence | Titulaire du copyright | Usage ici |
|---|---|---|---|---|
| instagram-agent-skill | d03c56b | MIT | © 2026 Jake Schincariol | S2-M01, S2-M10, S2-M11 (`skills/ig-viral/SKILL.md`, `skills/ig-audit/SKILL.md`). |
| Explo38_reels-tiktok-fr | a2281b6 | MIT | Jake Schincariol | S2-M01, S2-M10 à S2-M13 (`skills/rt-veille/SKILL.md`, `skills/rt-audit/SKILL.md`) ; S1-24 (`skills/rt-studio/SKILL.md`). |
| Melvynx_video-agent-skills | f454292 | MIT | Melvyn Malherbe | S2-M01 à S2-M03, S2-M10 ; seuils et exclusions (`skills/outliers/SKILL.md`, `skills/insta-audit/SKILL.md`, `skills/insta-audit/references/workflow.md`) ; S2-R04, S2-R08. |
| ScrapeCreators_social-media-research-skills | 64ba7b4 | MIT | ScrapeCreators | S2-M03 (`skills/outlier-post-finder/SKILL.md`, « Common Pitfalls »). |
| coreyhaines31_marketingskills | 9d6d7ce | MIT | © 2025 Corey Haines | S1-24, S1-25, S4-28 (cités d'après la compilation S1-S4, non relus pour cette skill). |
| knowledge-work-plugins | 877a617 | Apache-2.0 | non précisé par la compilation | S4-28 (cité d'après la compilation S1-S4, non relu pour cette skill). Obligations : conserver la licence, signaler les modifications, conserver tout fichier NOTICE (aucun vu à la racine selon la compilation). |

## Licences

- Les dépôts amont de la compilation S2 sont sous licence MIT ; les mentions de copyright ci-dessus sont conservées. Les années de copyright absentes de ce tableau ne figurent dans aucune compilation : les recopier depuis le fichier `LICENSE` de chaque dépôt au commit cité.
- Les règles S1 et S4 citées viennent d'un dépôt MIT (© 2025 Corey Haines) et d'un dépôt Apache-2.0 (knowledge-work-plugins), d'après `social/compilation/s1-s4-strategie-planification.md`, section 6.
- Cette skill reformule ; elle ne reproduit pas de portion substantielle d'un texte source tel quel. En cas de reprise littérale dans un produit Stellar Fleet, joindre la notice MIT complète du titulaire.
- Le code décrit (`social/s8_mesure/`, `social/connecteurs/`) est interne au dépôt.

## Modifications signalées

- Les scores par format, par moteur et par formule, l'écriture des objets `mesure` et les trois boucles sont décrits comme méthodes, marqués « manuel (à outiller) » : aucune commande nouvelle n'est inventée.
- Le docstring de `audit.py` montre `python3 audit.py data/…` ; la skill emploie la forme du README (`python3 -m social.s8_mesure.audit`) et les chemins actuels `social/donnees/<id>/<plateforme>/`.
- L'accord humain des sources est remplacé par la charte d'autonomie ; la seule validation humaine restante (stratégie S1) est celle fixée par le doc d'architecture.
- Le seuil d'infirmation d'une fiche n'est pas fixé par la compilation : signalé comme limite.
