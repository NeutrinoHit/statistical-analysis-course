"""
Demo for multidimensional Monte Carlo integration:
plain MC vs tensor-product Gauss-Legendre vs adaptive VEGAS.

Install:
    python -m pip install numpy vegas
Run:
    python mc_vegas_demo.py
    # or, from the stat-course root:
    python shared/notebooks/mc_vegas_demo.py
"""

from __future__ import annotations

import itertools
from math import erf
import time

import numpy as np
from numpy.polynomial.legendre import leggauss

try:
    import gvar
    import vegas
except ImportError:  # keep the script readable if vegas is not installed yet
    gvar = None
    vegas = None


# A deliberately difficult but controlled test integral.
# A normalized narrow d-dimensional Gaussian peak inside [0, 1]^d.
# The separable peak is a favorable case for VEGAS: it can learn where
# each coordinate matters and greatly reduce the variance.
d = 8
sigma = 0.10
center = np.array(
    [0.63, 0.37, 0.58, 0.42, 0.69, 0.31, 0.54, 0.46],
    dtype=float,
)
norm1d = 1.0 / (np.sqrt(2.0 * np.pi) * sigma)


def f_batch(x: np.ndarray) -> np.ndarray:
    """Vectorized integrand. x has shape (N, d)."""
    z2 = np.sum(((x - center) / sigma) ** 2, axis=1)
    return np.exp(-0.5 * z2) * norm1d**d


def exact_integral() -> float:
    """Exact value over [0,1]^d, from a product of 1D Gaussian CDFs."""
    a = (0.0 - center) / (np.sqrt(2.0) * sigma)
    b = (1.0 - center) / (np.sqrt(2.0) * sigma)
    one_dim = np.array(
        [0.5 * (erf(float(bi)) - erf(float(ai))) for ai, bi in zip(a, b)]
    )
    return float(np.prod(one_dim))


def plain_mc(N: int, seed: int = 12345) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    x = rng.random((N, d))
    y = f_batch(x)
    return float(np.mean(y)), float(np.std(y, ddof=1) / np.sqrt(N))


def tensor_gauss(m: int, batch_size: int = 200_000) -> tuple[float, int]:
    """Tensor-product Gauss-Legendre rule on [0,1]^d.

    This is intentionally shown because N=m**d grows very fast.
    Batching avoids storing the full grid.
    """
    nodes, weights = leggauss(m)
    nodes = 0.5 * (nodes + 1.0)
    weights = 0.5 * weights

    total = 0.0
    neval = m**d
    xs: list[list[float]] = []
    ws: list[float] = []

    for idx in itertools.product(range(m), repeat=d):
        xs.append([nodes[i] for i in idx])
        w = 1.0
        for i in idx:
            w *= weights[i]
        ws.append(w)

        if len(xs) == batch_size:
            xb = np.asarray(xs)
            wb = np.asarray(ws)
            total += float(np.sum(wb * f_batch(xb)))
            xs.clear()
            ws.clear()

    if xs:
        xb = np.asarray(xs)
        wb = np.asarray(ws)
        total += float(np.sum(wb * f_batch(xb)))

    return total, neval


def vegas_result(
    *,
    nitn_adapt: int = 8,
    neval_adapt: int = 20_000,
    nitn_final: int = 10,
    neval_final: int = 50_000,
    seed: int = 12345,
):
    """Run VEGAS and return the final gvar result."""
    if vegas is None or gvar is None:
        raise RuntimeError("vegas is not installed. Run: python -m pip install vegas")

    gvar.ranseed(seed)

    @vegas.lbatchintegrand
    def f_vegas(x):
        return f_batch(x)

    integ = vegas.Integrator(d * [[0.0, 1.0]])

    # Adaptation pass: do not use this as the final result.
    integ(f_vegas, nitn=nitn_adapt, neval=neval_adapt)

    # Final estimate after adaptation.
    return integ(f_vegas, nitn=nitn_final, neval=neval_final)


def run_vegas() -> None:
    if vegas is None:
        print("vegas is not installed. Run: python -m pip install vegas")
        return

    result = vegas_result()
    print(result.summary())
    print("VEGAS:", result, "Q=", result.Q)


def main() -> None:
    exact = exact_integral()
    print(f"dimension d = {d}")
    print(f"sigma       = {sigma}")
    print(f"exact       = {exact:.12g}\n")

    for N in [10_000, 100_000, 1_000_000]:
        t0 = time.perf_counter()
        val, err = plain_mc(N)
        dt = time.perf_counter() - t0
        pull = (val - exact) / err
        print(
            f"plain MC:   N={N:>9}  {val:.6g} ± {err:.2g}"
            f"   pull={pull:>5.2f}   time={dt:.2f}s"
        )

    print()
    for m in [3, 5, 7]:
        t0 = time.perf_counter()
        val, neval = tensor_gauss(m)
        dt = time.perf_counter() - t0
        print(
            f"Gauss grid: m={m:>2}, N={neval:>9}  {val:.6g}"
            f"   rel.bias={(val - exact) / exact:>7.2%}   time={dt:.2f}s"
        )

    print()
    run_vegas()


if __name__ == "__main__":
    main()
