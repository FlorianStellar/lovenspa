#!/usr/bin/env bash
# Tests du script de publication avec un faux Shopify CLI (aucun appel réseau).
set -u
D=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
export SHOPIFY_FLAG_STORE=x SHOPIFY_CLI_THEME_TOKEN=x
cat > "$W/fake" <<'F'
#!/usr/bin/env bash
# faux CLI : "theme pull|push ... --only f --path p" ; le live est $W/store
cmd=$2; f=""; p=""; while [ $# -gt 0 ]; do case $1 in --only) f=$2;shift;; --path) p=$2;shift;; esac; shift; done
echo "$cmd $f" >> "$LOG"
[ -d "$p" ] || { echo "path absent" >&2; exit 1; }
if [ "$cmd" = pull ]; then mkdir -p "$p/$(dirname $f)"; cp "$STORE/$f" "$p/$f"; else cp "$p/$f" "$STORE/$f"; fi
F
chmod +x "$W/fake"; export SHOPIFY_CMD="$W/fake" STORE="$W/store" LOG="$W/log"
f=sections/a.liquid; pass=0; fail=0
ok(){ if [ "$1" = "$2" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "KO: $3 (obtenu $1, attendu $2)"; fi; }
setup(){ rm -rf "$W/store" "$W/src" "$W"/src.live-* "$LOG"; mkdir -p "$W/store/sections" "$W/src/sections"
  echo original > "$W/store/$f"; echo patché > "$W/src/$f"; md5sum "$W/store/$f" | awk -v f=$f '{print $1"  "f}' > "$W/base"; }
# 1. live inchangé -> push + vérif OK
setup; bash "$D/theme_publish.sh" 1 "$W/src" "$W/base" $f >/dev/null 2>&1; ok $? 0 "publication nominale"
ok "$(cat $W/store/$f)" patché "contenu live après push"; ok "$(grep -c push $LOG)" 1 "un seul push"
ok "$(head -1 $LOG)" "pull $f" "pull avant push"
# 2. live modifié ailleurs -> exit 3, aucun push, copie du live
setup; echo "modif florian" > "$W/store/$f"; bash "$D/theme_publish.sh" 1 "$W/src" "$W/base" $f >/dev/null 2>&1; ok $? 3 "live modifié détecté"
ok "$(grep -c push $LOG)" 0 "aucun push si live modifié"; ok "$(cat $W/store/$f)" "modif florian" "live intact"
ok "$(ls -d $W/src.live-* | wc -l)" 1 "copie du live pour fusion"
# 3. fichier absent du manifeste -> exit 2
setup; : > "$W/base"; bash "$D/theme_publish.sh" 1 "$W/src" "$W/base" $f >/dev/null 2>&1; ok $? 2 "manifeste incomplet"
# 4. usage
bash "$D/theme_publish.sh" 1 >/dev/null 2>&1; ok $? 2 "usage"
echo "tests theme_publish : $pass OK, $fail KO"; [ $fail -eq 0 ]
