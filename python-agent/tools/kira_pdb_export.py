"""Convert the exact Kira-3.1 PDB kira2math data subset to closed PhenoAgent rules."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

import sympy as sp

from canon_pdb_intake import identity, parse_masters, X
from loop_basis_verify import expression, read

TERM=r"PDB\[\s*-?\d+(?:\s*,\s*-?\d+){8}\s*\]"
RULE=re.compile(r"("+TERM+r")\s*->\s*")
RHS=re.compile(r"\+\s*("+TERM+r")\s*\*\s*")
SYMS={str(x):x for x in (*X,sp.Symbol("d"))}
SYMS.update(q3sq=X[2],q4sq=X[3])


def canonical(name):
    return identity(parse_masters(re.sub(r"\s+","",name),1)[0])


def convert(raw, masters, targets):
    if len(set(masters))!=len(masters) or len(set(targets))!=len(targets):
        raise ValueError("duplicate requested target or master")
    text=raw.decode().strip()
    if not text.startswith("{") or not text.endswith("}"):
        raise ValueError("expected one Mathematica list, not executable code")
    text=text[1:-1].strip()
    matches=list(RULE.finditer(text))
    if text and (not matches or matches[0].start()!=0):
        raise ValueError("unexpected prefix in export")
    rules={}
    for i, rule in enumerate(matches):
        key=canonical(rule[1])
        if key in rules or key not in targets:
            raise ValueError(f"duplicate/unrequested Kira row {key}")
        more=i+1<len(matches)
        rhs=text[rule.end():matches[i+1].start() if more else len(text)].strip()
        if more:
            if not rhs.endswith(","):
                raise ValueError("missing rule separator")
            rhs=rhs[:-1].strip()
        terms=list(RHS.finditer(rhs))
        if re.fullmatch(r"\+?\s*0",rhs):
            rules[key]={}
            continue
        if not terms or terms[0].start()!=0:
            raise ValueError(f"unexpected RHS syntax for {key}")
        row={}
        for j,term in enumerate(terms):
            u=canonical(term[1])
            if u not in masters or u in row:
                raise ValueError(f"unexpected or repeated source master {u}")
            coeff=rhs[term.end():terms[j+1].start() if j+1<len(terms) else len(rhs)].strip()
            # Mathematica ^ is not Python bitwise XOR in this documented subset.
            coeff=re.sub(r"\s+","",coeff).replace("^","**")
            row[u]=str(expression(coeff,SYMS))
        rules[key]=row
    missing=set(targets)-set(masters)-set(rules)
    if missing:
        raise ValueError(f"{len(missing)} unresolved requested rows: {sorted(missing)[:4]}")
    return dict(schema="pheno-pdb-ibp-v1",masters=masters,rules=rules)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("native",type=Path)
    p.add_argument("masters",type=Path)
    p.add_argument("targets",type=Path)
    p.add_argument("out",type=Path)
    a=p.parse_args()
    raw=read(a.native)
    masters=[canonical(x.split("#",1)[0]) for x in a.masters.read_text().splitlines() if x.split("#",1)[0].strip()]
    targets=[canonical(x.split("#",1)[0]) for x in a.targets.read_text().splitlines() if x.split("#",1)[0].strip()]
    result=convert(raw,masters,targets)
    with a.out.open("x") as f:
        f.write(json.dumps(result,indent=2)+"\n")
    print(json.dumps(dict(native_sha256=hashlib.sha256(raw).hexdigest(),
                          masters=len(masters),targets=len(targets),
                          explicit_rows=len(result["rules"])),sort_keys=True))


if __name__=="__main__":
    main()
