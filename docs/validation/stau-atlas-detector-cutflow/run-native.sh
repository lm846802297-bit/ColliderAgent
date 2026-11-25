#!/usr/bin/env bash
set -euo pipefail
seed="$1"; input="$(realpath "${2:?HepMC3 sample}")"
here="$(cd "$(dirname "$0")" && pwd)"
export ROOTSYS="$here/runtime/ROOT"
export LD_LIBRARY_PATH="$ROOTSYS/lib:$here/runtime/root.libs:$here/delphes-28658365:${LD_LIBRARY_PATH:-}"
export ROOT_INCLUDE_PATH="$here/delphes-28658365:$here/delphes-28658365/external:${ROOT_INCLUDE_PATH:-}"
cd "$here/delphes-28658365"
"$here/delphes-28658365/DelphesHepMC3" "$here/card-$seed.tcl" "$here/detector-$seed.root" "$input" > "$here/delphes-$seed.stdout" 2> "$here/delphes-$seed.stderr"
