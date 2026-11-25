#!/usr/bin/env bash
set -euo pipefail
ref=b11c683f12618c2543ac9de9cc8c5aef2ab02759
url="https://gitlab.cern.ch/atlas-sa/framework/-/raw/$ref/src"
for name in METSignificanceCalculator ObjectResolutions; do
  curl -fsSL "$url/$name.cxx" -o "$name.cxx"
done
for i in {0..4}; do
  name="tauRes1p0nBin$i.h"
  curl -fsSL "$url/objres/$name" -o "$name"
done
python -m unittest -q test_sai.py
python sai.py
