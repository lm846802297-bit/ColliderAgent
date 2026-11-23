# Standard elastic halo interface benchmark

**Question:** Does the Standard Halo Model (SHM) mean inverse speed used by
an ordinary elastic recoil interface agree with an independent numerical
normalization and the recoil-to-speed unit map? This is a synthetic
ColliderAgent backend contract. **Native DDCalc is not run.** No target
response, efficiency, event rate, exclusion, or radiative/inelastic
kinematics is included.

## Fixed inputs and sources

Use a Galactic-frame spherical cutoff, $v_0=220$ km/s,
$v_{\rm esc}=544$ km/s, and a scalar lab boost of 232 km/s or 0 for the
unboosted control. These are benchmark inputs, not an inference of the
Earth's motion. The scoped domain is $0\le V<v_{\rm esc}$; the stationary
case is handled separately.

- [Baxter et al., arXiv:2105.00599v3, §3.1, Eqs. (10–12)](https://arxiv.org/pdf/2105.00599v3#page=10):
  (truncated) Galactic Maxwellian, speed conventions and frame translation.
- [DDCalc v2.3.0, src/DDHalo.f90](https://github.com/GambitBSM/DDCalc/blob/065c126c563107de090a9644bed997462d72ec61/src/DDHalo.f90#L596-L718):
  pinned $E_R$ to $v_{\min}$ map and analytic mean inverse speed; source
  SHA-256 is
  `c3e7ef05c339f66f3a22727a7410c7f031bfd799aecd5806bcc18a07288d1529`.
  [DDRates.f90](https://github.com/GambitBSM/DDCalc/blob/065c126c563107de090a9644bed997462d72ec61/src/DDRates.f90#L228-L240)
  uses these values in its elastic rate pipeline. The tool's direct-search
  phenomenology scope is described in the
  [pinned README](https://github.com/GambitBSM/DDCalc/blob/065c126c563107de090a9644bed997462d72ec61/README.md)
  and in [Bringmann et al., arXiv:1705.07920v2](https://arxiv.org/abs/1705.07920v2).
  These references identify conventions, not an executed native result.

## Definitions and independent computation

For elastic scattering in the nonrelativistic target rest frame, the
three-momentum magnitude $q=|\mathbf q|$ obeys $q^2=2m_A E_R$. The minimum incident speed is $q/(2\mu_A)$ with
$\mu_A=m_\chi m_A/(m_\chi+m_A)$. For energies in keV and masses in GeV,

$$
v_{\min}\,[{\rm km/s}]
= c\,[{\rm km/s}]\sqrt{\frac{m_A\,(10^{-6}E_R)}{2\mu_A^2}}.
$$

For halo velocities define $z=v_{\rm esc}/v_0$ and
$N=\operatorname{erf}z-2ze^{-z^2}/\sqrt{\pi}$. The lab-frame
inverse speed is

$$
\eta(v_{\min})=\int_{w\ge v_{\min}}\frac{f_{\rm lab}(\mathbf w)}{w}\,d^3w,
$$

in s/km. For $V>0$, writing $x=v_{\min}/v_0$ and $y=V/v_0$,
integrating the angularly shifted Maxwellian yields the following
numerators, each divided by $2NV$:

$$
\begin{cases}
\operatorname{erf}(x+y)-\operatorname{erf}(x-y)-4ye^{-z^2}/\sqrt{\pi},
 & x<z-y,\\[2pt]
\operatorname{erf}(z)-\operatorname{erf}(x-y)-2(z+y-x)e^{-z^2}/\sqrt{\pi},
 & z-y\le x<z+y,\\[2pt]
0, & x\ge z+y.
\end{cases}
$$

For $V=0$, integrate the ordinary Galactic radial density to obtain
$2(e^{-x^2}-e^{-z^2})/(\sqrt{\pi}Nv_0)$ for $x<z$, otherwise zero.

The independent computation keeps each **Galactic** shell of speed $u$.
For $V>0$ the allowed lab speeds on a shell span $[|u-V|,u+V]$.
Change its angular variable to $w$; the angular Jacobian contributes
$w/(uV)$ and cancels the $1/w$ integrand. The allowed angular width in
$w$ above the threshold is therefore
$[u+V-\max(|u-V|,v_{\min})]_+$.
Use composite Simpson integration of the resulting radial expression,
split at changes in support, and calculate the normalization separately
from $\int_0^{v_{\rm esc}}du\,u^2e^{-(u/v_0)^2}$. This route does not use
the piecewise lab-frame error-function formula.

## Reproduce the check

~~~sh
python scripts/elastic_shm_reference.py
python -m unittest discover -s scripts/tests -p test_elastic_shm_reference.py -v
~~~

The first command emits the complete pointwise synthetic comparison as JSON.
The fixed 18-point block exercises the branch join/cutoff, zero boost and
radial refinement. Both eta comparison and refinement must be within
$2\times10^{-11}$ s/km; relative normalization error must be below
$2\times10^{-9}$. At 8 keV, for masses 122 and 50 GeV, the reference gives
$v_{\min}=186.73650484$ km/s. Omitting keV-to-GeV conversion raises this by
$10^3$ and incorrectly eliminates support. The output's
`native_ddcalc: NOT_RUN` status is independent of the reference status.

## Archived synthetic fixture

The [task brief](benchmarks/elastic-shm/TASK_BRIEF.md), [exact reference JSON](benchmarks/elastic-shm/reference.json)
and [replay manifest](benchmarks/elastic-shm/run_manifest.json) preserve the
fixed benchmark. Before replay, check the manifest's SHA-256 digests of the
source and fixture. In the recorded environment, the command above produced
the archived JSON byte-for-byte twice. On another host, use the explicit
numerical tolerances to judge backend parity. This is a tooling fixture,
not a scientific run or an RCRPS record.
