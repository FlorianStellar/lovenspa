# Règles de plateforme utiles à la diffusion

Toutes ces règles sont **à vérifier dans la documentation officielle** avant usage. Elles viennent des sources compilées, qui le disent elles-mêmes : si la plateforme dit autre chose au moment de la lecture, la plateforme a raison. Aucune n’est codée comme vérité dans `instagram.py`, sauf le quota lu en direct par l’API (`content_publishing_limit`).

| # | Règle | Plateforme | Source | Statut |
| --- | --- | --- | --- | --- |
| P-01 | Hashtags plafonnés à 5 par publication depuis décembre 2025. | IG | `instagram-agent-skill@d03c56b:README.md` ; note sourcée de `regles.json` | à vérifier dans la documentation officielle |
| P-02 | L’API Content Publishing est réservée aux comptes professionnels et demande une application Meta, une Page liée, un jeton longue durée et une revue d’application. | IG | `instagram-agent-skill@d03c56b:README.md` | à vérifier dans la documentation officielle |
| P-03 | Automatiser publication, commentaires, abonnements ou messages par un navigateur ou un outil tiers non agréé enfreint les conditions d’utilisation et entraîne un blocage d’actions. | IG, TT | `instagram-agent-skill@d03c56b:README.md` ; `Explo38/reels-tiktok-fr@a2281b6:README.md` | à vérifier dans la documentation officielle |
| P-12 | Programmation native pour les comptes professionnels, ou via Meta Business Suite. | IG | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-publication/SKILL.md` | à vérifier dans la documentation officielle |
| P-13 | TikTok Studio sur ordinateur programme à environ 10 jours, comptes Créateur ou Entreprise. | TT | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-publication/SKILL.md` | à vérifier dans la documentation officielle |
| P-14 | Étiquette « contenu généré par IA » à activer pour voix de synthèse ou images générées. | IG, TT | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-publication/SKILL.md` | à vérifier dans la documentation officielle |
| P-15 | Les conditions d’utilisation interdisent robot connecté au compte, script non officiel, saisie du mot de passe par un tiers. | IG, TT | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-publication/SKILL.md` | à vérifier dans la documentation officielle |
| P-16 | Zone visible d’une légende avant « plus » : environ 125 caractères sur IG, 80 à 100 sur TT. | IG, TT | `Explo38/reels-tiktok-fr@a2281b6:README.md` ; `regles.json` (`max_visible`, non sourcé) | à vérifier dans la documentation officielle |
| P-17 | Metricool : offre gratuite limitée ; accès API réservé aux offres payantes. | IG, TT | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-publication/SKILL.md` | à vérifier dans la documentation officielle |

Pinterest : aucune source compilée ne donne de règle propre à Pinterest. Tout reste à établir depuis la documentation officielle.

## Éléments des sources écartés

- Voie B (préparer les posts dans le planificateur natif avec un outil de navigation) : écartée, l’automatisation de navigateur est exclue (S7-01).
- Voie C (kit manuel) : conservée seulement comme statut « à faire à la main » (S7-04).
- Accord humain par lot, confirmation avant le clic final, récapitulatif à valider : remplacés par les garde-fous de `instagram.py` et le récapitulatif au journal (C-07, S7-14).
