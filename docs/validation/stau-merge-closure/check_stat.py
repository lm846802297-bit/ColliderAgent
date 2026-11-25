"""Compare native refreshed end-of-file statistics at their printed precision."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import re


def check(rows, stdout):
    data=json.loads(rows.read_text())
    parsed={}
    for block in re.finditer(r"^FINAL-STAT (\d+) (\d+) (\d+)\n(.*?)^END-FINAL-STAT$",stdout.read_text(),re.S|re.M):
        s,seed,k,section=block.groups()
        p=re.findall(r"^\s*\| sum\s*\|\s*(\d+)\s+(\d+)\s+(\d+)\s*\|\s*([0-9.]+e[+-]\d+)\s+[0-9.]+e[+-]\d+\s*\|",section,re.M)
        if len(p)!=1 or (s,seed,k) in parsed: raise ValueError("unexpected native stat block")
        tried,n,acc,printed=p[0]
        exp=data[s][seed][k]
        if int(tried)!=exp["native_count"] or int(n)!=exp["native_count"]:
            raise ValueError("native statistics denominator incorrect")
        value=Decimal(printed).scaleb(12)
        half_step=Decimal(5).scaleb(value.as_tuple().exponent-1)
        diff=abs(value-Decimal(str(exp["sigma_fb"])))
        parsed[s,seed,k]=dict(scale=s,seed=seed,process=k,n_tried=int(tried),n_selected=int(n),
                      n_accepted=int(acc),native_printed_mb=printed,expected_fb=exp["sigma_fb"],
                      delta_fb=float(diff),half_print_unit_fb=float(half_step),pass_rounding=diff<=half_step)
    expected={(s,seed,k) for s,seeds in data.items() for seed,rs in seeds.items() for k,r in rs.items()
              if (k=="1" and seed=="41324") or abs(r["native_sigmaGen_fb"]/r["sigma_fb"]-1)>1e-8}
    if set(parsed)!=expected: raise ValueError("missing or extra native comparison rows")
    return dict(validated_at_print_precision=all(x["pass_rounding"] for x in parsed.values()),
                rows=list(parsed.values()),n_rows=len(parsed),native_stats_recomputed_after_eof=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("rows",type=Path)
    p.add_argument("stdout",type=Path)
    a=p.parse_args()
    print(json.dumps(check(a.rows,a.stdout),sort_keys=True,indent=2))
