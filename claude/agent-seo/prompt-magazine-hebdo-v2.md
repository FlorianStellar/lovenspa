# Prompt v2 de la tâche « Magazine Love'nSpa hebdo » (trig_017tNLpXRFaudoUQrMRwhjw9)

À appliquer depuis une conversation Cowork liée au MacBook Pro : la tâche tourne sur ce Mac, donc son prompt ne peut changer qu'avec une approbation signée sur l'appareil.
Changements par rapport à la v1, tout le reste est inchangé :
- §1 : ajout de la source « Export plat du site » ;
- §3 : inventaire et maillage pris dans l'export ;
- §4 : choix des liens internes ;
- §5 : liens vers des URL publiées uniquement, et metas uniques ;
- §6 : contrôle des liens contre l'export.

## Ajouts, à insérer aux endroits indiqués

§1, nouvelle puce en fin de liste :
- Export plat du site (remplace Matrixify ; dépôt FlorianStellar/lovenspa, branche claude/zen-edison-sac366) : le dernier dossier `claude/exports/site-AAAA-MM-JJ/`. Il contient :
  - `pages.csv` : toutes les URL, publiées ou non, avec titres, metas et nombre de mots ;
  - `audit/liens_entrants.csv`, `audit/liens_a_corriger.csv` et `audit/metas.csv`.

  S'il a plus de 7 jours et que la variable SHOPIFY_API_TOKEN existe, régénère-le :
  1. `pip install -q -r claude/agent-seo/requirements.txt` ;
  2. `python3 claude/agent-seo/site_export.py claude/exports/site-AAAA-MM-JJ` ;
  3. `python3 claude/agent-seo/site_audit.py claude/exports/site-AAAA-MM-JJ`.

  Ne le versionne pas : l'agent du mercredi le fait. Sans dépôt ni jeton, dis-le et utilise GraphQL comme avant.

§3, remplacer la puce « Inventaire exhaustif… » par :
- Inventaire exhaustif des articles du blog magazine : prends-le dans `pages.csv` de l'export (type article, URL /blogs/magazine/…). Sinon, utilise l'outil `mcp__remote-devices__shopify-seo-lovenspa__get-articles` ou GraphQL, en paginant jusqu'au bout. Pour chaque article : titre, handle, date, auteur, tags, cocon.

§3, nouvelle puce avant « Verdict » :
- Maillage du magazine, depuis l'export :
  - articles sans aucun lien entrant éditorial (`audit/liens_entrants.csv`, liens_entrants = 0) ;
  - liens des articles qui passent par une redirection ou visent une page non publiée (`audit/liens_a_corriger.csv`, source /blogs/magazine/…).

  Les corrections de liens existants relèvent de l'agent du mercredi : signale-les, ne modifie pas les articles existants.

§3, puce « Verdict » : ajouter « (compare aussi les titles de `pages.csv`) » après « avec les articles existants ou Holo ».

§4, nouvelle puce avant « Aucun doublon » :
- Articles internes à lier : choisis-les parmi les URL publiées de `pages.csv` du même cocon. Donne la priorité à celles qui ont le moins de liens entrants (`audit/liens_entrants.csv`). Jamais une URL de `audit/liens_a_corriger.csv`, ni une URL d'arrivée ou de départ d'une redirection.

§5, règles fermes : ajouter « chaque lien interne pointe vers une URL publiée de l'export, jamais vers une redirection ; » avant « tags Shopify ».

§5, puce « Meta title » : ajouter « Aucun title ni aucune description identique à une page de `pages.csv`. »

§6, liste des vérifications : ajouter « chaque lien interne contre l'export (URL publiée, pas de redirection), » après « (compte les tirets longs, emoji, ratio d'accents, liens en 200, ancres), ».

## Réserve

La tâche tourne sur le Mac et lit ses fichiers avec l'outil Projects. Si ce Mac n'a ni clone du dépôt ni la variable SHOPIFY_API_TOKEN, ces ajouts restent sans effet et le comportement actuel s'applique (repli prévu au §1).
