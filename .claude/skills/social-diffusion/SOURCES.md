# Sources de la skill social-diffusion

Compilation de référence : `social/compilation/s6-s7-s9-controle-diffusion-communaute.md` (11/11/2026). Aucun script tiers n’a été exécuté pour l’écrire.

## Provenance par élément

| Élément de la skill | Provenance (`dépôt@commit:chemin`) | Licence | Modification |
| --- | --- | --- | --- |
| Chemin réel, garde-fous, sorties, journal | `lovenspa:social/s7_diffusion/instagram.py` (copie de `lovenspa@485c428:claude/agent-instagram/publier.py`) | Interne | Décrit fidèlement, non modifié. |
| Nouvel essai sur erreurs temporaires | `lovenspa:social/connecteurs/instagram.py` (`IGClient.post`) | Interne | Décrit. |
| Contrats lus et produits | `lovenspa:social/contrats/paquet.schema.json`, `verdict.schema.json`, `publication.schema.json` | Interne | Décrits. |
| S7-01 | `instagram-agent-skill@d03c56b:README.md` (« The fine print ») ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-publication/SKILL.md` (garde-fou 3) | MIT | Traduit et reformulé par Stellar Projects, 2026. |
| S7-02 à S7-10, S7-12, S7-14, S7-15 | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-publication/SKILL.md` | MIT | Reformulés ; accord humain par lot retiré et remplacé par les garde-fous (C-07). |
| S7-11 | Flora, skill `flora-brand-consistency-audit` (« The asset record cannot answer the spec question ») | Aucune licence indiquée | Méthode reformulée seulement : aucun texte recopié. |
| S7-13 | `instagram-agent-skill@d03c56b:skills/ig-reply/SKILL.md` ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-reponse/SKILL.md` | MIT | Traduit et reformulé par Stellar Projects, 2026. |
| `references/regles-plateformes.md` (P-01 à P-17) | Sources citées ligne par ligne | MIT | Reformulées, toutes marquées « à vérifier dans la documentation officielle ». |

## Mentions de licence à conserver

- `instagram-agent-skill@d03c56b` : MIT, Copyright (c) 2026 Jake Schincariol.
- `Explo38/reels-tiktok-fr@a2281b6` : MIT, Copyright (c) 2026 Jake Schincariol (adaptation française sous la même licence). Texte complet de la licence MIT : `social/s6_controle/vendor/LICENSE-reels-tiktok-fr`.
- Flora : aucune licence indiquée ; méthode reformulée seulement.
