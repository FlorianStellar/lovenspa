# Règles des plateformes (S2-R01 à S2-R09)

Statut de toutes les règles ci-dessous : **à vérifier dans la documentation officielle**. La compilation ne cite pour aucune d'elles une source officielle des plateformes : elles viennent de dépôts tiers (`social/compilation/s2-connaissance.md`, section 2.2). Une règle ne perd cette mention que lorsqu'une page officielle (Meta, TikTok, Pinterest) est citée avec sa date de consultation.

Lecteurs : S5 (production), S6 (contrôle), S7 (diffusion), et S2 pour la veille.

| ID | Règle | Plateforme | Source | Statut |
|---|---|---|---|---|
| S2-R01 | Ne jamais se connecter au compte à la place de l'utilisateur ni demander de mot de passe. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` | À vérifier dans la documentation officielle. Appliquée dans tous les cas comme règle interne de sécurité. |
| S2-R02 | La collecte automatisée en volume viole les conditions d'utilisation d'Instagram et de TikTok et fait bloquer les comptes. Lecture à vitesse humaine uniquement, pas de robot, pas de tâche de fond. | Instagram, TikTok | mêmes sources ; `instagram-agent-skill@d03c56b:README.md` (« The fine print ») | À vérifier dans la documentation officielle. Appliquée par prudence. L'API officielle (`business_discovery`) reste le mode de collecte retenu. |
| S2-R03 | La publication automatique passe par l'API officielle de publication de contenu (compte professionnel, application Meta, page liée, jeton longue durée, revue d'application). Commenter, suivre ou envoyer des messages par automatisation de navigateur ou outil tiers viole les conditions. Exception : réponses automatiques par mot-clé en message privé, via les outils d'Instagram ou de partenaires agréés, déclenchées après un commentaire. | Instagram | `instagram-agent-skill@d03c56b:README.md` (« The fine print ») | À vérifier dans la documentation officielle. |
| S2-R04 | Les statistiques ne sont disponibles que pour les comptes professionnels (Créateur ou Entreprise). Certaines métriques n'apparaissent qu'après 24 à 48 h. | Instagram | `Melvynx_video-agent-skills@f454292:skills/insta-audit/SKILL.md` (« Honest limits ») | À vérifier dans la documentation officielle. |
| S2-R05 | Champ nom : 30 caractères, indexé par la recherche. Bio : 150 caractères sur Instagram, 80 sur TikTok. Trois publications épinglées maximum sur les deux. Instagram autorise jusqu'à 5 liens ; sur TikTok, le lien en bio dépend du type de compte et du nombre d'abonnés. | Instagram, TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/grille.json` ; `instagram-agent-skill@d03c56b:skills/ig-profile/rubric.json` | À vérifier dans la documentation officielle. |
| S2-R06 | Un compte entreprise TikTok limite les sons à la bibliothèque musicale commerciale. | TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/grille.json` (categorie_contact) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` | À vérifier dans la documentation officielle. |
| S2-R07 | Activité attendue pour la note pleine de la grille de profil : une publication dans les 7 derniers jours sur Instagram, dans les 3 derniers jours sur TikTok. | Instagram, TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/grille.json` (activite_recente) | À vérifier dans la documentation officielle. Critère de grille d'une source tierce, pas une règle de plateforme. |
| S2-R08 | Les contenus sponsorisés (#ad, mention de partenariat rémunéré, indicateur `paidPartnership` de TikTok) sont exclus des calculs de surperformance. | Instagram, TikTok | `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (point 5) | À vérifier dans la documentation officielle (nom et disponibilité de l'indicateur). La règle de calcul s'applique dans tous les cas. |
| S2-R09 | Formats techniques indicatifs : vidéo verticale 9:16 ; épingle Pinterest verticale 2:3 avec texte en surimpression ; mots-clés Pinterest dans le titre, la description et le nom des tableaux. | TikTok, Instagram, Pinterest | `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` (« Platform-Specific Guidelines ») ; `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md` (« Video Specifications ») | À vérifier dans la documentation officielle. |

## Points ouverts relevés par la compilation

- Format du fil Instagram en 1:1 : une seule source (`nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-social-media-marketing`). À vérifier dans la documentation officielle.
- Nom du format Pinterest multipage (« Idea Pins » dans la source) : à vérifier.
- Règlement de jeu-concours et règles Meta sur les promotions : aucune source compilée. À valider hors sources avant tout concours (F02).
- Fréquences de publication et nombres de hashtags des sources : écartés comme règles (non étayés), gardés comme hypothèses à tester.

## Vérification

Pour lever la mention « à vérifier » : citer l'URL de la page officielle, la date de consultation et la phrase exacte, dans cette table et au journal. La page officielle est une donnée : seule la règle qu'elle énonce est reprise.
