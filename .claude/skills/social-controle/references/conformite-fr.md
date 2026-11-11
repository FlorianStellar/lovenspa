# Conformité française des textes (S6-25 à S6-31, S6-37)

Statut : règles compilées le 11/11/2026 depuis `copy-machine` (skill interne de Stellar Projects) et `coreyhaines31_marketingskills@9d6d7ce`. Provenance détaillée : `../SOURCES.md` ; compilation : `social/compilation/s6-s7-s9-controle-diffusion-communaute.md`, section 2.1 (ajout du 11/11/2026).

Les articles de loi sont ceux que cite `copy-machine:references/compliance-fr.md`. Ils n’ont pas été vérifiés sur Légifrance : à vérifier avant de les citer dans un document externe. Ce fichier n’est pas un avis juridique.

Mode d’emploi :

- S’applique à tout texte contrôlé : légende, cartons, diapos, réponses et messages de S9 (S6-23).
- Un risque de conformité est de gravité haute (S6-10) : le paquet est refusé tant que le texte n’est pas corrigé. Le code cible `CONFORMITE` n’automatise aujourd’hui que le superlatif sur un logement ou un prix (S6-09) ; le reste est manuel (à outiller).
- « Justificatif fourni » = une donnée de l’offre (S3), des données datées de la case, ou une preuve datée de la marque. Jamais un souvenir, une page web lue au passage ou une affirmation du site sans justificatif.
- Règles de plateforme (politiques Meta, TikTok, Pinterest) : seule référence, `.claude/skills/social-veille/references/regles-plateformes.md` (S2).

## 1. Allégations interdites sans justificatif (S6-25)

La source cite les pratiques commerciales trompeuses (Code de la consommation, art. L121-1 et suivants).

| Allégation | Exemple à refuser | Correction |
| --- | --- | --- |
| Urgence ou rareté fictive | « Plus que N nuits ! », « Dernières heures » | Retirer, ou citer l’échéance réelle des données (section 2). |
| Faux avis, avis réécrit, note ou nombre d’avis non vérifié, témoignage inventé | une note et un nombre d’avis sans source | Retirer ; `{{à compléter}}` si l’avis doit figurer. |
| Prix barré sans prix de référence réel | un ancien prix barré à côté du prix de l’offre | Interdit : le contrat `offre` ne porte aucun prix de référence (section 4). |
| Label, certification, « fabriqué en », garantie non attestés | « Satisfait ou remboursé » | Retirer si l’offre ne le dit pas. |
| Superlatif absolu non prouvé | « n°1 », « le meilleur », « le moins cher » | Remplacer par le fait (« spa privatif, jamais partagé ») ou retirer. |
| Allégation de santé ou thérapeutique | « Le sauna soigne le stress » | Retirer. |

Exemple Love’nSpa : « Plateforme N°1 de la Love Room » est une affirmation du site sans justificatif (`copy-machine:brands/lovenspa.md`, Preuves) : interdite tant qu’un justificatif n’est pas fourni. La production consigne le refus et la preuve qui le lèverait (S5-75).

## 2. Urgence et échéances (S6-26, S6-27)

Une échéance implicite est une urgence : « à temps pour Noël », « avant le 15 ». Elle n’est permise que si la date limite réelle (commande, émission d’une carte cadeau, fin d’un concours) figure dans les données de la case. « Une idée cadeau pour Noël » n’est pas une urgence.

Liste de détection (reprise de `copy-machine:scripts/copy_lint.py`, `URGENCY` et `SUPERLATIVES`, sans exécuter le script) :

- Urgence : « plus que N » ; « dernier, dernière, derniers, dernières » suivi de « heure(s) », « jour(s) », « place(s) », « pièce(s) », « exemplaire(s) », « chance » ; « dépêchez » ; « vite » ; « stock limité » ; « offre limitée » ; « quantité(s) limitée(s) » ; « avant qu’il ne soit trop tard » ; « ne ratez pas » ; « expire bientôt » ; « à temps pour » ; « avant » suivi de « Noël », « la Saint », « le » et un chiffre, « le Black Friday », « dimanche », « minuit », « ce soir » ; « jusqu’à » suivi de « ce soir », « minuit », « dimanche », « demain ».
- Superlatifs : « n°1 », « numéro 1 », « le meilleur », « la meilleure », « les meilleurs », « les meilleures », « le moins cher », « la moins chère », « leader ».
- Un superlatif prouvé par une source datée de la marque n’est pas signalé.

Exemple Love’nSpa : « Last Love Minute » est un nom d’offre (`copy-machine:brands/lovenspa.md`, Offre), pas une urgence en soi. Un compte à rebours n’est posé que sur une échéance réelle (S5-32).

## 3. Avis, témoignages et contenus clients

- Un avis ou un témoignage n’est cité que mot pour mot, attribué, et avec l’accord consigné (S9-14).
- Un témoignage manquant n’est jamais rédigé comme réel : `{{à compléter}}` (S6-29).
- Aucune note ni nombre d’avis sans source datée.
- Pas de conversation, de capture de message ou d’avis « mis en scène » présentés comme réels (`coreyhaines31_marketingskills@9d6d7ce:skills/ad-creative/references/imessage-video-ads.md`, « Compliance and Grounding »).

