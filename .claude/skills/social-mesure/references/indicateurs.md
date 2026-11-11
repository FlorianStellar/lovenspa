# Indicateurs : définition, calcul, état d'outillage

« Codé » = calculé par `social/s8_mesure/audit.py` ou collecté par `social/s8_mesure/instantane.py` (via `social/connecteurs/instagram.py`). « Manuel (à outiller) » = à calculer à la main depuis l'instantané ou l'audit, en montrant le calcul, tant qu'aucune commande ne le fait.

## Ce que fait réellement l'instantané

`python3 -m social.s8_mesure.instantane --marque <id> [--out fichier] [--check]`

- `--check` : appelle seulement le profil et affiche `OK @compte · N abonnés · N publications`, ou l'échec (« jeton absent ou révoqué » si le code d'erreur est 190 ou absent).
- Sans `--check` : écrit `social/donnees/<id>/instagram/snapshot-AAAA-MM-JJ.json` avec :
  - `profil` : `username`, `name`, `followers_count`, `follows_count`, `media_count`, `biography`, `website`, et `portee_30j_par_type` (portée du compte sur les 30 derniers jours ventilée par type d'abonnement, ou `{"erreur": …}`) ;
  - `publications` : toutes les publications (pagination par 50), champs `id`, `caption`, `media_type`, `media_product_type`, `timestamp`, `permalink`, `like_count`, `comments_count` ;
  - pour chaque publication, `insights` : `reach`, `views`, `saved`, `shares`, `likes`, `comments`, `total_interactions`, `follows`, `profile_visits`, plus `ig_reels_avg_watch_time` et `ig_reels_video_view_total_time` pour les Reels. Une métrique refusée par l'API pour ce type de publication est retirée et notée dans `metriques_indisponibles` ; une autre erreur laisse `insights` vide et la note dans `erreur_insights` ;
  - `date` : date du jour.
- Le connecteur ne publie, ne commente et n'envoie rien. Le jeton est injecté par le proxy ou lu dans une variable d'environnement ; il n'est jamais écrit.

## Ce que fait réellement l'audit

`python3 -m social.s8_mesure.audit <instantané.json> [--depuis AAAA-MM-JJ] [--par-format] [--md fichier]`

| Calcul | Définition exacte dans le code |
|---|---|
| Format | `REELS` si `media_product_type` = REELS ; sinon `CAROUSEL` (CAROUSEL_ALBUM), `IMAGE`, `VIDEO`, ou `?`. |
| Valeur d'une métrique | lue dans `insights` ; non numérique = absente ; `views` = 0 avec `reach` > 0 = absente (non mesurée, pas zéro). |
| Médiane de référence | médiane des vues de toutes les publications retenues ; avec `--par-format`, médiane des vues du même format. Nombre pair : moyenne des deux valeurs du milieu. |
| `multiple` | vues ÷ médiane de référence ; absent si une des deux manque ou si la médiane vaut 0. |
| `partages_portee` | `shares` ÷ `reach`. |
| `enregistrements_portee` | `saved` ÷ `reach`. |
| `abonnements_portee` | `follows` ÷ `reach` (calculé, non affiché dans le rapport). |
| Complétude | nombre de publications ayant `views`, `reach`, `shares`, `saved`, `follows`. |
| Classements | top 5 et 5 derniers par `multiple` puis par `partages_portee` ; liste des 5 derniers seulement s'il y a plus de 5 valeurs ; classement « non publié » si la métrique manque pour plus de la moitié des publications. |
| Par format | nombre de publications, médiane des vues, médiane de partages ÷ portée et d'enregistrements ÷ portée. |
| Cadence | publications par semaine et par format sur les 4 dernières semaines complètes (lundi à dimanche) ; Reels comparés à une cible (3 par défaut dans le code, pas d'option en ligne de commande). |
| Période | `--depuis` garde les publications datées de ce jour ou après. |

Ce que l'audit ne fait pas : exclure les publications de moins de 48 h, les épinglées, les concours, sponsorisés ou collaborations ; appliquer le minimum de 3 publications par groupe ; lire le moteur ou la formule d'accroche ; écrire des objets `mesure`.

## Indicateurs de S2-M10 et état d'outillage

| Indicateur | Calcul | État |
|---|---|---|
| Multiple | vues ÷ médiane du compte (ou du format) | codé |
| Partages ÷ portée (le signal le plus fort) | `shares` ÷ `reach` | codé |
| Enregistrements ÷ portée | `saved` ÷ `reach` | codé |
| Abonnements ÷ portée | `follows` ÷ `reach` | codé (non affiché) |
| (Enregistrements + partages) pour 1 000 vues | (`saved` + `shares`) ÷ `views` × 1 000 ; absent si une valeur manque | manuel (à outiller), données présentes dans l'instantané |
| Commentaires pour 1 000 vues | `comments` ÷ `views` × 1 000 | manuel (à outiller), données présentes |
| Visionnage moyen ÷ durée de la vidéo | `ig_reels_avg_watch_time` ÷ durée | manuel (à outiller) : la durée n'est pas collectée |
| Rétention à 3 s | — | manuel (à outiller) : non collectée par le connecteur |
| Portée hors abonnés par publication | — | manuel (à outiller) : seule la portée du compte sur 30 jours est ventilée |
| Clics tracés | liens tracés de la stratégie (`utm`) et boutique | manuel (à outiller) |

## Scores par format, par moteur, par formule

Tous : manuel (à outiller). Méthode à appliquer à la main, à coder ensuite.

1. Partir des lignes de l'audit (une par publication), après exclusions : moins de 48 h, concours à part (sauf pour le score du moteur concours, calculé entre concours), sponsorisés et collaborations à part.
2. Rattacher chaque publication :
   - à son **format** : champ calculé par l'audit ;
   - à son **moteur** : `publies.json` (contrat `publication`), clé `media_id` = `id` de l'instantané. Une publication absente de `publies.json` (publiée hors système) a un moteur inconnu : groupe « inconnu », jamais deviné ;
   - à sa **formule d'accroche** : `id` (A01 à A63) noté dans le paquet S5. Absent = « inconnu ».
3. Pour chaque groupe d'au moins 3 publications : score = médiane des vues du groupe ÷ médiane des vues du compte sur la même période ; et médianes de partages ÷ portée, enregistrements ÷ portée, abonnements ÷ portée.
4. Groupe de moins de 3 publications : « pas assez de données », aucun score.
5. Écrire chaque score avec sa période, la taille du groupe et la complétude.

Exemple (première marque, journal du 11/11/2026) : séparation concours / hors concours faite à la main sur 168 publications ; médiane du compte 1 513 vues ; concours, médiane 8 004 vues ; hors concours, médiane 1 307 vues. Ce type de calcul est celui à outiller.

## Seuils

| Seuil | Valeur | Source |
|---|---|---|
| Surperformance de nos publications | 2x notre médiane | compilation S2, conflit « Seuil de surperformance » |
| Signal chez les comptes de référence | 3x (niveau B) | S2-M01 ; ne pas appliquer à nos publications |
| Publications trop récentes | moins de 48 h exclues | compilation S2, conflit « Exclusion des publications récentes » |
| Taille minimale d'un groupe | 3 publications | S2-M10 |
| Taille minimale de l'audit | 30 dernières, minimum 8 | S2-M10 |
| Classement publiable | métrique présente pour au moins la moitié des publications | code de l'audit |
