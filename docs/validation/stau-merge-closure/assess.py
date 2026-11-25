"""Score the frozen pilot gate without treating re-used hard events as independent."""
import argparse
import json
import math
from pathlib import Path
import statistics as st


def assessed(v, final_stats=None):
    scales={}
    modes=set()
    snapshot_diffs=[]
    for scale, seeds in sorted(v.items()):
        totals=[]; ms=[]; hists=[]; near=[]
        for seed, runs in sorted(seeds.items()):
            assert set(runs)==set("123456")
            modes.update(x.get("normalization_modes_checked", 3) for x in runs.values())
            snapshot_diffs.extend(x.get("native_snapshot_comparison_relative",math.inf)
                                  for x in runs.values())
            totals.append(math.fsum(x["sigma_fb"] for x in runs.values()))
            ms.append(min(x["neff"] for x in runs.values()))
            hs=[[math.fsum(x["d01_d12_fb"][i][j] for x in runs.values())
                 for j in range(10)] for i in range(2)]
            q2=[[math.fsum(x["d01_d12_weight2_fb2"][i][j] for x in runs.values())
                 for j in range(10)] for i in range(2)]
            # Compare bins with edges 20,25,35,45,60 for both transitions.
            near.append(min(hs[i][j]**2/q2[i][j] if q2[i][j] else 0
                            for i in range(2) for j in range(2,6)))
            hists.append(hs)
        bh=[[st.mean(h[i][j] for h in hists) for j in range(10)] for i in range(2)]
        scales[scale]=dict(seed_sigma_fb=totals,mean_sigma_fb=st.mean(totals),
            seed_spread_fb=st.stdev(totals) if len(totals)>1 else None, min_class_neff=min(ms),
            min_threshold_bin_neff=min(near), mean_histograms_fb=bh)
    nom=scales["30"]
    for s in scales.values():
        s["relative_sigma_to_30"]=s["mean_sigma_fb"]/nom["mean_sigma_fb"]-1
    good_class=all(s["min_class_neff"]>=25 for s in scales.values())
    good_bins=all(s["min_threshold_bin_neff"]>=25 for s in scales.values())
    good_total=all(abs(s["relative_sigma_to_30"])<=.15 for s in scales.values())
    match_bins=None
    if good_bins:
        match_bins=all(
          abs(s["mean_histograms_fb"][i][j]/nom["mean_histograms_fb"][i][j]-1)<=.25
          for s in scales.values() for i in range(2) for j in range(2,6)
        )
    native_delta=max(snapshot_diffs)
    native_gate=final_stats is not None and final_stats["validated_at_print_precision"]
    if native_gate:
        expected={(s,seed,k) for s,seeds in v.items() for seed,rs in seeds.items() for k,r in rs.items()
                  if (k=="1" and seed=="41324") or abs(r["native_sigmaGen_fb"]/r["sigma_fb"]-1)>1e-8}
        detected={(r["scale"],r["seed"],r["process"]) for r in final_stats["rows"] if r["pass_rounding"]}
        if detected!=expected or any(r["expected_fb"]!=v[r["scale"]][r["seed"]][r["process"]]["sigma_fb"] for r in final_stats["rows"]):
            raise ValueError("native stats evidence not bound to run records")
    return dict(scales=scales,native_snapshot_max_relative=native_delta if math.isfinite(native_delta) else None,gate=dict(normalization_parity=True if modes=={3} else None,class_effective_n=good_class,
        native_summary_reconciled=native_gate,bin_effective_n=good_bins,inclusive_scale_stability=good_total,threshold_jet_bin_stability=match_bins,
        detector_handoff=native_gate and good_class and good_bins and good_total and match_bins is True))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("rows",type=Path,nargs="?",default=Path("closure-rows.json"))
    p.add_argument("--native-stats",type=Path)
    a=p.parse_args()
    print(json.dumps(assessed(json.loads(a.rows.read_text()),json.loads(a.native_stats.read_text()) if a.native_stats else None),allow_nan=False,
          sort_keys=True,indent=2))
