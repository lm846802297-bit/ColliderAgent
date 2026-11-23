"""Compare the official ATLAS cutflows to genuine nominal HistFactory predictions."""
import argparse
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

CHANNELS = {"WREM_cuts","STCREM_cuts","TRHMEM_cuts","TRMMEM_cuts","TRLMEM_cuts",
            "SRHMEM_mct2","SRMMEM_mct2","SRLMEM_mct2"}
REGIONS = {"LM":(300,75),"MM":(500,0),"HM":(750,100)}
BINS = (("Low","[180,230]"),("Med","[230,280]"),("High",">280"))
CUTS = (r"$m_{\mathrm{CT}}$ $\in$ [180,230] GeV",
        r"$m_{\mathrm{CT}}$ $\in$ [230,280] GeV",
        r"$m_{\mathrm{CT}}$ $>$ 280 GeV")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def verify_blob(raw, pin):
    require(len(raw)==pin["bytes"] and hashlib.sha256(raw).hexdigest()==pin["sha256"],
            "wrong official input fingerprint")
    return raw


def terminal(data, row):
    region, index = row["region"], row["index"]
    masses = REGIONS[region]
    name = f"cutflow_SR_{region}_{BINS[index][0]}_MCT"
    doi = "10.17182/hepdata.90607.v4/t"+str(42+list(REGIONS).index(region)*3+index)
    require((data["name"],data["doi"])==(name,doi)==(row["name"],row["doi"]),
            "wrong official table version, region or bin")
    match = re.search(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*GeV$",data["headers"][-1]["name"])
    require(match and tuple(map(int,match.groups()))==masses==tuple(row["benchmark_masses_GeV"]),
            "wrong locked or published masses")
    require(data["qualifiers"]["SQRT(S)"][0]["value"]=="13000.0 GEV","wrong collision energy")
    y=data["values"][-1]
    require(len(y["x"])==1 and y["x"][0]["value"]==CUTS[index] and len(y["y"])==1
            and isinstance(y["y"][0]["value"],str),"wrong terminal cut row")
    v=Decimal(y["y"][0]["value"])
    require(v.is_finite() and v>0,"invalid weighted yield")
    return v


def round_check(official,prediction):
    tol=Decimal("0.5").scaleb(official.as_tuple().exponent)
    delta=Decimal(str(prediction))-official
    require(abs(delta)<=tol,"selected yield exceeds printed rounding interval")
    return tol,delta


def run(folder,lock):
    import numpy
    import pyhf
    import scipy
    require(pyhf.__version__=="0.7.6","wrong native pyhf version")
    pyhf.set_backend("numpy","scipy",precision="64b")
    arc=verify_blob((folder/lock["archive"]["filename"]).read_bytes(),lock["archive"])
    src={}
    with tarfile.open(fileobj=io.BytesIO(arc),mode="r:gz") as tf:
        for n in ("BkgOnly.json","patchset.json"):
            members=[m for m in tf.getmembers() if m.name==n]
            require(len(members)==1 and members[0].isfile() and members[0].size==lock["members"][n]["bytes"],
                    "wrong original archive member")
            with tf.extractfile(members[0]) as f:
                src[n]=json.loads(verify_blob(f.read(),lock["members"][n]))
    base=src["BkgOnly.json"]
    patches=pyhf.PatchSet(src["patchset.json"])
    patches.verify(base)
    rows,controls=[],[]
    for reg,masses in REGIONS.items():
        signal="C1N2_Wh_hbb_"+"_".join(map(str,masses))
        chan=f"SR{reg}EM_mct2"
        require(tuple(patches[signal].values)==masses,"wrong original patch masses")
        original=patches.apply(base,signal)
        require(original["observations"]==base["observations"],"published observations changed")
        ws=pyhf.Workspace(original)
        model=ws.model()
        cfg=model.config
        require(set(cfg.channels)==CHANNELS and cfg.poi_name=="mu_SIG" and
                ws.measurement_names==["BasicMeasurement"],"unexpected full workspace configuration")
        c=next(c for c in original["channels"] if c["name"]==chan)
        nfs={"name":"mu_SIG","type":"normfactor","data":None}
        match=[s for s in c["samples"] if s["name"]==signal and nfs in s["modifiers"]]
        require(len(match)==1 and len(match[0]["data"])==3,"unexpected signal sample")
        pred=match[0]["data"]
        a=cfg.suggested_init()
        b=list(a)
        a[cfg.poi_index]=0.
        b[cfg.poi_index]=1.
        native=(model.expected_actualdata(b)-model.expected_actualdata(a))[cfg.channel_slices[chan]]
        require(len(native)==3 and max(abs(x-y) for x,y in zip(native,pred,strict=True))<=1e-9,
                "native mean response differs from original sample")
        for i in range(3):
            matches=[r for r in lock["tables"] if (r["region"],r["index"])==(reg,i)]
            require(len(matches)==1,"wrong locked table mapping")
            r=matches[0]
            t=json.loads(verify_blob((folder/r["filename"]).read_bytes(),r))
            y=terminal(t,r)
            tol,delta=round_check(y,pred[i])
            round_check(y,float(native[i]))
            if i==0:
                try:
                    round_check(y,pred[2])
                except ValueError:
                    controls.append(reg+"_swapped_low_high")
                else:
                    raise ValueError("swapped-bin negative control did not fail")
            rows.append(dict(region=reg,workspace_channel=chan,benchmark_masses_GeV=masses,
                             bin_mCT_GeV=BINS[i][1],table_doi=r["doi"],cutflow_printed=str(y),
                             rounding_tolerance_events=str(tol),nominal_sample_events=pred[i],
                             native_delta_mu_events=float(native[i]),sample_minus_cutflow_events=float(delta),
                             native_minus_sample_events=float(native[i]-pred[i])))
    require(len(rows)==9 and len(controls)==3,"incorrect coverage")
    return dict(status="passed",scope="published selected weighted yields vs native nominal means; no fit",
                sqrts_TeV=13,lumi_inverse_fb=139,pyhf=pyhf.__version__,numpy=numpy.__version__,
                scipy=scipy.__version__,channels_per_workspace=len(CHANNELS),rows=rows,
                swapped_controls_rejected=controls)


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("official_input_directory",type=Path)
    p.add_argument("--lock",type=Path,default=Path(__file__).with_name("input-lock.json"))
    a=p.parse_args()
    print(json.dumps(run(a.official_input_directory,json.loads(a.lock.read_text())),indent=2,allow_nan=False))
