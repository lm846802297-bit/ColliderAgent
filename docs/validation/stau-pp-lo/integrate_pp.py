"""NNPDF2.3-LO and a Born-only hard process; not ATLAS matched production."""
import argparse
import ctypes
import json
import math
import sys
from pathlib import Path
import numpy as np

from stau_born import born

S = 13000.**2
T0 = 800.**2/S
LMIN = math.log(T0)
PIDS = dict(enumerate("duscb",1))


class PDF:
    def __init__(self, so, root, positive=True):
        lib = ctypes.CDLL(str(Path(so).resolve()))
        lib.pdf_init.argtypes = [ctypes.c_char_p]
        lib.pdf_init.restype = ctypes.c_int
        lib.pdf_light.argtypes = [ctypes.c_double, ctypes.c_double,
                                 ctypes.POINTER(ctypes.c_double)]
        lib.pdf_light.restype = ctypes.c_int
        if lib.pdf_init(str(Path(root).resolve()).encode()):
            raise RuntimeError("could not initialize native LHAPDF")
        self.lib = lib
        self.positive = positive

    def values(self, x, q):
        out = (ctypes.c_double*10)()
        if self.lib.pdf_light(x,q,out):
            raise ValueError(f"PDF rejected x={x} scale={q}")
        return [max(v,0.) for v in out] if self.positive else list(out)


def channel_weights(pdf, x1, x2, q, shat, state):
    f, g = pdf.values(x1,q), pdf.values(x2,q)
    energy=math.sqrt(shat)
    return [(pid,ori,born(energy,char,state)*f[2*(pid-1)+ori]*g[2*(pid-1)+1-ori])
        for pid,char in PIDS.items() for ori in (0,1)]


def convolute(pdf, n, coordinates, scale=400.):
    x,w=np.polynomial.legendre.leggauss(n)
    result = np.zeros((2,5))
    for u,wu in zip(x,w):
        for v,wv in zip(x,w):
            if coordinates=="logtau_y":
                logt = LMIN*(1-u)/2
                ymax = -logt/2
                y = v*ymax
                t = math.exp(logt)
                x1,x2=math.exp(logt/2+y),math.exp(logt/2-y)
                jac=(-LMIN/2)*ymax
            else:
                x1=T0+(1-T0)*(1+u)/2
                a=T0/x1
                x2=a+(1-a)*(1+v)/2
                t=x1*x2
                jac=((1-T0)*(1-a)/4)/t
            for i,state in enumerate("LR"):
                for pid,_,wt in channel_weights(pdf,x1,x2,scale,t*S,state):
                    result[i,pid-1]+=jac*wu*wv*wt
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--library",default="./pdf_bridge.so")
    p.add_argument("--pdf-dir",default=".")
    p.add_argument("--orders",nargs="+",type=int,default=[24,48,96])
    args=p.parse_args()
    pdf=PDF(args.library,args.pdf_dir)
    report={f"{coords}:{n}":convolute(pdf,n,coords).tolist() for n in args.orders
            for coords in ("logtau_y","x1_x2")}
    a,b=(np.array(report[f"{c}:{args.orders[-1]}"]) for c in ("logtau_y","x1_x2"))
    maxerr=float(np.max(np.abs(a-b)/a))
    raw=convolute(PDF(args.library,args.pdf_dir,positive=False),args.orders[-1],"logtau_y")
    clipping=float(np.max(np.abs(raw-a)/a))
    tot=np.sum(a,axis=1)
    print(json.dumps(dict(beam_cme_gev=13000,scale_gev=400,pdf="NNPDF23_lo_as_0130_qed/0",
          pid_order=[1,2,3,4,5],state_order=["L","R"],by_flavor_fb=report,
          final_total_fb=tot.tolist(),max_rel_diff=maxerr,
          largest_pdf_positivity_shift=clipping, accepted=maxerr<.001 and clipping<.001,level="LO_Born_parton_luminosity_only"),sort_keys=True,indent=2))
    return int(maxerr>=.001 or clipping>=.001)


if __name__=="__main__":
    sys.exit(main())
