"""Build an auditable benchmark from the official ATLAS public cutflow."""
import decimal
import hashlib
import json
from pathlib import Path

D=decimal.Decimal
ROOT=Path(__file__).resolve().parent

# Public validation numbers from arXiv:2101.02245 Tables 7.2 and 7.3.
# Baseline matched by authors; only compare equivalent post-selection stages.
MA5 = {
 "120_1": {"low": ["14.65","57.10"], "high": ["8.24","45.41"]},
 "280_1": {"low": ["5.64","10.35"], "high": ["13.37","19.68"]},
}


def parse(path,doi,names):
    raw=path.read_bytes()
    j=json.loads(raw)
    if j["doi"] != doi or len(j["values"])!=len(names):
        raise ValueError("unexpected table provenance/shape")
    for i,v in enumerate(j["values"]):
        if names[i] is not None and v["x"][0]["value"]!=names[i]:
            raise ValueError(f"unexpected row at {i}")
    return j,hashlib.sha256(raw).hexdigest()


def values(row, n, want_error=False):
    d={v["group"]:v for v in row["y"]}
    if set(d)!=set(range(n)):
        raise ValueError("invalid column identities")
    if want_error:
        return [(D(d[k]["value"]),D(d[k]["errors"][0]["symerror"]) if d[k]["errors"][0]["symerror"] else None)
                for k in range(0,n,2)]
    return [d[k]["value"] for k in range(n)]


def grids(root):
    cols, hashes = {}, {}
    for k in range(11,17):
        p=root/f"{648426+k}.json"
        raw=p.read_bytes()
        j=json.loads(raw)
        doi=f"10.17182/hepdata.92006.v2/t{k}"
        matches=[r for r in j["values"] if [D(x["value"]) for x in r["x"]]==[280,1]]
        if j["doi"]!=doi or len(matches)!=1 or len(matches[0]["y"])!=1:
            raise ValueError("wrong acceptance grid, or absent benchmark")
        cols[k]=D(matches[0]["y"][0]["value"])/100
        hashes[doi]=hashlib.sha256(raw).hexdigest()
    return {name:{"acceptance":float(cols[a]),"conditional_efficiency":float(cols[e]),
                  "acceptance_times_efficiency":float(cols[p]),
                  "product_relative_printed_delta":float(cols[a]*cols[e]/cols[p]-1)}
            for name,(a,e,p) in {"low":(12,14,16),"high":(11,13,15)}.items()},hashes


def audit(root=ROOT):
    table,sha=parse(root/"atlas-t17.json","10.17182/hepdata.92006.v2/t17",
        ["Total events","Generator filter","Baseline cut",None,"b-jet veto","Light lepton veto","Z/H-veto",
         "SR-lowMass","Trigger & offline cuts",None,None,None,None,
         r"$ m_{T2} > 70 GeV $","SR-highMass","Trigger & offline cuts",None,None,None,
         r"$ m_{T2} > 70 GeV $"])
    control,csha=parse(root/"atlas-t18.json","10.17182/hepdata.92006.v2/t18",
        ["Observed","SM total","Diboson","$W$+jets","Top quark","$Z$+jets","Multi-jet"])
    records=table["values"]
    out={}
    for i,mass in enumerate(("120_1","280_1")):
        jj=2*i
        total=D(values(records[0],4)[jj])
        gen=D(values(records[1],4)[jj])
        base=D(values(records[2],4)[jj])
        if values(records[0],4)[jj+1]!="": raise ValueError("unexpected raw all-events count")
        phases={}
        for name,js in {"low":list(range(8,14)),"high":list(range(15,20))}.items():
            prev=D(values(records[6],4)[jj])
            stages=[]
            for k in js:
                r=records[k]
                yield_, stat=values(r,4,True)[i]
                if not (0 < yield_ <= prev): raise ValueError("non-monotone branch")
                stages.append(dict(id=k,label=r["x"][0]["value"],weighted=str(yield_),
                    stat=str(stat),raw_count=int(values(r,4)[jj+1]),step_eff=float(yield_/prev)))
                prev=yield_
            n=D(stages[-1]["weighted"])
            before=D(stages[-2]["weighted"])
            ma_n,ma_before=map(D, MA5[mass][name])
            phases[name]=dict(stages=stages,atlas_eff_times_acc=float(n/total),
                 ma5_baseline_normalized_final=float(ma_n),
                 ma5_final_relative_difference=float(ma_n/n-1),
                 ma5_mt2_conditional_relative_difference=float((ma_n/ma_before)/(n/before)-1))
        out[mass]=dict(atlas_weighted_total=str(total),generator_filter_fraction=float(gen/total),
          atlas_baseline_fraction=float(base/total),regions=phases)
    if [h["name"].split(" [")[0] for h in control["headers"]][1:]!=[
       "Multi-jet CR-lowMass","Multi-jet CR-highMass","WCR","SR-lowMass","SR-highMass"]:
        raise ValueError("unknown t18 region order")
    if [int(x.strip("$")) for x in values(control["values"][0],5)] != [72,27,1099,10,7]:
        raise ValueError("unexpected observation mapping")
    grid, hashes=grids(root)
    for region,row in grid.items():
        if abs(row["product_relative_printed_delta"])>0.001:
            raise ValueError("acceptance times efficiency mismatch")
        row["cutflow_vs_grid_relative_delta"]=(out["280_1"]["regions"][region]["atlas_eff_times_acc"]
                                              /row["acceptance_times_efficiency"]-1)
    return dict(grid_280_1=grid,grid_sha256=hashes,t17_sha256=sha,t18_sha256=csha,benchmarks=out,
        published_t17="two_signal_regions_only",
        published_t18="observations_and_backgrounds_only_no_signal_cutflow",
        ma5_status="baseline_normalized_different_matching_not_independent_detector_calibration",
        atlas_merge_validation="NOT_RUN", detector_validation="NOT_RUN", five_region_fitting="NOT_RUN")


if __name__=="__main__":
    print(json.dumps(audit(),sort_keys=True,indent=2))
