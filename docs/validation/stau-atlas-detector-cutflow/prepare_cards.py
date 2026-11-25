"""Keep the public response unchanged; set seed and enable truth diagnostics."""
from pathlib import Path
import hashlib
import sys
p=Path(sys.argv[1])
src=p.read_bytes()
if hashlib.sha256(src).hexdigest()!='66248229f75a734fb65f6a6a7865f3e24c7c025f73183a518030126f7afafc5c':
    raise ValueError('public recast card mismatch')
card=src.decode()
marker='module TreeWriter TreeWriter {'
if card.count(marker)!=1: raise ValueError('unexpected tree writer')
for seed in (34025,34026,34027):
    Path(f'card-{seed}.tcl').write_text(f'set RandomSeed {seed}\n'+card.replace(marker,marker+'\n  add Branch Delphes/allParticles Particle GenParticle'))
