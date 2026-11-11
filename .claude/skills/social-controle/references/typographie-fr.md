# Typographie française : règles à appliquer et règles à ne jamais reprendre

Notre code fait foi (C-01) : `social/s6_controle/controle.py` (fonction `typo_issues`, code `TYPO`). Les règles des sources tierces qui dégradent la typographie française sont listées en partie 2 et ne s’appliquent jamais.

## 1. Règles à appliquer

### 1.1 Contrôlées par `controle.py` (avertissement `TYPO`)

| Règle | Détail du contrôle | Message produit |
| --- | --- | --- |
| Espace avant `;` `:` `!` `?` | Insécable (U+00A0) ou fine insécable (U+202F) attendue. Une espace ordinaire est signalée, une espace absente aussi. | « espace ordinaire avant « ? » (insécable conseillée) » ; « espace manquante avant « : » » |
| Exceptions au contrôle ci-dessus | Signes doublés (`?!`, `!!`), début de ligne, heure écrite `16:00` (chiffre de part et d’autre du deux-points), adresses web (`http…`, `www.…`) ignorées. | — |
| Guillemets français | « » avec une insécable à l’intérieur, de chaque côté. Un seul signalement par texte. | « « » sans espace insécable à l’intérieur » |
| Guillemets droits interdits | Tout `"` dans le texte est signalé. | « guillemets droits : utiliser « » » |

Statut : avertissement (`A_REVOIR` dans `check`). Le verdict reste `PRET` si aucun bloquant : corriger quand même avant diffusion (déroulé de la skill).

### 1.2 Appliquées par le modèle (code cible à outiller)

| ID | Règle |
| --- | --- |
| S6-03 | Supprimer les caractères invisibles : U+200B, U+200C, U+200E, U+200F, U+2060, U+FEFF, U+00AD, U+180E, U+061C, U+2063 et la plage U+E0000 à U+E007F. Garder U+200D (liant sans chasse) à l’intérieur d’une séquence emoji. Ne jamais toucher U+00A0 ni U+202F. |
| S6-04 | Tiret cadratin (—) dans une légende ou une réponse : avertissement `TIRET_LONG`, sans remplacement automatique. Reformuler (virgule, deux-points, ou deux phrases). Le demi-cadratin (–) d’un intervalle reste (« 14 h – 18 h »). |
| S6-22 | Emojis : un au plus ; jamais 🚀 🔥 💡 ✨ 🎯 ; jamais en puce ; jamais en premier caractère d’un commentaire. Majuscules : un mot au plus dans une légende. |
| — | Apostrophe typographique ’ conservée (ne pas la convertir en ’). |
| — | Points de suspension en un seul caractère … conservés. |
| — | Point médian · et flèche → conservés s’ils sont voulus. |
| — | Montants : nombre, insécable, symbole (« {{prix_a_partir_de}} € »). `controle.py` reconnaît l’espace ordinaire, U+00A0 et U+202F entre le nombre et « € » ; le séparateur de milliers peut être l’un de ces trois. |

## 2. Règles des sources à ne jamais reprendre

| Règle source | Effet sur un texte français | Source |
| --- | --- | --- |
| U+00A0 et U+202F remplacées par une espace simple | Supprime les insécables avant `;` `:` `!` `?` et dans « ». Contredit `TYPO`. | `slop.json` et `lexique.json` (`invisible`, action `space`) |
| ’ et ‘ remplacées par ’ | Dégrade l’apostrophe française. | `slop.json`, `lexique.json` (`typographic`) |
| « et » remplacés par " | Supprime les guillemets français. | `lexique.json` (`typographic`) ; `humaniser.py` (`pass_typographic`) |
| “ et ” remplacés par " | Acceptable seulement si l’on remplace ensuite par « ». Ne pas reprendre tel quel. | `slop.json`, `lexique.json` (`typographic`) |
| … remplacé par ... | Dégrade les points de suspension. | `slop.json`, `lexique.json` (`typographic`) |
| — remplacé d’office par une virgule, – par un trait d’union | Casse les incises et les intervalles. Remplacé par l’avertissement S6-04 (C-14). | `slop.json`, `lexique.json` (`typographic`) ; `humanize.py` (`pass_typographic`) |
| · remplacé par - ; → remplacé par -> | Dégrade la typographie sans gain. | `slop.json` (`typographic`) ; `lexique.json` (`→`) |
| Le contrôle FINGERPRINT compte U+00A0, U+202F et ’ comme traces machine | Pénalise un texte français correct. La version FR `vendor/detecter.py` les exclut ; ne jamais utiliser `detect.py`. | `instagram-agent-skill` `detect.py` (`check_fingerprint`) |
| Expressions régulières `[A-Za-z']+` et contractions anglaises | Ignorent les mots accentués, mesurent mal la voix d’un texte français. | `detect.py` (`WORD_RE`, `CONTRACTIONS`) |
| Suppression de U+200D partout | Casse les emojis composés. | `slop.json`, `lexique.json` (`invisible`) |
| Réécriture automatique (`humanize.py`, `humaniser.py`) | Réécrit « », ’, insécables, hashtags et emojis composés ; remplacements aveugles qui cassent les accords. | Écarté (compilation, section 5) |

`rt-humain/SKILL.md` reconnaît que l’insécable et « » sont la norme française, mais les convertit « pour que le texte passe partout ». Nous gardons la norme française.

## 3. Ordre d’application (S6-05)

1. Nettoyage mécanique : caractères invisibles seulement (1.2, S6-03).
2. Lecture des signalements `TYPO`, `TIRET_LONG`, structures ; réécriture par le modèle.
3. Nouveau contrôle.
4. Au-delà de deux tours, jeter le brouillon et en écrire un autre.
