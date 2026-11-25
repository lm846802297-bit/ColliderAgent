#!/usr/bin/env bash
set -euo pipefail
d="$(realpath "$1")"; root="$(realpath "$2")"; truth="$(realpath "$3")"; result="$(realpath -m "$4")"
here="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$d/runtime:$d/mt2-runtime:$d:${PYTHONPATH:-}"
export ROOT_INCLUDE_PATH="$d/delphes-28658365:$d/delphes-28658365/external"
export LD_LIBRARY_PATH="$d/runtime/ROOT/lib:$d/runtime/root.libs:$d/delphes-28658365:${LD_LIBRARY_PATH:-}"
python "$here/response_audit.py" "$root" "$truth" "$d/delphes-28658365/libDelphes.so" "$result"
