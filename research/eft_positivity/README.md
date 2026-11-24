# Optional aQGC EFT positivity check

Implements **only** the W–B–H M-sector constraint in [Chang, Wan & Zhou,
arXiv:2611.26692v1](https://arxiv.org/html/2611.26692v1), Eq. (18), not the
full positivity cone. This is a standalone tool, not on the default analysis path.

## Use

From the repository root:

```sh
python python-agent/tools/eft_positivity_eq18.py research/eft_positivity/eq18-example.json
```

Supply exactly `F_M1`, `F_M3`, `F_M5`, `F_M7` inside `coefficients`. Use
integers or exact decimal/rational strings; the executable uses only the Python
standard library. Declare `unit` as `GeV^-4` or `TeV^-4` for **all** four.
No conversion from raw generator/model cards is attempted; the unit and basis
tag are caller attestations, not proof that a mapping was performed.

The basis tag requires Appendix D Eqs. (43)–(46), including its operator
normalizations and gauge factors: for the four inputs, Eq. (46) gives
$g^2 f_{M1}$, $g'^2 f_{M3}$, $gg' f_{M5}$, $g^2 f_{M7}$, respectively.
Supply their dimensionful values after dividing by the common $\Lambda^4$
if starting from dimensionless coefficients. Do not pass bare $f_{Mi}$ or
same-name coefficients from different operators. An unknown convention, missing
input or malformed coefficient returns `UNDETERMINED`. Invalid JSON syntax and
duplicate keys are input errors (nonzero CLI exit).

The exact conditions are $a=F_{M7}-8F_{M1}\ge0$, $c=-4F_{M3}\ge0$,
and $ac-F_{M5}^2\ge0$. The three possible determinate labels are
`INTERIOR` (positive definite), `BOUNDARY` (singular positive semidefinite,
including zero), and `OUTSIDE` (not positive semidefinite), **for this block
only**. The matrix entries have the declared coefficient unit and the
determinant has its square. The signs are exact for the supplied numbers;
finite data uncertainties or rounded EFT matching are not automatically
interpreted as exact physical saturation.

## Verification

```sh
python -m unittest discover -s python-agent/tests -p test_eft_positivity_eq18.py -v
```

Independent numerical diagonalization for the tests uses NumPy (not needed by
the CLI). Five heavy vector controls use the tree-level matching accompanying
Eq. (20): the signed matrix must exactly equal the outer product of
$(2\tilde g_1,-4\tilde g_2)$ multiplied by $\lambda$. These controls include
both interference signs and the degenerate axes/origin; the nonzero mixed
examples also check the Eq. (19) null direction. Six synthetic controls check
interior, determinant violation, and diagonal sign violations. Numeric parity
uses a relative test tolerance; a separate exact test resolves perturbations of
$10^{-60}$ that the floating-point diagonalization cannot distinguish.
The input example uses real couplings 2 and 3 and $\lambda=(1/81)\,\mathrm{TeV}^{-4}$.
The example is a matching regression, not a claim of a renormalizable UV model
or a physically perturbative benchmark. No other positivity bounds, VBS data,
likelihoods, clipping of parameter scans or interval construction are included.
