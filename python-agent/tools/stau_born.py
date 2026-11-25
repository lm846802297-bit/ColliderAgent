"""Generate fixed-partonic-energy LO stau events for a scoped validation fixture."""
from __future__ import annotations

import argparse
import json
import math
import random

M_STAU, M_CHI, M_TAU, M_Z = 400., 80., 1.77686, 91.1876
ALPHA, SW2 = 1/128, 0.23122
E2, FB = 4*math.pi*ALPHA, 0.389379338e12
QUARKS = {q: (2/3, 1/2) if q in "uc" else (-1/3, -1/2) for q in "udscb"}


def coefficients(s, quark, chirality, photon_only=False):
    q, t3q = QUARKS[quark]
    t3s = {"L": -0.5, "R": 0.}[chirality]
    gam = -E2*q/s
    z_scalar = 0. if photon_only else E2*(t3s+SW2)/(SW2*(1-SW2)*(s-M_Z*M_Z))
    return tuple(gam + z_scalar*(t-SW2*q) for t in (t3q, 0.))


def born(energy, quark, chirality, photon_only=False):
    if not math.isfinite(energy) or energy <= 0:
        raise ValueError("positive finite partonic energy required")
    if energy <= 2*M_STAU:
        return 0.
    s = energy*energy
    beta = math.sqrt((energy-2*M_STAU)*(energy+2*M_STAU))/energy
    left, right = coefficients(s, quark, chirality, photon_only)
    return FB * s * beta**3 * (left**2+right**2)/(288*math.pi)


def direction(c, phi):
    r = math.sqrt(max(0., 1-c*c))
    return r*math.cos(phi), r*math.sin(phi), c


def rest_momentum(m, a, b):
    if m <= a+b:
        raise ValueError("closed decay")
    return math.sqrt((m-a-b)*(m+a+b)*(m-a+b)*(m+a-b))/(2*m)


def partial_width(chirality):
    y2 = 2*E2/(1-SW2)*{"L": .25, "R": 1.}[chirality]
    p = rest_momentum(M_STAU, M_TAU, M_CHI)
    return y2*(M_STAU**2-M_TAU**2-M_CHI**2)*p/(8*math.pi*M_STAU**2)


def boost(v, parent):
    gamma = parent[0]/M_STAU
    u = tuple(x/M_STAU for x in parent[1:])
    dot = sum(a*b for a,b in zip(u, v[1:]))
    return (gamma*v[0]+dot, *(x+y*(v[0]+dot/(gamma+1)) for x,y in zip(v[1:],u)))


def decay(parent, rng):
    p = rest_momentum(M_STAU, M_TAU, M_CHI)
    xyz = tuple(p*n for n in direction(rng.uniform(-1,1),rng.uniform(0,2*math.pi)))
    return [boost((math.hypot(M_TAU,p),*xyz),parent),
            boost((math.hypot(M_CHI,p),*(-v for v in xyz)),parent)]


def generate(energy, quark, chirality, count, seed):
    """Returns fixed-initial-state unweighted events and their independent total weight."""
    sigma = born(energy, quark, chirality)
    if count <= 0 or sigma == 0:
        raise ValueError("open phase space and a positive event count required")
    rng = random.Random(seed)
    p = rest_momentum(energy, M_STAU, M_STAU)
    events = []
    for _ in range(count):
        while True:
            c = rng.uniform(-1, 1)
            if rng.random() < 1-c*c:
                break
        xyz = tuple(p*n for n in direction(c, rng.uniform(0,2*math.pi)))
        ps = [(energy/2,*xyz), (energy/2,*(-x for x in xyz))]
        a, b = (decay(x,rng) for x in ps)
        events.append(dict(cos_theta=c, stau_minus=ps[0], stau_plus=ps[1],
                           tau_minus=a[0], chi_minus_parent=a[1],
                           tau_plus=b[0], chi_plus_parent=b[1]))
    return dict(process="fixed-partonic-energy Born q qbar -> stau pair (NWA)",
                energy_gev=energy, quark=quark, chirality=chirality, seed=seed,
                partonic_sigma_fb=sigma, equal_event_weight_fb=sigma/count,
                benchmark_partial_width_gev=partial_width(chirality), events=events)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--energy", type=float, required=True)
    p.add_argument("--quark", choices=QUARKS, required=True)
    p.add_argument("--chirality", choices=("L","R"), required=True)
    p.add_argument("--events", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    a = p.parse_args()
    try:
        out = generate(a.energy, a.quark, a.chirality, a.events, a.seed)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(out, sort_keys=True, allow_nan=False, separators=(",",":")))


if __name__ == "__main__":
    main()