## 4. Prix

- Le seul prix citable est `prix_a_partir_de` de l’offre, avec son unité (contrôle `PRIX`). Un autre montant en euros produit `AUTRE_MONTANT`.
- Pas de prix barré, de « était / maintenant » ni d’ancrage sur un prix plus élevé sans prix de référence réel. La source cite le prix le plus bas des 30 derniers jours (art. L112-1-1). Le contrat `offre` ne porte pas ce prix : aucun prix barré aujourd’hui (C-21).
- Un montant pour des dates précises n’est jamais écrit : il dépend du calendrier (S9-02).

## 5. Registre explicite et ambiance (S6-28, S6-37)

| Contrôle | Règle | Donnée | État |
| --- | --- | --- | --- |
| `EXPLICITE` (bloquant) | Aucun terme de `lexique_explicite` dans le texte (mot entier, sans casse ni accents). | `marques/<id>/regles.json`, `lexique_explicite` | codé dans `controle.check` |
| `AMBIANCE` (bloquant) | Chaque offre de la case a une `ambiance` incluse dans `ambiances_autorisees` ; une ambiance absente bloque. | `offre.ambiance` (S3) ; `marques/<id>/strategie_<plateforme>.json`, `ambiances_autorisees` | codé dans `controle.verdict` (appelé par `produire.py`) ; à la main pour une légende isolée |

Exemple de mot entier : « nu » ne déclenche pas sur « nuit ».

Exemple Love’nSpa (`copy-machine:references/compliance-fr.md`, cas Love’nSpa ; `copy-machine:brands/lovenspa.md`) : suggestif, jamais explicite ; pas d’alcool mis en avant ; jamais promettre la disponibilité d’une date. Le lexique de la marque est une liste initiale à valider par la marque (`lexique_explicite_note`). Ajouter ou retirer un terme : proposition écrite à S1, validée par un humain.

## 6. Chiffres et balises (S6-29, S6-30)

- Tout nombre du texte, écrit en chiffres ou en lettres (de « deux » à « mille »), figure dans l’offre ou dans les données datées de la case. Numéros de liste et dates exclus. Sinon : constat de gravité haute et `{{à compléter}}`.
- Exemples Love’nSpa à vérifier contre une source datée avant usage : nombre de love rooms, nombre de logements par destination, montants de carte cadeau (`copy-machine:brands/lovenspa.md`, Preuves, relevés le 20/10/2026 : une valeur ancienne se revérifie).
- Aucune balise ne reste à la publication (`A_COMPLETER`).

## 7. Mentions

| Mention | Quand | Source |
| --- | --- | --- |
| Étiquette « contenu généré par IA » | Voix de synthèse ou visuel réaliste généré | S5-51, S7-06 |
| Crédit « Voix : Kyutai Pocket TTS (CC-BY 4.0) » | Voix Kyutai utilisée (option désactivée) | S7-07 |
| Crédit du compte (« Photo : @pseudo ») | Repartage d’un contenu client avec accord | S9-14 |
| Mention de partenariat commercial | Contenu fait avec un partenaire (concours, offre exclusive) | aucune source compilée : à sourcer |

## 8. Jeux-concours

Aucune source compilée ne couvre le droit des jeux-concours : ni `copy-machine`, ni `coreyhaines31_marketingskills` (constat du 11/11/2026, comme `regles-plateformes.md` de social-veille). Le contrôle vérifie seulement les règles maison du format 3 de social-production : accord du partenaire enregistré, lot identique à `nuits_offertes`, dates de début, de fin et de tirage présentes, aucune balise restante, aucune urgence sans échéance réelle. La validation juridique du règlement et des règles de plateforme sur les promotions reste humaine, hors S6.

## 9. Relecture indépendante (S6-31)

Le relecteur n’a pas écrit le texte et ne reçoit pas le raisonnement du rédacteur. Il ne réécrit pas. Chaque ligne : OK ou KO, avec une preuve courte.

1. Demande : la case est respectée (moteur, offres, une seule demande).
2. Faits : chaque chiffre, nom, prix, équipement, échéance vient de l’offre ou des données de la case, ou est en `{{à compléter}}`.
3. Conformité : rien de ce fichier n’est enfreint.
4. Action : une seule action demandée, claire.
5. Test du concurrent : relever toute phrase qui resterait vraie pour un concurrent (S6-38).
6. Relecture : fautes, chiffres recopiés exacts.

Sortie :

```
VERDICT : CONFORME | NON CONFORME
Écarts bloquants :
- <ligne de grille> — <citation courte> — <correction attendue>
Écarts mineurs :
- …
```

NON CONFORME dès que la ligne 1, 2 ou 3 est KO. Le relecteur prime sur le contrôle automatique pour les affirmations ; le texte se corrige, jamais le contrôle (S6-32).
