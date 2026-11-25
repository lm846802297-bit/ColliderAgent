"""Prepare exact Kira targets for CANON §IV.1's pre-canonical PDB family."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import sympy as sp

from loop_basis_verify import expression, keys, loads, prepare, read

X = sp.symbols("s t Q3sq Q4sq m2")
Z = sp.symbols("D1:10")
V = sp.symbols("k11 k22 k12 k1p1 k1p2 k1p3 k2p1 k2p2 k2p3")
S, T, Q3, Q4, M = X
G = sp.Matrix([[0, S/2, (Q4-S-T)/2], [S/2, 0, (T-Q3)/2],
               [(Q4-S-T)/2, (T-Q3)/2, Q3]])
# Each row encodes (a.k+b.p)^2 minus the propagator squared mass.
LOOPS = ((1,0),(1,0),(1,0),(0,1),(0,1),(1,-1),(0,1),(0,1),(1,0))
EXT = ((0,0,0),(1,0,0),(0,-1,0),(1,0,0),(0,-1,0),(0,0,0),
       (0,-1,-1),(0,0,0),(0,-1,-1))
MASS = (0,0,0,0,0,0,M,0,0)


def scalar_products():
    ll = sp.Matrix([[V[0],V[2]],[V[2],V[1]]])
    lp = sp.Matrix([V[3:6],V[6:9]])
    return ll, lp


@lru_cache(maxsize=1)
def propagators_and_map():
    ll, lp = scalar_products()
    ds = []
    for a,b,m in zip(LOOPS,EXT,MASS):
        a,b = sp.Matrix([a]),sp.Matrix([b])
        ds.append(sp.expand((a*ll*a.T+2*a*lp*b.T+b*G*b.T)[0]-m))
    solutions = sp.solve([d-z for d,z in zip(ds,Z)], V, dict=True)
    if len(solutions)!=1 or set(solutions[0])!=set(V):
        raise RuntimeError("scalar product map is not invertible")
    return ds, solutions[0]


@lru_cache(maxsize=1)
def denominator_derivatives():
    _, mapping = propagators_and_map()
    _, lp = scalar_products()
    inverse = G.inv()
    result = {}
    for x in X:
        dg = G.diff(x)
        # del p_i = C_ij p_j: C G + G C^T = del G.
        c = dg * inverse / 2
        direction = []
        for a,b,m in zip(LOOPS,EXT,MASS):
            a,b = sp.Matrix([a]),sp.Matrix([b])
            delta=(2*a*lp*c.T*b.T+b*dg*b.T)[0]-sp.diff(m,x)
            polynomial=sp.Poly(sp.cancel(delta.subs(mapping, simultaneous=True)), *Z)
            if polynomial.total_degree() > 1:
                raise RuntimeError("expected affine denominator derivative")
            direction.append(dict(polynomial.terms()))
        result[x]=tuple(direction)
    return result


def derivative(indices, x):
    terms = defaultdict(lambda: sp.S.Zero)
    for j,(power, dp) in enumerate(zip(indices,denominator_derivatives()[x])):
        if not power:
            continue
        for monomial,coeff in dp.items():
            shifted=tuple(n+(i==j)-k for i,(n,k) in enumerate(zip(indices,monomial)))
            terms[shifted] -= power * coeff
    return {k:v for k,c in sorted(terms.items()) if (v:=sp.cancel(c))!=0}


def identity(indices):
    return "PDB["+ ",".join(map(str,indices))+"]"


def parse_masters(text, count):
    result=[]
    for line in text.splitlines():
        value=line.split("#",1)[0].strip()
        if not value:
            continue
        match=re.fullmatch(r"PDB\[(-?\d+(?:\s*,\s*-?\d+){8})\]",value)
        if not match:
            raise ValueError(f"unsupported line in ordered master list: {line}")
        nums=tuple(map(int,match[1].split(",")))
        if max(nums[7:])>0:
            raise ValueError("positive powers in an ISP slot")
        result.append(nums)
    if len(result)!=count or len(set(result))!=count:
        raise ValueError(f"need exactly {count} distinct master integrals")
    return result


def package(masters, path):
    targets=set(masters)
    directions={}
    for x in X:
        rows=[]
        for i in masters:
            terms=derivative(i,x)
            targets.update(terms)
            rows.append({identity(key):str(value) for key,value in terms.items()})
        directions[str(x)] = rows
    targets = sorted(targets)
    dot_budget=max(sum(max(a,0) for a in i) for i in targets)
    numerator_budget=max(-sum(min(a,0) for a in i) for i in targets)
    path.mkdir(parents=True)
    lines=lambda ints:"".join(identity(row)+"\n" for row in ints)
    (path/"preferred-masters").write_text(lines(masters))
    (path/"targets").write_text(lines(targets))
    (path/"precanonical-derivatives.json").write_text(json.dumps(
        dict(schema="pheno-canon-pdb-derivatives-v1", variables=list(map(str,X)),
             masters=list(map(identity,masters)), directions=directions,
             target_count=len(targets), target_r_upper=dot_budget,
             target_s_upper=numerator_budget),indent=2)+"\n")
    # Heuristic seeding, not a claim of closure. Symbolic Kira output must be
    # checked for all required targets in the requested ordered basis.
    (path/"jobs.yaml").write_text(f"""jobs:
  - reduce_sectors:
      reduce:
        - {{sectors: [127], r: {max(8,dot_budget)}, s: {max(2,numerator_budget)}}}
      select_integrals:
        select_mandatory_list:
          - [PDB, targets]
      run_initiate: true
      run_firefly: true
      preferred_masters: "preferred-masters"
  - kira2math:
      reconstruct_mass: true
      target:
        - [PDB, targets]
