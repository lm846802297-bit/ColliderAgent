#!/usr/bin/env bash
set -euo pipefail
d="$(realpath "$1")"; f="$(realpath "$2")"; m="$(realpath "$3")"
export PYTHONPATH="$d/runtime:$d/mt2-runtime:$d:$f:$m:${PYTHONPATH:-}"
export ROOT_INCLUDE_PATH="$d/delphes-28658365:$d/delphes-28658365/external"
export LD_LIBRARY_PATH="$d/runtime/ROOT/lib:$d/runtime/root.libs:$d/delphes-28658365:${LD_LIBRARY_PATH:-}"
here="$(cd "$(dirname "$0")" && pwd)"
python "$here/tau_met.py" "$d" "$4" "$d/delphes-28658365/libDelphes.so" "$5"
PYTHONPATH="$here:$PYTHONPATH" python -m unittest -v test_tau_met
