#!/usr/bin/env bash
# Publication sûre d'un fichier du thème Shopify : pull du live, contrôle, push, vérification.
# Usage : theme_publish.sh <theme_id> <dossier_patché> <manifeste_base> <fichier> [fichier...]
#   manifeste_base : lignes "md5  chemin/relatif" relevées au pull qui a servi de base au patch.
# Codes de sortie : 0 publié et vérifié · 2 usage · 3 live modifié ailleurs depuis la base (rien poussé)
#                   4 échec pull/push · 5 vérification après push en échec
set -euo pipefail
SHOPIFY="${SHOPIFY_CMD:-npx -y @shopify/cli@latest}"
[ $# -ge 4 ] || { echo "usage: $0 <theme_id> <dossier_patché> <manifeste_base> <fichier>..." >&2; exit 2; }
THEME="$1"; SRC="$2"; BASE="$3"; shift 3
: "${SHOPIFY_FLAG_STORE:?absent}" "${SHOPIFY_CLI_THEME_TOKEN:?absent}"
only=(); for f in "$@"; do only+=(--only "$f"); done
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/live" "$tmp/verif"

# 1. Pull du live juste avant publication
$SHOPIFY theme pull --theme "$THEME" "${only[@]}" --path "$tmp/live" >/dev/null 2>&1 || { echo "ECHEC pull live" >&2; exit 4; }
# 2. Le live doit être identique à la base du patch
changed=0
for f in "$@"; do
  base=$(awk -v f="$f" '$2==f{print $1}' "$BASE")
  live=$(md5sum "$tmp/live/$f" 2>/dev/null | cut -d' ' -f1 || true)
  [ -n "$base" ] || { echo "ABSENT du manifeste : $f" >&2; exit 2; }
  if [ "$live" != "$base" ]; then echo "LIVE MODIFIÉ : $f (base $base, live ${live:-absent})" >&2; changed=1; fi
done
[ $changed -eq 0 ] || { cp -r "$tmp/live" "${SRC%/}.live-$(date +%Y%m%d%H%M%S)"; echo "Rien poussé : fusionner avec la version live copiée à côté de $SRC" >&2; exit 3; }
# 3. Push
$SHOPIFY theme push --theme "$THEME" "${only[@]}" --allow-live --nodelete --path "$SRC" >/dev/null 2>&1 || { echo "ECHEC push" >&2; exit 4; }
# 4. Vérification : re-pull, md5 live == md5 patché
$SHOPIFY theme pull --theme "$THEME" "${only[@]}" --path "$tmp/verif" >/dev/null 2>&1 || { echo "ECHEC pull de vérification" >&2; exit 5; }
for f in "$@"; do
  a=$(md5sum "$SRC/$f" | cut -d' ' -f1); b=$(md5sum "$tmp/verif/$f" | cut -d' ' -f1)
  [ "$a" = "$b" ] || { echo "VERIF KO : $f (attendu $a, live $b)" >&2; exit 5; }
  echo "PUBLIÉ $f md5 avant $(awk -v f="$f" '$2==f{print $1}' "$BASE") après $b"
done
