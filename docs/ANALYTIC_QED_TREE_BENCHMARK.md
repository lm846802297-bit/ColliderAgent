# FeynArts → FeynCalc tree benchmark contract

**Status:** Exact independent Python reference checked. Native Wolfram run
and package interoperability are **NOT RUN**. This is a reusable toolchain
test, not a project calculation, simulation, or statistical limit.

## Source and setup

Use the native route in the [analytic toolchain guide](ANALYTIC_TOOLCHAIN.md)
only on an approved host. The pinned working-example source is FeynCalc
**10.2.1**, tag `Release-10_2_1`, commit
`782aa16e7187ea9226c09a07be7f947c24fca2f5`.
Its [tree-level QED example](https://github.com/FeynCalc/feyncalc/blob/782aa16e7187ea9226c09a07be7f947c24fca2f5/FeynCalc/Examples/QED/Tree/Mathematica/ElAel-MuAmu.m)
has SHA-256 `c29ddfa3209ec0abf37298d5e4040e8e5844d2202e5283512e655c3047514892`.
It uses the FeynArts add-on loader, the `QEDOnly` restriction and
`FCFAConvert` in four dimensions. The
[pinned interface notes](https://github.com/FeynCalc/feyncalc/blob/782aa16e7187ea9226c09a07be7f947c24fca2f5/FeynCalc/Documentation/Markdown/Extra/FeynArts.md)
explain patched versus standalone FeynArts installation. The
[FeynArts 3.12 source mirror](https://github.com/FeynCalc/feynarts-mirror/tree/024e6976523eea5ab4d22f6d9869b978b0f3f7a6)
identifies the candidate unpatched base. This does not assert that a local
patched copy or a specific kernel version was run. Record the actual kernel,
FeynCalc, FeynArts patch/model identities and their file hashes separately.

Use a fresh authorized local kernel and a reviewed compatible package
installation. Do not mix independently loaded unpatched FeynArts with the
patch/add-on interface. Do not download, patch an installation, or start an
external service as a side effect of this benchmark. Do not copy the upstream
script into the repository. An upstream example's reported success is not a
local execution result.

## Conventions and independent oracle

Consider massless, unpolarized `e⁻(p1) e⁺(p2) → μ⁻(k1) μ⁺(k2)` in four
dimensions, metric `(+---)`, distinct final particles, only the tree
s-channel photon, with no weak exchanges or radiation. Use natural units,
positive-energy physical four-vectors and `s=(p1+p2)²`,
`t=(p1-k1)²`, `u=(p1-k2)²`; translate to all-incoming signs at
`SetMandelstam`. Set both lepton masses to zero and average over **both**
incoming spins. The overall amplitude phase is not a physics comparison.

For a current trace write
`T(a,b)^(μν) = a^μ b^ν + a^ν b^μ − g^(μν) a·b`
so the four-gamma trace is `4T`. Contract the two tensors with the
metric, giving `M̄²/e⁴ = 4 T(p2,p1)^(μν) T(k1,k2)_(μν)/s²`.
This trace gives `2(t²+u²)/s² = 1+cos²θ` and both tensors are transverse
to `q=p1+p2=k1+k2`. The separate Python oracle computes the contraction
from integer four-vectors and exact fractions, with no Wolfram, FeynCalc,
FeynArts, or MadGraph calls:

```sh
python scripts/qed_tree_reference.py
```

With `α=e²/(4π)` and the massless flux and two-body phase space,
`dσ/dΩ = α²(1+cos²θ)/(4s)` and `σ = 4πα²/(3s)`. At
`cosθ=3/5`, compare `t/s=-1/5`, `u/s=-4/5` separately: a test of the
spin average alone cannot detect a swap of `t` and `u`. The exact point
matrix includes forward/backward limits, `cosθ=±3/5`, the central point,
and fixed angle at two energies.

## Native acceptance evidence

1. Report the selected diagrams and show one photon exchange with no
   substituted zero diagram or weak contribution.
2. Save the native converted amplitude and its spin-averaged square.
   Require the exact symbolic residual from `2e⁴(t²+u²)/s²` to vanish
   under the massless constraint and check the signed invariants and all
   six point controls against the independent oracle. Check conservation
   on the two currents before any gauge-dependent term could contribute.
3. Keep the differential and total cross-section normalization separate
   from the spin-average check, including the `1/s` scaling. The
   center-angle value `M̄²/e⁴=1` rejects a missing initial `1/4` factor;
   the forward/backward value 2 rejects an angle-independent output.
4. Record the exact source/version, model/patch identities, invocation,
   native outputs, log and residuals. A package load, example source
   download, or Python oracle run is not evidence for a native pass.
