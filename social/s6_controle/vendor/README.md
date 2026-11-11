# vendor/ : outils repris de reels-tiktok-fr

Source : https://github.com/Explo38/reels-tiktok-fr @ a2281b65dba8d9ba0397f312771256462e326c5e
(adaptation FR de instagram-agent-skill de Jake Schincariol). Licence MIT : voir LICENSE-reels-tiktok-fr.
Audit complet le 11/11/2026 : bibliothèque standard seule, aucun réseau, aucune exécution externe.

Repris : detecter.py, lexique.json (notation anti-style IA, lecture seule), score_hook.py, minutage.py, hooks.json.
Non repris : humaniser.py (réécrit les « », ’, espaces insécables, hashtags et emojis composés : incompatible
avec la typographie française), legende.py (remplacé par ../controle.py).

Modifications, toutes marquées `[lovenspa]` dans le code :
- score_hook.py : PROPER_RE ne matchait jamais (lookbehind `(?<!^)`) ; garde mpm <= 0 ; fichiers fermés.
- minutage.py : arrondi de tc() (« 0:60.0 ») ; garde mpm <= 0 ; fichiers fermés.
- detecter.py : « … » n'est plus pénalisé (typographie française) ; fichiers fermés.
- Espaces insécables littérales remplacées par des échappements \u00a0 / \u202f.
