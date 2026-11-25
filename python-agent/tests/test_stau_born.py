import importlib.util
import math
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("stau_born", ROOT/"python-agent/tools/stau_born.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

I = np.eye(2)
Z = np.zeros((2,2))
SIG = [np.array(x) for x in ([[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]])]
G = [np.block([[I,Z],[Z,-I]])] + [np.block([[Z,p],[-p,Z]]) for p in SIG]
G5 = 1j*G[0]@G[1]@G[2]@G[3]
P = [(np.eye(4)-G5)/2,(np.eye(4)+G5)/2]


def slash(v):
    return G[0]*v[0]-sum(g*x for g,x in zip(G[1:],v[1:]))


def trace_rate(energy, quark, state):
    shat, e = energy**2, energy/2
    p = math.sqrt(e**2-400**2)
    sw = math.sqrt(0.23122)
    cw = math.sqrt(1-sw**2)
    em = math.sqrt(4*math.pi/128)
    qu = 2/3 if quark in ("u","c") else -1/3
    t3q = (1 if qu > 0 else -1)/2
    t3s = {"L": -.5,"R": 0}[state]
    scalar_z = em/(sw*cw)*(t3s+sw**2)
    neutral = (
        em**2*qu*(-1)/shat*np.eye(4)
        + scalar_z*em/(sw*cw)*(t3q*P[0]-qu*sw**2*np.eye(4))/(shat-91.1876**2)
    )
    # Integrate with an independent 8-point Gauss rule and explicit trace.
    x, w = np.polynomial.legendre.leggauss(8)
    values = []
    for c in x:
        v = slash([0,2*p*math.sqrt(1-c*c),0,2*p*c])@neutral
        bar = G[0]@v.conj().T@G[0]
        values.append(np.trace(slash([e,0,0,-e])@v@slash([e,0,0,e])@bar).real/12)
    return (p/e)*float(np.dot(w,values))/(32*math.pi*shat)*3.89379338e11


class StauTests(unittest.TestCase):
    def test_trace_all_flavors_and_chiralities(self):
        for energy in (800.01, 1000, 1500, 3000):
            for q in "udscb":
                for state in "LR":
                    with self.subTest(energy=energy,quark=q,state=state):
                        self.assertAlmostEqual(b.born(energy,q,state)/trace_rate(energy,q,state),1,places=10)

    def test_photon_only_and_chiral_split(self):
        for state in "LR":
            e = 1000
            beta = math.sqrt(1-(800/e)**2)
            qed = 3.89379338e11*math.pi*(1/128)**2*(2/3)**2*beta**3/(9*e**2)
            self.assertAlmostEqual(b.born(e,"u",state,True)/qed,1,places=13)
        self.assertNotAlmostEqual(b.born(1000,"u","L"),b.born(1000,"u","R"))

    def test_threshold_is_closed(self):
        self.assertEqual(b.born(799,"u","L"),0)
        self.assertEqual(b.born(800,"u","L"),0)
        with self.assertRaisesRegex(ValueError,"open phase space"):
            b.generate(800,"u","L",1,5)
        self.assertAlmostEqual(b.born(800.0004,"u","L")/b.born(800.0001,"u","L"),8,places=4)

    def test_width_and_exact_decay(self):
        self.assertAlmostEqual(b.partial_width("R")/b.partial_width("L"),4,places=14)
        self.assertGreater(b.partial_width("L"),0)
        for q,state in (("u","L"),("d","R")):
            sample = b.generate(1000,q,state,128,431)
            self.assertAlmostEqual(len(sample["events"])*sample["equal_event_weight_fb"],sample["partonic_sigma_fb"])
            for event in sample["events"]:
                for suffix in ("minus","plus"):
                    parent = np.array(event["stau_"+suffix])
                    tau = np.array(event["tau_"+suffix])
                    chi = np.array(event["chi_"+suffix+"_parent"])
                    np.testing.assert_allclose(tau+chi,parent,atol=1e-11,rtol=0)
                    for v,m in ((parent,400),(tau,1.77686),(chi,80)):
                        self.assertAlmostEqual(v[0]**2-np.dot(v[1:],v[1:]),m*m,places=8)
                np.testing.assert_allclose(
                    np.array(event["stau_minus"])+np.array(event["stau_plus"]),[1000,0,0,0],atol=1e-11,rtol=0)

    def test_independent_seeds_and_production_moments(self):
        for seed in (431,7012):
            events = b.generate(1000,"u","L",8192,seed)["events"]
            c = np.array([ev["cos_theta"] for ev in events])
            self.assertLess(abs(c.mean()),5*math.sqrt(.2/len(c)))
            self.assertLess(abs(np.mean(c*c)-.2),5*math.sqrt((3/35-(1/5)**2)/len(c)))
        self.assertEqual(b.generate(1000,"u","L",8,431),b.generate(1000,"u","L",8,431))
        self.assertNotEqual(b.generate(1000,"u","L",8,431),b.generate(1000,"u","L",8,7012))


if __name__ == "__main__":
    unittest.main()
