# One-bin Asimov CLs benchmark

**Purpose:** Does a pinned pyhf inference backend recover the median expected
asymptotic upper limit for a transparent HistFactory likelihood? This is a
synthetic backend test, **not** an observed exclusion, experimental recast,
or validation of asymptotic coverage.

## Fixed fixture and independent derivation

The workspace has one Poisson bin, a fixed background of $b=100$
expected events, and a nominal signal of $s=20$ events multiplied by the
only parameter, the nonnegative dimensionless strength $\mu$.
Use background-only Asimov data $n=b$; there are no nuisance modifiers or
auxiliary observations. This is deliberately not an uncertain-background
simple model. The synthetic observation is not measured data.

At $n=b$, the maximum-likelihood estimate is $\hat{\mu}=0$. With
$\lambda_\mu=b+\mu s$ and
$\ell(\mu)=b\log\lambda_\mu-\lambda_\mu+\mathrm{const}$, the one-sided
bounded profile-likelihood statistic at this Asimov point is

$$
\widetilde q_{\mu,A}=-2[\ell(\mu)-\ell(0)]
= 2\left[\mu s-b\log\!\left(1+\frac{\mu s}{b}\right)\right].
$$

At the background-Asimov median, $CL_b=1/2$ and
$CL_{s+b}=\Phi(-\sqrt{\widetilde q_{\mu,A}})$. The asymptotic $CL_s$
ratio is thus $2\Phi(-\sqrt{\widetilde q_{\mu,A}})$. Solve $CL_s=0.05$
by independent bounded bisection. The reference is:

- $\mu_{95} = 1.0450250398233$, bracket width below $10^{-12}$.
- $CL_s(\mu=1)=0.0600613883881$.
- Doubling nominal $s$ halves the bound on $\mu$ at fixed $b$.
- Omitting $CL_b$, or using the $CL_{s+b}=0.05$ cutoff $1.6448536270$
  instead of the $CL_s=0.05$ Asimov cutoff $1.9599639845$,
  fails the negative controls.

See [Cowan, Cranmer, Gross and Vitells, arXiv:1007.1727v3](https://arxiv.org/abs/1007.1727v3)
for the one-sided test statistic and background-Asimov method. The ratio
definition is explicit in the
[pyhf 0.7.6 calculator source](https://github.com/scikit-hep/pyhf/blob/b500270c6a7744d16b481dfda247c066ef3c2cb4/src/pyhf/infer/calculators.py#L462-L468).

## Reproduce and check the optional backend

~~~sh
python scripts/one_bin_asimov_limit.py
python -m unittest discover -s scripts/tests -p test_one_bin_asimov_limit.py -v
~~~

This standard-library route emits the full synthetic workspace, five
pointwise checks and the limit bracket. It does not import pyhf. To check a
trusted, **already configured** runtime with pyhf **0.7.6**, opt in:

~~~sh
python scripts/one_bin_asimov_limit.py --native
~~~

The release tag resolves to commit
`b500270c6a7744d16b481dfda247c066ef3c2cb4`; the
[pinned interval implementation](https://github.com/scikit-hep/pyhf/blob/b500270c6a7744d16b481dfda247c066ef3c2cb4/src/pyhf/infer/intervals/upper_limits.py)
defines the bracketed solver used here. The replay checks that the native
workspace has exactly the intended POI and no auxiliary data. It uses
NumPy 64-bit and the asymptotic `qtilde` calculator, validates the scan
endpoints for all bands before invoking the solver, and compares the
synthetic-as-observed and median expected limits and pointwise $CL_s$ values
to the independent oracle. Acceptance requires maximum absolute residual
$5\times10^{-7}$ on $CL_s$ and $5\times10^{-6}$ on $\mu_{95}$.
The other expected bands are used only for safe scan bracketing.

Discovery or a missing/wrong version must not count as a native pass.
There is no installation, data retrieval, or remote execution. The current
checked result is the independent reference; native pyhf parity remains
**NOT RUN** on hosts without the pinned runtime. A later successful replay
only passes this specific synthetic backend gate.
