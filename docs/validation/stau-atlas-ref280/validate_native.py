"""Verify the frozen hard-event and CKKW-L plumbing checkpoints."""
import json
from pathlib import Path
from audit_mg5_lhe import audit
from public_cutflow import audit as audit_data


def verify():
    p=Path("unweighted_events.lhe.gz")
    x=audit(p)
    gold=json.loads(Path("mg5-hard-result.json").read_text())
    assert x==gold and x["events"]==1000
    a=json.loads(Path("ckkwl-result.json").read_text())
    assert len(a["trials"])==24
    indexed={(v["scale_gev"],v["process"],v["estimation_phase"]):v for v in a["trials"]}
    checks={}
    for scale in (20.,40.):
        accepted=nonzero=0
        for proc in range(1,7):
            e=indexed[scale,proc,True]
            v=indexed[scale,proc,False]
            n=a["counts"][str(proc)]
            assert 0<v["weights_nonzero"]<=v["successful"]==e["successful"]<=n
            assert e["successful"]==e["weights_nonzero"] and e["weight_max"]==1
            assert e["veto_or_trial_failure"]==v["veto_or_trial_failure"]==0
            accepted+=v["successful"]
            nonzero+=v["weights_nonzero"]
        checks[str(scale)]={"above_matching_cut":accepted,"nonzero_ckkwl_weight":nonzero}
    assert checks["20.0"]["above_matching_cut"]>checks["40.0"]["above_matching_cut"]
    assert audit_data()==json.loads(Path("cutflow-result.json").read_text())
    return {"scope":"native hard event and CKKW-L interface; no detector gate passed",
            "status":"PASS", "validated_trials":24, "by_scale":checks}


if __name__=="__main__":
    print(json.dumps(verify(),indent=2,sort_keys=True))
