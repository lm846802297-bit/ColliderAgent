import copy
import unittest
import pyhepmc as h
import transport as t

P = 682.0
E = 750.0
ONE = {"event_id":"1:11","weight_fb":0.002,"kt":[1.,2.],
 "parents":[[-1000015,[0,0,P,E]],[1000015,[0,0,-P,E]]],
 "other_particles":[[2112,[0,0,0,11500.]]],
 "taus":[
    {"pid":15,"p":[0,0,-600,610.],"neutralino":[0,0,-82,140.],"products":[[16,[0,0,-300,300.]],[-211,[0,0,-300,310.]]]},
    {"pid":-15,"p":[0,0,600,610.],"neutralino":[0,0,82,140.],"products":[[-16,[0,0,300,300.]],[211,[0,0,300,310.]]]}
 ]}


class TestPreservation(unittest.TestCase):
    def setUp(self):
        ri=h.GenRunInfo();ri.weight_names=[t.WEIGHT]
        self.event=t.make_event(ONE,ri)

    def test_nominal(self):
        self.assertEqual(t.verify_event(ONE,self.event), (0.,7,4,0.))

    def test_weight_fails(self):
        self.event.weights=[0.003]
        with self.assertRaisesRegex(ValueError, "event weight"):
            t.verify_event(ONE,self.event)

    def test_event_id_fails(self):
        self.event.event_number=10012
        with self.assertRaisesRegex(ValueError, "source ID"):
            t.verify_event(ONE,self.event)

    def test_daughter_tag_fails(self):
        t0=next(p for p in self.event.particles if p.pid==15)
        t0.end_vertex.particles_out[0].pid=-16
        with self.assertRaisesRegex(ValueError, "tau daughters"):
            t.verify_event(ONE,self.event)

    def test_neutrino_charge_fails(self):
        alt=copy.deepcopy(ONE)
        alt['taus'][0]['products'][0][0]=-16
        with self.assertRaisesRegex(ValueError,"neutrino charge"):
            t.expected(alt)

    def test_hard_stable_duplicate_fails(self):
        self.event.beams[0].end_vertex.add_particle_out(h.GenParticle((0,0,0,11500.),2112,1))
        with self.assertRaisesRegex(ValueError, "primary stable"):
            t.verify_event(ONE,self.event)


if __name__=="__main__":
    unittest.main()
