#!/usr/bin/env bash
set -euo pipefail
seed="$1"; truth="$(realpath "$2")"; reference="$(realpath "$3")"
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"
export PYTHONPATH="$here/runtime:$here/mt2-runtime:${PYTHONPATH:-}"
export ROOT_INCLUDE_PATH="$here/delphes-28658365:$here/delphes-28658365/external:${ROOT_INCLUDE_PATH:-}"
export LD_LIBRARY_PATH="$here/runtime/ROOT/lib:$here/runtime/root.libs:$here/delphes-28658365:${LD_LIBRARY_PATH:-}"
python cutflow.py "detector-$seed.root" "$truth" "$reference" "result-$seed.json" --lib "$here/delphes-28658365/libDelphes.so" --seed "$seed" >"cutflow-$seed.stdout" 2>"cutflow-$seed.stderr"
