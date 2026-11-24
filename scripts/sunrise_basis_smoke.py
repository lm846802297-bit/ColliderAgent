"""Small ColliderAgent basis-gate smoke: published equal-mass sunrise."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import sys

import sympy as s

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python-agent" / "tools"))
from integral_basis_gate import audit_basis, compare_basis_reports, time_exact_replay

z, eps = s.symbols("z eps")
d = 2-2*eps
Q = z*(z+1)*(z+9)
p1 = ((12-3*d)*z**2+10*(6-d)*z+9*d)/2
p2 = (d-3)*((d-4)*z-d-4)/2


def models():
    # Laporta–Remiddi Eq. (2.8), with H=(d-4)^(-2), H'=0.
    low = s.Matrix([
        [(d-3)/z, 3/z, 0],
        [(d-3)*(8-3*d)*(z+3)/(2*Q),
         ((d-4)*z**2+10*(2-d)*z+9*(8-3*d))/(2*Q), z/(2*Q)],
        [0, 0, 0],
    ])
    # Independent routes. Start from scalar Eq. (2.9); compute S' and
    # S1=(z*S'-(d-3)*S)/3, then differentiate S1 by the product rule.
    S, derivative, H = s.symbols("S V H")
    ddS = (-p1*derivative-p2*S+s.Rational(3, 2)*H)/Q
    Bdot = ((4-d)*derivative+z*ddS)/3
    dot_reference = s.Matrix([derivative, Bdot, 0]).subs(
        derivative, ((d-3)*S+3*derivative)/z
    ).jacobian([S, derivative, H])
    # AI candidate: obtain J' directly by differentiating z(z+1)(z+9) S'.
    Jdot = s.Matrix([[0, 1/Q, 0],
                     [-p2, (s.diff(Q,z)-p1)/Q, s.Rational(3,2)],
                     [0, 0, 0]])
    choice = s.Matrix([[1,0,0],[(z+1)*(z+9)*(d-3),3*(z+1)*(z+9),0],[0,0,1]])
    return low, dot_reference, choice, Jdot


def check_parameter_integral():
    # At d=2, Euclidean Feynman-simplex representation in Eq. (2.1)
    # loop-measure conventions. Map a=u,b=(1-u)v,c=(1-u)(1-v).
    # Compute S, S_z and S_zz directly, not by solving the input DE.
    import scipy
    from scipy.integrate import quad
    from math import isfinite
    records = []
    for point in (0.5, 2.0, 8.0):
        values = []
        for n in range(3):
            def outer(u):
                def integrand(v):
                    a,b,c=u,(1-u)*v,(1-u)*(1-v)
                    x=a*b*c
                    F=a*b+b*c+c*a+point*x
                    return (1-u)*x**n/F**(n+1)
                return quad(integrand,0,1,epsabs=3e-11,epsrel=3e-11)[0]
            integral, error_est = quad(outer,0,1,epsabs=3e-10,epsrel=3e-10)
            values.append((integral * (1,-1,2)[n] / 16, error_est))
        f,f1,f2 = (v[0] for v in values)
        residual = point*(point+1)*(point+9)*f2+(3*point**2+20*point+9)*f1+(point+3)*f-3/8
        if not isfinite(residual) or abs(residual)>2e-8:
            raise ValueError(f"direct Feynman-parameter check failed at {point}")
        records.append(dict(z=point,S=f,dS_dz=f1,d2S_dz2=f2,residual=residual))
    return {"dimensions": 2, "scipy": scipy.__version__, "points": records, "absolute_tolerance": 2e-8}


def run(with_integrals=False):
    A, reference, T, Jref = models()
    a, ra = audit_basis(A, s.eye(3), z, eps, reference)
    b, rb = audit_basis(A, T, z, eps, Jref)
    grid = [[(z, s.Rational(k,3)), (eps,s.Rational(1,17+k))] for k in (2,3,5,9,23)]
    proof = {
        "family": "PL1 equal-mass sunrise D1,D2,D8; exact Laporta–Remiddi block",
        "mode": "one AI proposal vs one fixed rule; not a blinded trial",
        "coordinate": "z = -s24/m_e^2; m_e=1; d=2-2eps",
        "inputs": {
            "lar_eq28_matrix_sha256": hashlib.sha256(str(A).encode()).hexdigest(),
            "paper_ancillary_sha256": "4054767d0a8a3b1a253a9845c17adb8f8027f972fd78bd9b6c54d89b88d5f83b",
            "laporta_remiddi_pdf_sha256": "90e6d09ec39b9fc8b8021c0db7d95efa0cd72c72d9fdc2fd3198a442641cf84d",
        },
        "python":platform.python_version(), "sympy":s.__version__,
        "fixed_lowest_dot":ra,"ai_weighted_derivative":rb,
        "structural_decision": compare_basis_reports(ra, rb),
        "native_ibp":"NOT_RUN", "autonomous_ai_search":"NOT_RUN",
        "parameter_integral":check_parameter_integral() if with_integrals else "NOT_RUN",
    }
    return proof, (a,b), grid


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--quadrature",action="store_true",help="independently check d=2 on the simplex using SciPy")
    p.add_argument("--timing",action="store_true",help="time replay only, not native IBP")
    args=p.parse_args()
    proof, matrices, points=run(args.quadrature)
    if args.timing:
        proof["replay_timing"]=time_exact_replay(matrices,points)
    print(json.dumps(proof,ensure_ascii=False,sort_keys=True,indent=2))
