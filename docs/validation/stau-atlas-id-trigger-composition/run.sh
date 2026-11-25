#!/usr/bin/env bash
set -euo pipefail
d="$(realpath "$1")"; fa="$(realpath "$2")"
export PYTHONPATH="$d/runtime:$d/mt2-runtime:$d:$fa:${PYTHONPATH:-}"
export ROOT_INCLUDE_PATH="$d/delphes-28658365:$d/delphes-28658365/external"
export LD_LIBRARY_PATH="$d/runtime/ROOT/lib:$d/runtime/root.libs:$d/delphes-28658365:${LD_LIBRARY_PATH:-}"
p="$(cd "$(dirname "$0")" && pwd)"
python "$p/compare.py" "$3" "$4" "$d/delphes-28658365/libDelphes.so" "$5" "$6"
PYTHONPATH="$p:$PYTHONPATH" python -m unittest -v test_compare