""")
    config=Path(__file__).resolve().parents[2]/"research/loop_basis/double_box_kira/config"
    (path/"config").mkdir()
    for file in ("kinematics.yaml","integralfamilies.yaml"):
        (path/"config"/file).write_bytes((config/file).read_bytes())


def assemble(derivative_data, reduction, letters):
    """Fail closed on incomplete exported IBP rules; check exact homogeneity."""
    from loop_basis_verify import Field
    keys(reduction, ("schema", "masters", "rules"))
    if reduction["schema"]!="pheno-pdb-ibp-v1":
        raise ValueError("unrecognized normalized IBP export")
    ordered=derivative_data["masters"]
    if reduction["masters"]!=ordered:
        raise ValueError("reducer master order/content changed")
    rules=reduction["rules"]
    if not isinstance(rules,dict):
        raise ValueError("expected exact target-reduction dictionary")
    ep=sp.Symbol("eps")
    d=sp.Symbol("d")
    field=Field(X,ep)
    names={**field.names,"d":d}
    def coeff(s):
        return field.normal(expression(s,names).subs(d,4-2*ep))

    compiled={}
    for target,row in rules.items():
        parse_masters(target,1)
        keys(row, (), ordered)
        compiled[target]={key:coeff(value) for key,value in row.items()}
    for name in ordered:
        if name in compiled and compiled[name]!={name:sp.S.One}:
            raise ValueError(f"inconsistent master identity {name}")
        compiled[name]={name:sp.S.One}

    n=len(ordered)
    cols=dict(zip(ordered,range(n)))
    matrices={}
    for x in map(str,X):
        matrix={}
        for i,row in enumerate(derivative_data["directions"][x]):
            for target, prefactor in row.items():
                if target not in compiled:
                    raise ValueError(f"missing required IBP rule: {target}")
                for master, value in compiled[target].items():
                    k=(i,cols[master])
                    matrix[k]=matrix.get(k,0)+coeff(prefactor)*value
        matrices[x]={key:v for key,val in matrix.items() if (v:=field.normal(val))!=0}
    for i,label in enumerate(ordered):
        degree=4-2*ep-sum(parse_masters(label,1)[0])
        row_cols={i}|{j for m in matrices.values() for row,j in m if row==i}
        for j in row_cols:
            weighted=sum(x*matrices[str(x)].get((i,j),0) for x in X)
            if field.normal(weighted-(degree if i==j else 0))!=0:
                raise ValueError(f"Euler identity fails at row {i}, column {j}")
    src=dict(schema="pheno-loop-source-v1",masters=ordered,
             variables=list(map(str,X)),epsilon="eps",
             connections={x:[[i,j,str(v)] for (i,j),v in sorted(m.items())]
                          for x,m in matrices.items()},
             letters=letters,
             quadratic_root={"name":"r","radicand":"(s-Q3sq-Q4sq)**2-4*Q3sq*Q4sq"})
    prepare(src)
    return src


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_subparsers(dest="mode",required=True)
    prepare_cli=modes.add_parser("prepare")
    prepare_cli.add_argument("masters",type=Path)
    prepare_cli.add_argument("out",type=Path)
    assemble_cli=modes.add_parser("assemble")
    assemble_cli.add_argument("job_directory",type=Path)
    assemble_cli.add_argument("normalized_reduction",type=Path)
    assemble_cli.add_argument("letters",type=Path)
    assemble_cli.add_argument("out",type=Path)
    args=parser.parse_args()
    if args.mode=="prepare":
        package(parse_masters(args.masters.read_text(),37),args.out)
    else:
        masters=parse_masters((args.job_directory/"preferred-masters").read_text(),37)
        # Regenerate derivatives from the exact ordered master list rather than
        # trusting a mutable intermediate file in the reducer directory.
        derivative_data={"masters":list(map(identity,masters)),
                         "directions":{str(x):[{identity(i):str(v) for i,v in derivative(a,x).items()}
                                               for a in masters] for x in X}}
        source=assemble(derivative_data, loads(read(args.normalized_reduction)),
                        loads(read(args.letters)))
        with args.out.open("x") as output:
            output.write(json.dumps(source,indent=2)+"\n")


if __name__=="__main__":
    main()
