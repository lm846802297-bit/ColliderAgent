import json
import sys
import tempfile
import unittest
from pathlib import Path

import sympy as sp

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import canon_pdb_intake as p
import loop_basis_verify as gate


class IntakeTests(unittest.TestCase):
    def test_momenta_and_denominators(self):
        s,t,q3,q4,m=p.X
        assert sp.expand(sum(p.G))==q4
        assert (p.G[1,1]+p.G[2,2]+2*p.G[1,2]).expand()==t
        ds,scalar=p.propagators_and_map()
        for d,z in zip(ds,p.Z):
            assert sp.expand(d.subs(scalar,simultaneous=True)-z)==0
        assert ds[6]==p.V[1]-2*p.V[7]-2*p.V[8]+t-m

    def test_all_directions_against_explicit_four_vectors(self):
        metric=sp.diag(1,-1,-1,-1)
        ext=sp.Matrix([[1,1,0,0],[2,-2,0,0],[3,1,1,0]])
        loops=sp.Matrix([[4,1,1,2],[5,-1,3,1]])
        gram=ext*metric*ext.T
        m=sp.Integer(7)
        s=2*gram[0,1]
        t=gram[2,2]+2*gram[1,2]
        at=dict(zip(p.X,(s,t,gram[2,2],sum(gram),m)))
        self.assertEqual(p.G.subs(at),gram)
        q=sp.Symbol("q")
        # Solve the full linear directional constraint instead of reusing
        # the closed dG*G^-1 formula. Its antisymmetric freedom is fixed
        # by requiring (C G) to be symmetric.
        entries=sp.symbols("a:9")
        a=sp.Matrix(3,3,entries)
        for x in p.X:
            target=p.G.diff(x)
            equations=list(a*gram+gram*a.T-target)+list(a*gram-gram*a.T)
            c=a.subs(sp.solve(equations,entries,dict=True)[0])
            perturbed=(sp.eye(3)+q*c)*ext
            source=dict(at)
            for i,(l,e,mass) in enumerate(zip(p.LOOPS,p.EXT,p.MASS)):
                v=sp.Matrix([l])*loops+sp.Matrix([e])*ext
                source[p.Z[i]]=(v*metric*v.T)[0]-sp.sympify(mass).subs(at)
            for i,(l,e,mass) in enumerate(zip(p.LOOPS,p.EXT,p.MASS)):
                v=sp.Matrix([l])*loops+sp.Matrix([e])*perturbed
                want=(v*metric*v.T)[0].diff(q).subs(q,0)-sp.sympify(mass).diff(x)
                got=sum(c0*sp.prod(z**power for z,power in zip(p.Z,exponents))
                        for exponents,c0 in p.denominator_derivatives()[x][i].items()).subs(source)
                self.assertEqual(got,want)

    def test_mass_derivative_sign(self):
        indices=(1,1,1,1,1,1,2,0,0)
        assert p.derivative(indices,p.M)=={(1,1,1,1,1,1,3,0,0):sp.Integer(2)}

    def test_euler_before_reduction(self):
        ds,scalar=p.propagators_and_map()
        # Independently obtain half the loop Euler derivative by scaling
        # all loop scalar products as l^2 and loop-external products as l.
        k=sp.Symbol("k")
        rules={x:x*k**(2 if i<3 else 1) for i,x in enumerate(p.V)}
        for i,(d,z) in enumerate(zip(ds,p.Z)):
            loop=d.subs(rules,simultaneous=True).diff(k).subs(k,1)/2
            total=loop.subs(scalar,simultaneous=True)+sum(
                x*sum(c*sp.prod(z0**a for z0,a in zip(p.Z,pow0))
                      for pow0,c in p.denominator_derivatives()[x][i].items()) for x in p.X)
            assert sp.cancel(total-z)==0

    def test_executable_pdb_subtopology_and_missing_rule(self):
        # Sector 30 factorizes into two massless bubbles carrying s. The
        # scales other than s decouple. Verify assembly with the closed
        # physical D2,D3,D4,D5 example using its analytic scaling row.
        eps=sp.Symbol("eps")
        I=p.identity((0,1,1,1,1,0,0,0,0))
        dot=p.identity((0,1,2,1,1,0,0,0,0))
        # Each bubble has B_12/B_11=(3-d)/s from IBP, scaleless B_02=0;
        # differentiate the two integrated bubbles: B' = (d-4)/(2s)*B.
        # Fixture expresses the same row in terms of a dotted bubble
        # plus a master coefficient, not a native Kira run.
        fd={"masters":[I],"directions":{str(x):[{}] for x in p.X}}
        fd["directions"]["s"]=[{dot:"-1",I:"-1/s"}]
        rules={"schema":"pheno-pdb-ibp-v1","masters":[I],"rules":{dot:{I:"(3-d)/s"}}}
        src=p.assemble(fd,rules,{"scale":"s"})
        assert src["connections"]["s"]==[[0,0,"-2*eps/s"]]
        raw=json.dumps(src).encode()
        candidate=dict(schema="pheno-loop-proposal-v1",source_sha256=gate.digest(raw),
                       transform=[[0,0,1]],inverse=[[0,0,1]],residues={"scale":[[0,0,-2]]})
        assert gate.verify(raw,json.dumps(candidate).encode())["status"]=="PASS"
        rules["rules"][dot][I]="(d-3)/s"
        with self.assertRaisesRegex(ValueError,"Euler identity"):
            p.assemble(fd,rules,{"scale":"s"})
        rules["rules"].clear()
        with self.assertRaisesRegex(ValueError,"missing required IBP rule"):
            p.assemble(fd,rules,{"scale":"s"})

    def test_package_all_directions_and_scale(self):
        indices=(1,1,1,1,1,1,1,0,0)
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"job"
            p.package([indices],out)
            config=(out/"config/kinematics.yaml").read_text()
            assert "symbol_to_replace_by_one" not in config
            a=json.loads((out/"precanonical-derivatives.json").read_text())
            assert len(a["directions"])==5 and a["target_count"]>5
            assert p.identity((1,1,1,1,1,1,2,0,0)) in (out/"targets").read_text()
        with self.assertRaisesRegex(ValueError,"37 distinct"):
            p.parse_masters(p.identity(indices),37)


if __name__=="__main__":
    unittest.main()
