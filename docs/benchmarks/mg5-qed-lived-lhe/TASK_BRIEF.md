# Native MadGraph to LHE to independent muon cutflow

Objective: verify ColliderAgent's parton-event production and analysis handoff, extending the analytic-only QED benchmark. Question: can pinned MG5 v3.5.17 generate the photon-only SM muon-pair ensemble and does an independent LHE reader recover its analytic normalization and angular acceptance?

Use native compiled MG5 v3.5.17 commit 4492b3e392effbb650447763fef5f67700673f03 and authenticated GNU 14.2.0-19. At 50+50 GeV e+/e− beams, use e+ e− > mu+ mu− excluding Z, fixed seed 27183, LO and 5,000 unweighted events, no showers, ISR, PDF or beam spectrum, no lepton generation cuts. Read actual α from the preserved generated param card. Compare to massless Born QED with negligible muon mass effects at 100 GeV.

Acceptance before generation: independent cross section 4πα²/(3s) in pb within max(0.5%, five reported integration errors), correct incoming and outgoing IDs and five thousand positive common-weight LHE records, against 2e-5 GeV tolerance per momentum component. At |cos θ|<0.8 require acceptance compatible with 0.728 at five binomial standard errors. Rejection controls: truncated or malformed LHE must fail. Record generator cards, exact software, original event files and weights, and distinguish successful handoff from detector or new analysis/limit validation.
