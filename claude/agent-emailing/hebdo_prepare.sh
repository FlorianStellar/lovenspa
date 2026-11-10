#!/usr/bin/env bash
# Prépare la campagne hebdo : relevé de dispos -> email -> lint --live -> template Klaviyo. Ne programme rien.
# Usage : hebdo_prepare.sh <date_vendredi> <date_samedi> <clé campagne dans campaigns_ids.json> <clé template>
set -euo pipefail
cd "$(dirname "$0")"
VEN="$1"; SAM="$2"; CK="$3"; TK="$4"
SK=/root/.claude/skills/synced/5702de8d-bbc9-417e-bb68-8772896a0e36_def019a4-ad17-4856-a094-a71272bd7888/copy-machine
python3 dispos_weekend.py "$(cat runs/candidats-$VEN.txt)" "$VEN,$SAM"
python3 hebdo_build.py "$VEN" "$SK/runs/hebdo-$VEN"
python3 "$SK/scripts/copy_lint.py" "$SK/runs/hebdo-$VEN/copy.md" --brand "$SK/brands/lovenspa.md" --format email --data "$SK/runs/hebdo-$VEN/data.md" --live | tail -3 | tee runs/lint-$VEN.txt
grep -q "Score 100/100" runs/lint-$VEN.txt || { echo "LINT < 100 : rien mis à jour"; exit 3; }
python3 hebdo_build.py "$VEN" "$SK/runs/hebdo-$VEN" --push "$CK" "$TK"
