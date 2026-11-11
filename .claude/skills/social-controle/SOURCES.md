# Sources de la skill social-controle

Compilation de référence : `social/compilation/s6-s7-s9-controle-diffusion-communaute.md` (11/11/2026). Aucun script tiers n’a été exécuté pour l’écrire ; les fichiers Python des sources ont été lus seulement.

## Provenance par élément

| Élément de la skill | Provenance (`dépôt@commit:chemin`) | Licence | Modification |
| --- | --- | --- | --- |
| Codes bloquants et avertissements, fonction `verdict`, typographie `TYPO` | `lovenspa:social/s6_controle/controle.py` (copie de `lovenspa@485c428:claude/agent-instagram/controle.py`) | Interne | Décrit fidèlement, non modifié. |
| Clés de règles citées | `lovenspa:social/marques/lovenspa/regles.json` | Interne | Exemple de marque ; la skill ne reprend que les noms de clés. |
| Note anti-style IA, `detecter.py`, `lexique.json` repris | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-humain/` via `social/s6_controle/vendor/` | MIT | Modifications du vendor listées dans `social/s6_controle/vendor/README.md` (marquées `[lovenspa]`). |
| `references/lexique-tics-fr.md`, entrées « L » (149) | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-humain/lexique.json` | MIT | Recopiées ; « en définitive » remplacé par une suppression (C-12) ; six remplacements marqués « à relire ». |
| `references/lexique-tics-fr.md`, entrées « S » (44) | `instagram-agent-skill@d03c56b:skills/ig-human/slop.json` | MIT | Adaptées et traduites en français par Stellar Projects, 2026, à partir de 53 entrées anglaises. |
| Tics de structure (annexe B) | `lexique.json` (`structures`) ; `slop.json` (`structures`) ; `instagram-agent-skill@d03c56b:skills/ig-human/humanize.py` (`scan_structures`) ; `instagram-agent-skill@d03c56b:skills/ig-human/detect.py` (`check_voice`) | MIT | Traduits et reformulés ; seuil de hashtags aligné sur `max_hashtags` (C-06). |
| S6-03 à S6-05, S6-07, S6-22, S6-24 | `instagram-agent-skill@d03c56b:skills/ig-human/SKILL.md`, `slop.json` ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-humain/SKILL.md`, `lexique.json` | MIT | Reformulés ; remplacement automatique retiré (avertissement seulement). |
| S6-06 | `Explo38/reels-tiktok-fr@a2281b6:skills/rt-humain/SKILL.md` ; `instagram-agent-skill@d03c56b:skills/ig-human/detect.py` (`run`) | MIT | Rendu non bloquant (C-09). |
| S6-08 | `instagram-agent-skill@d03c56b:README.md` ; `Explo38/reels-tiktok-fr@a2281b6:skills/rt-dm/SKILL.md` ; code interne | MIT ; interne | Confirme `A_COMPLETER`. |
| S6-09, S6-10, S6-13 (format des attributs) | `knowledge-work-plugins@877a617:marketing/skills/brand-review/SKILL.md` | Apache-2.0 | Traduits et reformulés par Stellar Projects, 2026 ; règles de style anglaises retirées. |
| S6-11, S6-12, S6-14, S6-17 | `knowledge-work-plugins@877a617:partner-built/brand-voice/agents/quality-assurance.md` ; `.../skills/brand-voice-enforcement/references/voice-constant-tone-flexes.md` ; `.../skills/guideline-generation/SKILL.md` et `references/confidence-scoring.md` | MIT (Tribe AI) dans un dépôt Apache-2.0 | Modifié et traduit en français par Stellar Projects, 2026. |
| S6-12, S6-13, S6-14, S6-15, S6-16 | `thatrebeccarae/claude-marketing@a8a63ec:skills/brand-voice-guidelines/SKILL.md` ; `skills/brand-dna/SKILL.md` et `REFERENCE.md` (schéma `voice`) | MIT | Traduits et reformulés par Stellar Projects, 2026. |
| S6-18 | `knowledge-work-plugins@877a617:partner-built/brand-voice/skills/guideline-generation/SKILL.md` (« Privacy and Security ») | MIT (Tribe AI) dans un dépôt Apache-2.0 | Modifié et traduit en français par Stellar Projects, 2026. |
| S6-19 à S6-21 | Flora, skill `flora-brand-consistency-audit` (instructions servies par le MCP Flora, lecture seule) | Aucune licence indiquée | Méthode reformulée seulement : aucun texte recopié. |
| Règles typographiques à ne pas reprendre | `slop.json`, `lexique.json` (`invisible`, `typographic`) ; `humanize.py`, `humaniser.py` (`pass_typographic`) ; `detect.py` (`check_fingerprint`, `WORD_RE`, `CONTRACTIONS`) | MIT | Citées comme contre-exemples, non reprises. |
| Exemple « Nous sommes / Nous ne sommes pas » de Love’nSpa | Brief du projet | Interne | Marqué « exemple ». |

## Mentions de licence à conserver

### instagram-agent-skill@d03c56b (MIT)

Copyright (c) 2026 Jake Schincariol

### Explo38/reels-tiktok-fr@a2281b6 (MIT)

Copyright (c) 2026 Jake Schincariol. Adaptation française sous la même licence MIT. Texte complet déjà copié dans `social/s6_controle/vendor/LICENSE-reels-tiktok-fr`.

### thatrebeccarae/claude-marketing@a8a63ec (MIT)

Copyright (c) 2026 Rebecca Rae Barton

### knowledge-work-plugins@877a617, dossier partner-built/brand-voice (MIT, dans un dépôt Apache-2.0)

Copyright (c) 2025 Tribe AI. Modifié et traduit en français par Stellar Projects, 2026. Le dépôt qui contient ce dossier est sous licence Apache-2.0 ; la licence la plus proche du fichier (MIT) s’applique (C-13).

### knowledge-work-plugins@877a617, marketing/skills/brand-review (Apache-2.0)

Sous licence Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0). Fichier modifié : traduit, reformulé et réduit par Stellar Projects, 2026.

### Texte de la licence MIT (s’applique aux quatre sources MIT ci-dessus, chacune avec sa ligne de copyright)

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Flora

Aucune licence indiquée : aucun texte recopié, méthode reformulée seulement.

## Sécurité

- Ne pas installer `partner-built/brand-voice/.mcp.json` (serveurs MCP externes).
- Ne jamais utiliser `humanize.py`, `humaniser.py` ni `detect.py` (anglais).
- Aucune génération ni juge de vision Flora (payants).
