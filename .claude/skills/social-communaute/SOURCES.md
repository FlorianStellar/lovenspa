# Sources de la skill social-communaute

Compilation de référence : `social/compilation/s6-s7-s9-controle-diffusion-communaute.md` (11/11/2026). Aucun script tiers n’a été exécuté pour l’écrire. Le sous-système n’est pas codé : aucune ligne de code n’est décrite, hormis les commandes S3, S7 et S8 citées pour la lecture.

## Provenance par élément

| Élément de la skill | Provenance (`dépôt@commit:chemin`) | Licence | Modification |
| --- | --- | --- | --- |
| État du sous-système, jalon J7, droits du jeton | `lovenspa:social/s9_communaute/README.md` ; `lovenspa:social/README.md` | Interne | Décrit. |
| S9-01 (tri), S9-03, S9-04, S9-05, S9-06, S9-07, S9-08, S9-11, S9-15, S9-18 | `instagram-agent-skill@d03c56b:skills/ig-reply/SKILL.md` ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-reponse/SKILL.md` ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-commentaire/SKILL.md` (150 caractères) | MIT | Traduits et reformulés par Stellar Projects, 2026 ; validation humaine avant envoi retirée et remplacée par la charte ; vouvoiement (C-08) ; masquer seulement (C-02). |
| S9-08, S9-09, S9-10, S9-12, S9-13 | `instagram-agent-skill@d03c56b:skills/ig-dm/SKILL.md` ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-dm/SKILL.md` | MIT | Reformulés ; prospection à froid, relances et collab écartées. |
| S9-17 | `instagram-agent-skill@d03c56b:skills/ig-comment/SKILL.md` ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-commentaire/SKILL.md` | MIT | Reformulé : l’agent ne commente jamais chez les autres. |
| S9-02, S9-14, S9-16, catégories ARGENT, RÉCLAMATION, DOUTE, HÉBERGEUR, REPARTAGE | Brief S9 du projet ; `lovenspa@485c428:claude/agent-instagram/controle.py` (PRIX) | Interne | — |
| S9-14 (attribution des témoignages) | `knowledge-work-plugins@877a617:marketing/skills/brand-review/SKILL.md` (« Testimonial issues ») | Apache-2.0 | Traduit et reformulé par Stellar Projects, 2026. |
| S6-14 (ton par contexte) | `knowledge-work-plugins@877a617:partner-built/brand-voice/skills/brand-voice-enforcement/references/voice-constant-tone-flexes.md` ; `thatrebeccarae/claude-marketing@a8a63ec:skills/brand-voice-guidelines/SKILL.md` | MIT (Tribe AI, dans un dépôt Apache-2.0) ; MIT | Modifié et traduit en français par Stellar Projects, 2026. |
| S6-18 (confidentialité) | `knowledge-work-plugins@877a617:partner-built/brand-voice/skills/guideline-generation/SKILL.md` | MIT (Tribe AI, dans un dépôt Apache-2.0) | Modifié et traduit en français par Stellar Projects, 2026. |
| `references/gabarits-reponses.md` (G1 à G9) | Rédigés pour ce projet d’après les règles ci-dessus ; G3 d’après `instagram-agent-skill@d03c56b:skills/ig-dm/SKILL.md` et `Explo38/reels-tiktok-fr@a2281b6:skills/rt-dm/SKILL.md` | Interne ; MIT pour la structure de G3 | Compte de la marque et contacts mis en paramètres ; G1 et le message privé de G3 suspendus par les décisions en attente C-03 et C-04. |
| Décisions en attente C-03, C-04 | Compilation, section 6 (conflits) | Interne | Comportement par défaut le plus prudent : transmettre ; ne pas envoyer. |
| Règles de plateforme P-04 à P-11 | Sources citées dans la compilation, section 4 | MIT | Toutes « à vérifier dans la documentation officielle ». |

## Mentions de licence à conserver

- `instagram-agent-skill@d03c56b` : MIT, Copyright (c) 2026 Jake Schincariol.
- `Explo38/reels-tiktok-fr@a2281b6` : MIT, Copyright (c) 2026 Jake Schincariol (adaptation française sous la même licence). Texte complet : `social/s6_controle/vendor/LICENSE-reels-tiktok-fr`.
- `knowledge-work-plugins@877a617`, dossier `partner-built/brand-voice` : MIT, Copyright (c) 2025 Tribe AI, dans un dépôt sous licence Apache-2.0 ; modifié et traduit en français par Stellar Projects, 2026. La licence la plus proche du fichier (MIT) s’applique ; les deux sont citées (C-13).
- `knowledge-work-plugins@877a617:marketing/skills/brand-review` : Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0) ; modifié (traduit, reformulé, réduit) par Stellar Projects, 2026.
- `thatrebeccarae/claude-marketing@a8a63ec` : MIT, Copyright (c) 2026 Rebecca Rae Barton.
- Texte complet de la licence MIT : voir `.claude/skills/social-controle/SOURCES.md`.

## Écartés

Commentaires automatiques sous les publications d’autres comptes, prospection à froid, approche « tiède », relances J+4 et J+10, proposition de collab, validation humaine avant envoi (« They paste the replies ») : compilation, sections 5 et 7.
