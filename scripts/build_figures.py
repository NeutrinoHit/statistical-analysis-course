from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from helpers import ensure_dir, project_root


def build_normal_density(out_dir: Path) -> None:
    x = np.linspace(-4.0, 4.0, 400)
    y = np.exp(-0.5 * x**2) / math.sqrt(2.0 * math.pi)

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.plot(x, y, color="#1f5f8b", linewidth=2.2)
    ax.set_xlabel("x")
    ax.set_ylabel("density")
    ax.set_title("Standard normal density")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "normal_density.png", dpi=160)
    plt.close(fig)


def build_poisson_pmf(out_dir: Path, lam: float = 4.0) -> None:
    k = np.arange(0, 15)
    pmf = np.exp(-lam) * lam**k / np.array([math.factorial(int(v)) for v in k])

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.vlines(k, 0.0, pmf, color="#c44536", linewidth=2.0)
    ax.scatter(k, pmf, color="#c44536", s=28)
    ax.set_xlabel("k")
    ax.set_ylabel("P(X = k)")
    ax.set_title(f"Poisson PMF, lambda = {lam:g}")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "poisson_pmf.png", dpi=160)
    plt.close(fig)


def build_poisson_pmf_profiles(out_dir: Path) -> None:
    configs = [(1, "#1f3db8"), (4, "#2e8b57"), (10, "#d62728")]

    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    k = np.arange(0, 26)
    factorials = np.array([math.factorial(int(i)) for i in k], dtype=float)
    for lam, color in configs:
        pmf = np.exp(-lam) * lam**k / factorials
        ax.plot(
            k,
            pmf,
            marker="o",
            markersize=5.2,
            linewidth=1.3,
            color=color,
            markeredgecolor="black",
            markeredgewidth=0.4,
            label=rf"$\lambda$={lam}",
        )

    ax.set_xlim(0, 25)
    ax.set_ylim(0, 0.40)
    ax.set_xlabel("k")
    ax.set_ylabel("P(k)")
    ax.set_title("Распределение Пуассона")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "poisson_pmf_profiles.png", dpi=180)
    plt.close(fig)


def build_binomial_pmf_profiles(out_dir: Path, p: float = 0.3) -> None:
    configs = [(5, "#1f3db8"), (20, "#2e8b57"), (100, "#d62728")]

    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    for n, color in configs:
        k = np.arange(0, n + 1)
        pmf = np.array(
            [math.comb(n, int(i)) * p**i * (1.0 - p) ** (n - i) for i in k],
            dtype=float,
        )
        ax.plot(
            k,
            pmf,
            marker="o",
            markersize=5.2,
            linewidth=1.3,
            color=color,
            markeredgecolor="black",
            markeredgewidth=0.4,
            label=f"n={n}\np={p:g}",
        )

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 0.40)
    ax.set_xlabel("k")
    ax.set_ylabel("P(k)")
    ax.set_title("Биномиальное распределение")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "binomial_pmf_profiles.png", dpi=180)
    plt.close(fig)


def build_normal_density_profiles(out_dir: Path) -> None:
    configs = [
        (0, 1, "#1f3db8"),
        (0, 2, "#2e8b57"),
        (2, 1, "#d62728"),
    ]
    x = np.linspace(-6.0, 6.0, 500)

    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    for mu, sigma, color in configs:
        density = np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (
            sigma * math.sqrt(2.0 * math.pi)
        )
        ax.plot(
            x,
            density,
            linewidth=1.8,
            color=color,
            label=rf"$\mu$={mu}, $\sigma$={sigma}",
        )

    ax.set_xlim(-6, 6)
    ax.set_ylim(0, 0.45)
    ax.set_xlabel("x")
    ax.set_ylabel("density")
    ax.set_title("Нормальное распределение")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "normal_density_profiles.png", dpi=180)
    plt.close(fig)


def normal_pdf(x: np.ndarray, mu: float = 0.0, sigma: float = 1.0) -> np.ndarray:
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (
        sigma * math.sqrt(2.0 * math.pi)
    )


def mulberry32(seed: int):
    """Return the deterministic generator used by the book's OJS applets."""

    state = seed & 0xFFFFFFFF

    def random() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        value = state
        value = ((value ^ (value >> 15)) * (value | 1)) & 0xFFFFFFFF
        value ^= (
            value
            + (((value ^ (value >> 7)) * (value | 61)) & 0xFFFFFFFF)
        ) & 0xFFFFFFFF
        value &= 0xFFFFFFFF
        return ((value ^ (value >> 14)) & 0xFFFFFFFF) / 4294967296.0

    return random


def normal_sample_from_seed(seed: int, size: int) -> np.ndarray:
    """Generate standard normal values exactly as the OJS Box--Muller code."""

    random = mulberry32(seed)
    values = np.empty(size)
    for index in range(size):
        u1 = max(random(), 1e-12)
        u2 = random()
        values[index] = math.sqrt(-2.0 * math.log(u1)) * math.cos(
            2.0 * math.pi * u2
        )
    return values


def build_numpy_sampling_demos(out_dir: Path) -> None:
    rng = np.random.default_rng(20260423)
    sample_size = 20_000

    x = rng.uniform(-1.0, 1.0, sample_size)
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.hist(x, bins=50, density=True, color="#4ea1ff", alpha=0.72, edgecolor="white")
    ax.hlines(0.5, -1, 1, color="#ffb347", linewidth=2.4, label="плотность")
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(0, 0.7)
    ax.set_xlabel("x")
    ax.set_ylabel("density")
    ax.set_title("Равномерное распределение из выборки")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "numpy_uniform_sample.png", dpi=180)
    plt.close(fig)

    n, p = 20, 0.3
    k_sample = rng.binomial(n=n, p=p, size=sample_size)
    k = np.arange(0, n + 1)
    freq = np.bincount(k_sample, minlength=n + 1) / sample_size
    pmf = np.array(
        [math.comb(n, int(i)) * p**i * (1.0 - p) ** (n - i) for i in k],
        dtype=float,
    )
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.bar(k, freq, color="#4ea1ff", alpha=0.72, edgecolor="white", label="частоты")
    ax.plot(k, pmf, color="#ffb347", marker="o", linewidth=2.0, label="PMF")
    ax.set_xlim(-0.8, 20.8)
    ax.set_ylim(0, 0.22)
    ax.set_xlabel("k")
    ax.set_ylabel("P(k)")
    ax.set_title("Биномиальное распределение из выборки")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "numpy_binomial_sample.png", dpi=180)
    plt.close(fig)

    lam = 4.0
    k_sample = rng.poisson(lam=lam, size=sample_size)
    k = np.arange(0, 16)
    freq = np.bincount(k_sample, minlength=len(k))[: len(k)] / sample_size
    pmf = np.exp(-lam) * lam**k / np.array([math.factorial(int(i)) for i in k])
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.bar(k, freq, color="#4ea1ff", alpha=0.72, edgecolor="white", label="частоты")
    ax.plot(k, pmf, color="#ffb347", marker="o", linewidth=2.0, label="PMF")
    ax.set_xlim(-0.8, 15.8)
    ax.set_ylim(0, 0.23)
    ax.set_xlabel("k")
    ax.set_ylabel("P(k)")
    ax.set_title("Распределение Пуассона из выборки")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "numpy_poisson_sample.png", dpi=180)
    plt.close(fig)

    mu, sigma = 0.0, 1.0
    x = rng.normal(loc=mu, scale=sigma, size=sample_size)
    grid = np.linspace(-4.0, 4.0, 500)
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.hist(x, bins=70, density=True, color="#4ea1ff", alpha=0.72, edgecolor="white")
    ax.plot(grid, normal_pdf(grid, mu, sigma), color="#ffb347", linewidth=2.4, label="PDF")
    ax.set_xlim(-4, 4)
    ax.set_ylim(0, 0.46)
    ax.set_xlabel("x")
    ax.set_ylabel("density")
    ax.set_title("Нормальное распределение из выборки")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "numpy_normal_sample.png", dpi=180)
    plt.close(fig)


def build_clt_uniform_sums(out_dir: Path) -> None:
    rng = np.random.default_rng(20260424)
    sample_size = 80_000
    grid = np.linspace(-4.2, 4.2, 500)

    for m in [1, 2, 5, 10]:
        x = rng.uniform(-1.0, 1.0, size=(sample_size, m))
        z = x.sum(axis=1) / math.sqrt(m / 3.0)

        fig, ax = plt.subplots(figsize=(9.2, 5.2))
        ax.hist(
            z,
            bins=80,
            range=(-4.2, 4.2),
            density=True,
            color="#4ea1ff",
            alpha=0.72,
            edgecolor="white",
        )
        ax.plot(
            grid,
            normal_pdf(grid),
            color="#ffb347",
            linewidth=2.6,
            label=r"$\mathrm{N}(0,1)$",
        )
        ax.set_xlim(-4.2, 4.2)
        ax.set_ylim(0, 0.55)
        ax.set_xlabel(r"$z$")
        ax.set_ylabel("density")
        ax.set_title(rf"ЦПТ: сумма {m} равномерных случайных величин")
        ax.text(
            0.03,
            0.92,
            rf"$z=(X_1+\cdots+X_m)/\sqrt{{m/3}},\quad m={m}$",
            transform=ax.transAxes,
            fontsize=12,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.9},
        )
        ax.grid(axis="y", alpha=0.25)
        ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
        fig.tight_layout()
        fig.savefig(out_dir / f"clt_uniform_sum_m{m}.png", dpi=180)
        plt.close(fig)


def build_chapter05_fallbacks(out_dir: Path) -> None:
    """Build the static counterparts of the chapter 5 OJS applets."""

    rng = np.random.default_rng(20260904)
    sample_size = 60_000

    # Mean of Cauchy variables versus a normalized Gaussian sum.
    n_cauchy = 100
    cauchy_means = rng.standard_cauchy((sample_size, n_cauchy)).mean(axis=1)
    gaussian_sum = rng.normal(size=sample_size)
    grid = np.linspace(-10.0, 10.0, 600)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.hist(
        gaussian_sum,
        bins=100,
        range=(-10, 10),
        density=True,
        color="#9be564",
        alpha=0.40,
        label="нормированная сумма гауссовых величин",
    )
    ax.hist(
        cauchy_means,
        bins=100,
        range=(-10, 10),
        density=True,
        color="#4ea1ff",
        alpha=0.68,
        label="среднее величин Коши",
    )
    ax.plot(
        grid,
        1.0 / (math.pi * (1.0 + grid**2)),
        color="#ffb347",
        linewidth=2.6,
        label=r"$\mathrm{Cauchy}(0,1)$",
    )
    ax.set_xlim(-10, 10)
    ax.set_ylim(0, 0.38)
    ax.set_xlabel("Значение")
    ax.set_ylabel("Плотность")
    ax.text(
        0.03,
        0.92,
        rf"$n={n_cauchy}$",
        transform=ax.transAxes,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "cauchy_mean_n100.png", dpi=180)
    plt.close(fig)

    # Maximally right-skewed alpha-stable law used by the Landau-like applet.
    v = math.pi * (rng.random(sample_size) - 0.5)
    w = rng.exponential(size=sample_size)
    landau_values = (2.0 / math.pi) * (
        (math.pi / 2.0 + v) * np.tan(v)
        - np.log(
            (math.pi / 2.0 * w * np.cos(v))
            / (math.pi / 2.0 + v)
        )
    )
    median = float(np.median(landau_values))
    q16, q84 = np.quantile(landau_values, [0.16, 0.84])
    central_width = float((q84 - q16) / 2.0)
    grid = np.linspace(-8.0, 25.0, 600)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.hist(
        landau_values,
        bins=120,
        range=(-8, 25),
        density=True,
        color="#4ea1ff",
        alpha=0.70,
        edgecolor="white",
        label="ландау-подобное распределение",
    )
    ax.plot(
        grid,
        normal_pdf(grid, median, central_width),
        color="#ffb347",
        linewidth=2.6,
        label="гаусс с той же медианой и центральной шириной",
    )
    ax.set_xlim(-8, 25)
    ax.set_ylim(0, 0.42)
    ax.set_xlabel(r"Потеря энергии $\Delta$")
    ax.set_ylabel("Плотность")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "landau_like_default.png", dpi=180)
    plt.close(fig)

    # Mean with a Gaussian common-mode shift.
    n_corr = 100
    sigma_common = 0.6
    sigma_stat = 1.0
    corr_sigma = math.sqrt(sigma_common**2 + sigma_stat**2 / n_corr)
    corr_means = rng.normal(scale=sigma_common, size=sample_size) + rng.normal(
        scale=sigma_stat / math.sqrt(n_corr), size=sample_size
    )
    grid = np.linspace(-4.0, 4.0, 600)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.hist(
        corr_means,
        bins=90,
        range=(-4, 4),
        density=True,
        color="#4ea1ff",
        alpha=0.70,
        edgecolor="white",
        label="псевдоэксперименты",
    )
    ax.plot(
        grid,
        normal_pdf(grid, 0.0, corr_sigma),
        color="#ffb347",
        linewidth=2.6,
        label=r"гаусс с $\sigma^2=\sigma_C^2+\sigma_\varepsilon^2/n$",
    )
    ax.set_xlim(-4, 4)
    ax.set_xlabel(r"Среднее $\overline{X}_n$")
    ax.set_ylabel("Плотность")
    ax.text(
        0.03,
        0.92,
        rf"$n={n_corr},\ \sigma_C={sigma_common},\ \sigma_\varepsilon={sigma_stat}$",
        transform=ax.transAxes,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "correlated_error_sigma06.png", dpi=180)
    plt.close(fig)

    # Mixture of two Gaussian classes.
    weight = 0.5
    separation = 1.9
    sigma_1 = 1.0
    sigma_2 = 1.0
    mu_1 = -separation / 2.0
    mu_2 = separation / 2.0
    first_class = rng.random(sample_size) < weight
    mixture = np.where(
        first_class,
        rng.normal(mu_1, sigma_1, sample_size),
        rng.normal(mu_2, sigma_2, sample_size),
    )
    mixture_mean = weight * mu_1 + (1.0 - weight) * mu_2
    mixture_var = (
        weight * (sigma_1**2 + (mu_1 - mixture_mean) ** 2)
        + (1.0 - weight) * (sigma_2**2 + (mu_2 - mixture_mean) ** 2)
    )
    grid = np.linspace(-8.0, 8.0, 600)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.hist(
        mixture,
        bins=100,
        range=(-8, 8),
        density=True,
        color="#4ea1ff",
        alpha=0.70,
        edgecolor="white",
        label="смесь двух классов",
    )
    ax.plot(
        grid,
        normal_pdf(grid, mixture_mean, math.sqrt(mixture_var)),
        color="#ffb347",
        linewidth=2.6,
        label="гаусс с теми же средним и дисперсией",
    )
    ax.set_xlim(-8, 8)
    ax.set_ylim(0, 0.55)
    ax.set_xlabel("x")
    ax.set_ylabel("Плотность")
    ax.text(
        0.03,
        0.92,
        rf"$w={weight},\ \Delta\mu={separation},\ \sigma_2={sigma_2}$",
        transform=ax.transAxes,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "gaussian_mixture_sep1_9.png", dpi=180)
    plt.close(fig)

    # Ratio of two independent standard Gaussian variables.
    x = rng.normal(size=sample_size)
    y = rng.normal(size=sample_size)
    ratio = x / y
    grid = np.linspace(-20.0, 20.0, 600)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.hist(
        ratio,
        bins=120,
        range=(-20, 20),
        density=True,
        color="#4ea1ff",
        alpha=0.70,
        edgecolor="white",
        label=r"$R=X/Y$",
    )
    ax.plot(
        grid,
        1.0 / (math.pi * (1.0 + grid**2)),
        color="#ffb347",
        linewidth=2.6,
        label=r"$\mathrm{Cauchy}(0,1)$",
    )
    ax.set_xlim(-20, 20)
    ax.set_ylim(0, 0.35)
    ax.set_xlabel(r"Отношение $R$")
    ax.set_ylabel("Плотность")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "ratio_gaussians_cauchy.png", dpi=180)
    plt.close(fig)


def build_chapter06_fallbacks(out_dir: Path) -> None:
    """Build the static counterparts of the chapter 6 OJS applets."""

    def nonlinear_figure(sigma_x: float, coefficient: float, filename: str) -> None:
        seed = (
            20260905
            + round(sigma_x * 100) * 1009
            + round(coefficient * 100) * 9176
        ) & 0xFFFFFFFF
        x = 1.0 + sigma_x * normal_sample_from_seed(seed, 18_000)
        y = x + coefficient * x**2
        linear_mean = 1.0 + coefficient
        linear_sigma = abs(1.0 + 2.0 * coefficient) * sigma_x
        exact_mean = 1.0 + coefficient + coefficient * sigma_x**2
        exact_sigma = math.sqrt(
            (1.0 + 2.0 * coefficient) ** 2 * sigma_x**2
            + 2.0 * coefficient**2 * sigma_x**4
        )
        lo, hi = float(y.min()), float(y.max())
        grid = np.linspace(lo, hi, 600)

        fig, ax = plt.subplots(figsize=(9.2, 5.2))
        ax.hist(
            y,
            bins=80,
            range=(lo, hi),
            density=True,
            color="#4ea1ff",
            alpha=0.72,
            edgecolor="white",
            label="Монте-Карло",
        )
        ax.plot(
            grid,
            normal_pdf(grid, linear_mean, linear_sigma),
            color="#ffb347",
            linewidth=2.6,
            label="линейное приближение",
        )
        ax.set_xlabel(r"$Y=X+aX^2$")
        ax.set_ylabel("Плотность")
        ax.text(
            0.03,
            0.94,
            "\n".join(
                [
                    rf"$\sigma_X={sigma_x:.2f},\ a={coefficient:.2f}$",
                    rf"линейно: $\mu={linear_mean:.3f},\ \sigma={linear_sigma:.3f}$",
                    rf"точно: $\mu={exact_mean:.3f},\ \sigma={exact_sigma:.3f}$",
                ]
            ),
            transform=ax.transAxes,
            va="top",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.92},
        )
        ax.grid(alpha=0.25)
        ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)

    nonlinear_figure(0.35, 0.35, "error_propagation_nonlinear_default.png")
    nonlinear_figure(0.90, 0.90, "error_propagation_nonlinear_strong.png")

    # Ten measurements from the same generator and default state as the applet.
    mu, sigma, sample_size, seed = 0.8, 1.5, 10, 123
    x = mu + sigma * normal_sample_from_seed(seed, sample_size)
    xbar = float(x.mean())
    variance = float(x.var(ddof=1))
    sigma_hat = math.sqrt(variance)
    sigma_mean = sigma_hat / math.sqrt(sample_size)
    variance_mean = variance / sample_size
    sigma_sigma_hat = sigma_hat / math.sqrt(2.0 * (sample_size - 1))
    variance_sigma_hat = variance / (2.0 * (sample_size - 1))

    rows = [
        [
            str(index + 1),
            f"{value:.3f}",
            f"{value - xbar:.3f}",
            f"{(value - xbar) ** 2:.3f}",
        ]
        for index, value in enumerate(x)
    ]
    fig, ax = plt.subplots(figsize=(10.4, 6.2))
    ax.axis("off")
    table = ax.table(
        cellText=rows,
        colLabels=[r"$k$", r"$X_k$", r"$X_k-\overline{X}$", r"$(X_k-\overline{X})^2$"],
        cellLoc="right",
        colLoc="center",
        bbox=[0.01, 0.04, 0.60, 0.92],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.15)
    summary = "\n".join(
        [
            "Истинные параметры",
            rf"$\mu={mu:.3f},\ \sigma={sigma:.3f},\ N={sample_size}$",
            "",
            "Оценки по выборке",
            rf"$\overline{{X}}={xbar:.3f}$",
            rf"$\widehat{{\sigma^2}}={variance:.3f}$",
            rf"$\widehat\sigma={sigma_hat:.3f}$",
            "",
            "Неопределённость среднего",
            rf"$\widehat\sigma/\sqrt{{N}}={sigma_mean:.3f}$",
            rf"$\widehat{{\mathrm{{Var}}}}(\overline{{X}})={variance_mean:.3f}$",
            "",
            r"Неопределённость $\widehat\sigma$",
            rf"$\widehat\sigma/\sqrt{{2(N-1)}}={sigma_sigma_hat:.3f}$",
            rf"$\widehat{{\mathrm{{Var}}}}(\widehat\sigma)\simeq{variance_sigma_hat:.3f}$",
        ]
    )
    ax.text(
        0.66,
        0.92,
        summary,
        transform=ax.transAxes,
        va="top",
        fontsize=11,
        linespacing=1.35,
        bbox={"boxstyle": "round,pad=0.6", "facecolor": "white", "edgecolor": "#888888"},
    )
    fig.tight_layout()
    fig.savefig(out_dir / "error_propagation_sample10.png", dpi=180)
    plt.close(fig)

    def correlation_figure(rho: float, filename: str) -> None:
        grad_x, grad_y = 1.0, 1.0
        sigma_x, sigma_y = 1.0, 0.8
        terms = np.array(
            [
                grad_x**2 * sigma_x**2,
                grad_y**2 * sigma_y**2,
                2.0 * rho * grad_x * grad_y * sigma_x * sigma_y,
            ]
        )
        total = float(terms.sum())
        colors = ["#4ea1ff", "#ffb347", "#b388ff"]

        fig, ax = plt.subplots(figsize=(9.2, 4.8))
        ax.barh(["вклад X", "вклад Y", "корреляция"], terms, color=colors)
        ax.axvline(0.0, color="#777777", linewidth=1.0)
        ax.set_xlabel("Вклад в дисперсию")
        ax.text(
            0.02,
            0.95,
            rf"$\rho={rho:+.2f}$" + "\n" + rf"$\sigma_F^2={total:.3f},\ \sigma_F={math.sqrt(total):.3f}$",
            transform=ax.transAxes,
            va="top",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.92},
        )
        ax.grid(axis="x", alpha=0.25)
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)

    correlation_figure(0.8, "error_propagation_corr_positive.png")
    correlation_figure(-0.8, "error_propagation_corr_negative.png")


def build_chapter07_fallbacks(out_dir: Path) -> None:
    """Build the static counterparts of the chapter 7 OJS applets."""

    rho = 0.65
    sigma_x = 1.4
    sigma_y = 0.8
    seed = (
        20260906
        + 37 * round((rho + 1.0) * 1000)
        + 101 * round(sigma_x * 100)
        + 211 * round(sigma_y * 100)
    ) & 0xFFFFFFFF
    normals = normal_sample_from_seed(seed, 2400).reshape(1200, 2)
    residual_scale = math.sqrt(1.0 - rho**2)
    cloud_x = sigma_x * normals[:, 0]
    cloud_y = sigma_y * (
        rho * normals[:, 0] + residual_scale * normals[:, 1]
    )
    angle = np.linspace(0.0, 2.0 * math.pi, 241)
    radius = math.sqrt(2.30)
    contour_x = sigma_x * radius * np.cos(angle)
    contour_y = sigma_y * radius * (
        rho * np.cos(angle) + residual_scale * np.sin(angle)
    )
    extent_x = 3.5 * sigma_x
    extent_y = 3.5 * sigma_y

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    ax.scatter(
        cloud_x,
        cloud_y,
        s=10,
        color="#4ea1ff",
        alpha=0.34,
        edgecolors="none",
        label="выборка",
    )
    ax.plot(
        contour_x,
        contour_y,
        color="#ff8c42",
        linewidth=3.0,
        label=r"$D^2=2.30$",
    )
    ax.axhline(0.0, color="#777777", linewidth=0.9)
    ax.axvline(0.0, color="#777777", linewidth=0.9)
    ax.set_xlim(-extent_x, extent_x)
    ax.set_ylim(-extent_y, extent_y)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$X$")
    ax.set_ylabel(r"$Y$")
    ax.text(
        0.03,
        0.96,
        rf"$\rho={rho:.2f},\ \sigma_X={sigma_x:.2f},\ \sigma_Y={sigma_y:.2f}$"
        + "\n"
        + r"внутри линии $68.3\%$ распределения",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.92},
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "gaussian2d_correlation_ellipse.png", dpi=180)
    plt.close(fig)

    probability = 0.683
    rho = -0.55
    sigma_x = 1.5
    sigma_y = 0.8
    threshold = -2.0 * math.log(1.0 - probability)
    residual_scale = math.sqrt(1.0 - rho**2)

    def contour(level: float) -> tuple[np.ndarray, np.ndarray]:
        contour_radius = math.sqrt(level)
        x = sigma_x * contour_radius * np.cos(angle)
        y = sigma_y * contour_radius * (
            rho * np.cos(angle) + residual_scale * np.sin(angle)
        )
        return x, y

    unit_x, unit_y = contour(1.0)
    probability_x, probability_y = contour(threshold)
    scale = 1.25 * math.sqrt(max(threshold, 1.0))
    extent_x = scale * sigma_x
    extent_y = scale * sigma_y

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.plot(
        unit_x,
        unit_y,
        color="#4ea1ff",
        linewidth=2.8,
        linestyle="--",
        label=r"$D^2=1$, внутри $39.3\%$",
    )
    ax.plot(
        probability_x,
        probability_y,
        color="#ff8c42",
        linewidth=3.5,
        label=rf"$D^2={threshold:.2f}$, внутри $68.3\%$",
    )
    ax.axhline(0.0, color="#777777", linewidth=0.9)
    ax.axvline(0.0, color="#777777", linewidth=0.9)
    ax.set_xlim(-extent_x, extent_x)
    ax.set_ylim(-extent_y, extent_y)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$X$")
    ax.set_ylabel(r"$Y$")
    ax.text(
        0.03,
        0.96,
        rf"$\rho={rho:.2f}$",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.92},
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right", framealpha=1.0, edgecolor="black")
    fig.tight_layout()
    fig.savefig(out_dir / "gaussian2d_probability_contour.png", dpi=180)
    plt.close(fig)


def build_chapter08_fallbacks(out_dir: Path) -> None:
    """Build static counterparts of the chapter 8 Monte Carlo applets."""

    # Rejection sampling for f(x) = 6x(1-x).
    sample_size = 1200
    random = mulberry32((20260908 + 1009 * sample_size) & 0xFFFFFFFF)
    pairs = np.array([(random(), 1.5 * random()) for _ in range(sample_size)])
    x, y = pairs[:, 0], pairs[:, 1]
    accepted = y <= 6.0 * x * (1.0 - x)
    curve_x = np.linspace(0.0, 1.0, 401)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.scatter(
        x[~accepted], y[~accepted], s=12, color="#777777", alpha=0.28,
        label="отброшенные точки",
    )
    ax.scatter(
        x[accepted], y[accepted], s=14, color="#4ea1ff", alpha=0.64,
        label="принятые точки",
    )
    ax.plot(
        curve_x, 6.0 * curve_x * (1.0 - curve_x), color="#ffb347",
        linewidth=2.8, label=r"$f(x)=6x(1-x)$",
    )
    ax.set(xlim=(0, 1), ylim=(0, 1.55), xlabel=r"$x$", ylabel=r"$y$")
    ax.set_title(
        f"Метод отбора: принято {accepted.sum()} из {sample_size} "
        f"({100 * accepted.mean():.1f}%)"
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", framealpha=0.88)
    fig.tight_layout()
    fig.savefig(out_dir / "mc_rejection_sampling.png", dpi=180)
    plt.close(fig)

    # Estimating pi from the area of a quarter-circle.
    random = mulberry32((20260908 + 1009 * sample_size) & 0xFFFFFFFF)
    pairs = np.array([(random(), random()) for _ in range(sample_size)])
    x, y = pairs[:, 0], pairs[:, 1]
    inside = x**2 + y**2 <= 1.0
    pi_estimate = 4.0 * inside.mean()
    pi_error = 4.0 * math.sqrt(inside.mean() * (1.0 - inside.mean()) / sample_size)
    angle = np.linspace(0.0, math.pi / 2.0, 301)

    fig, ax = plt.subplots(figsize=(6.6, 6.6))
    ax.scatter(
        x[~inside], y[~inside], s=12, color="#ff6b6b", alpha=0.30,
        label="вне четверти круга",
    )
    ax.scatter(
        x[inside], y[inside], s=12, color="#4ea1ff", alpha=0.62,
        label="внутри четверти круга",
    )
    ax.plot(np.cos(angle), np.sin(angle), color="#ffb347", linewidth=2.8)
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel=r"$x$", ylabel=r"$y$")
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(
        rf"$\widehat{{\pi}}={pi_estimate:.5f}$, "
        rf"статистическая ошибка $\simeq {pi_error:.5f}$"
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="lower left", framealpha=0.88)
    fig.tight_layout()
    fig.savefig(out_dir / "mc_pi_estimate.png", dpi=180)
    plt.close(fig)

    def grid_card(points: int, dimension: int, filename: str) -> None:
        total = points**dimension
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        ax.axis("off")
        ax.text(0.5, 0.88, "Регулярная сетка", ha="center", fontsize=22)
        ax.text(
            0.5, 0.60,
            f"{points} точек по каждой координате\n"
            f"в {dimension}-мерном пространстве",
            ha="center", va="center", fontsize=21,
        )
        ax.text(
            0.5, 0.30, f"N = {total:,}".replace(",", " "),
            ha="center", va="center", fontsize=32, fontweight="bold",
        )
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)

    grid_card(5, 8, "mc_grid_m5_d8.png")
    grid_card(12, 8, "mc_grid_m12_d8.png")

    # Uniform and importance samples around the same small region.
    importance_size = 1500
    region_sigma = 0.06
    centre = np.array([0.68, 0.42])
    random = mulberry32(20260618)
    uniform = np.array([(random(), random()) for _ in range(importance_size)])
    uniform_inside = np.sum((uniform - centre) ** 2, axis=1) < region_sigma**2

    def region_plot(
        points: np.ndarray,
        mask: np.ndarray,
        title: str,
        filename: str,
        outside_label: str,
    ) -> None:
        fig, ax = plt.subplots(figsize=(6.6, 6.6))
        ax.scatter(
            points[~mask, 0], points[~mask, 1], s=11,
            color="#777777", alpha=0.28, label=outside_label,
        )
        ax.scatter(
            points[mask, 0], points[mask, 1], s=16,
            color="#2163ff", alpha=0.78, label="точки внутри области",
        )
        circle = plt.Circle(centre, region_sigma, fill=False, color="#2163ff", linewidth=2.4)
        ax.add_patch(circle)
        ax.set(xlim=(0, 1), ylim=(0, 1), xlabel=r"$x$", ylabel=r"$y$")
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title)
        ax.grid(alpha=0.25)
        ax.legend(loc="upper left", framealpha=0.88)
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)

    region_plot(
        uniform,
        uniform_inside,
        f"Равномерная генерация: попало {uniform_inside.sum()} из {importance_size}",
        "mc_rare_uniform.png",
        "точки вне важной области",
    )

    random = mulberry32(424242)
    normal_points: list[tuple[float, float]] = []
    for _ in range(importance_size):
        values = []
        for _coordinate in range(2):
            u1 = max(random(), 1e-12)
            u2 = random()
            values.append(
                math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            )
        point = centre + region_sigma * np.asarray(values)
        if np.all((0.0 <= point) & (point <= 1.0)):
            normal_points.append((float(point[0]), float(point[1])))
    importance = np.asarray(normal_points)
    importance_inside = np.sum((importance - centre) ** 2, axis=1) < region_sigma**2
    region_plot(
        importance,
        importance_inside,
        f"Выборка по важности: внутри области {importance_inside.sum()} точек",
        "mc_importance_sampling.png",
        "точки рядом с областью",
    )

    moderate_weights = np.array([1.0, 1.2, 0.8, 1.1, 0.9, 1.05])
    uneven_weights = np.array([0.15, 0.25, 0.12, 1.5, 0.08, 0.2])
    positions = np.arange(1, 7)
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    width = 0.38
    ax.bar(
        positions - width / 2, moderate_weights, width,
        color="#4ea1ff", label="умеренные веса",
    )
    ax.bar(
        positions + width / 2, uneven_weights, width,
        color="#ff8c42", label="редкие большие веса",
    )
    ax.set(xlabel="событие", ylabel="вес")
    ax.set_title("Выборка по важности: характер весов")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_dir / "mc_weights_good_bad.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.2))
    coarse = np.linspace(0.0, 1.0, 6)
    adapted_x = np.array([0.0, 0.18, 0.36, 0.52, 0.61, 0.67, 0.72, 0.77, 0.80, 1.0])
    adapted_y = np.array([0.0, 0.18, 0.31, 0.36, 0.40, 0.44, 0.48, 0.54, 0.72, 1.0])
    for ax, x_lines, y_lines, title in zip(
        axes,
        [coarse, adapted_x],
        [coarse, adapted_y],
        ["до адаптации", "после адаптации"],
    ):
        for value in x_lines:
            ax.axvline(value, color="#4ea1ff", linewidth=1.0)
        for value in y_lines:
            ax.axhline(value, color="#4ea1ff", linewidth=1.0)
        ax.add_patch(plt.Circle(centre, region_sigma * 1.7, fill=False, color="black", linewidth=2.4))
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Адаптация выборки VEGAS к важной области", fontsize=19)
    fig.tight_layout()
    fig.savefig(out_dir / "mc_vegas_adaptation.png", dpi=180)
    plt.close(fig)

    # Counting pseudoexperiments at the default applet settings.
    signal, background, toy_count = 5.0, 10.0, 6000
    seed = (
        20260908
        + 101 * round(2 * signal)
        + 1009 * round(2 * background)
        + 17 * toy_count
    ) & 0xFFFFFFFF
    random = mulberry32(seed)

    def poisson_draw(lam: float) -> int:
        limit = math.exp(-lam)
        product = 1.0
        count = 0
        while True:
            count += 1
            product *= random()
            if product <= limit:
                return count - 1

    estimates = np.array(
        [poisson_draw(signal + background) - background for _ in range(toy_count)]
    )
    values, counts = np.unique(estimates, return_counts=True)
    probabilities = counts / toy_count
    exact_counts = np.arange(0, int(signal + background + 8 * math.sqrt(signal + background)) + 1)
    exact_probabilities = np.empty(exact_counts.size)
    exact_probabilities[0] = math.exp(-(signal + background))
    for index in range(1, exact_counts.size):
        exact_probabilities[index] = (
            exact_probabilities[index - 1] * (signal + background) / index
        )

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.bar(values, probabilities, width=0.86, color="#4ea1ff", alpha=0.72, label="псевдоэксперименты")
    ax.plot(
        exact_counts - background, exact_probabilities, "o-",
        color="#ff8c42", linewidth=1.6, markersize=4.0,
        label="распределение Пуассона",
    )
    ax.axvline(signal, color="#216b73", linestyle="--", linewidth=2.0)
    ax.axvline(0.0, color="#777777", linestyle=":", linewidth=1.8)
    negative_fraction = np.mean(estimates < 0.0)
    ax.set(xlabel=r"оценка сигнала $\widehat s=N-b$", ylabel="вероятность")
    ax.set_title(
        f"{toy_count} псевдоэкспериментов; доля оценок "
        rf"$\widehat s<0$: {100 * negative_fraction:.1f}%"
    )
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_dir / "mc_counting_pseudoexperiments.png", dpi=180)
    plt.close(fig)


def build_chapter09_fallbacks(out_dir: Path) -> None:
    """Build static likelihood plots used when the OJS applet is unavailable."""

    epsilon = np.linspace(0.0, 1.0, 1001)
    for sample_size, registered, filename in (
        (20, 7, "mle_binomial_n20_k7.png"),
        (100, 35, "mle_binomial_n100_k35.png"),
    ):
        likelihood = (
            epsilon**registered
            * (1.0 - epsilon) ** (sample_size - registered)
        )
        relative_likelihood = likelihood / np.max(likelihood)
        estimate = registered / sample_size

        fig, ax = plt.subplots(figsize=(9.4, 5.2))
        ax.plot(
            epsilon,
            relative_likelihood,
            color="#4ea1ff",
            linewidth=3.2,
        )
        ax.axvline(estimate, color="#ff8c42", linewidth=2.6)
        ax.set(
            xlim=(0.0, 1.0),
            ylim=(0.0, 1.05),
            xlabel=r"эффективность $\varepsilon$",
            ylabel=r"$L(\varepsilon)/L(\widehat\varepsilon)$",
            title=(
                f"Биномиальное правдоподобие: "
                f"N={sample_size}, k={registered}"
            ),
        )
        ax.grid(alpha=0.25)
        ax.annotate(
            rf"$\widehat\varepsilon={estimate:.2f}$",
            xy=(estimate, 1.0),
            xytext=(estimate + 0.06, 0.88),
            arrowprops={"arrowstyle": "->", "color": "#ff8c42"},
        )
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)


def build_chapter10_fallbacks(out_dir: Path) -> None:
    """Use the chapter's OJS models, seeds and default parameters for print."""
    from scipy.optimize import brentq

    blue, orange, dark = "#4ea1ff", "#dc792f", "#1d3941"
    sample_size = 6
    sample = normal_sample_from_seed(
        20260910 + 1009 * sample_size, 6000 * sample_size
    ).reshape(6000, sample_size)
    ml = np.var(sample, axis=1)
    unbiased = ml * sample_size / (sample_size - 1)
    bins = np.linspace(0, max(3, math.ceil(float(unbiased.max()))), 81)
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    for values, color, label in (
        (ml, blue, "ММП: делитель N"),
        (unbiased, orange, "Несмещённая: делитель N−1"),
    ):
        ax.hist(values, bins=bins, density=True, color=color, alpha=0.45,
                label=f"{label}; MSE = {np.mean((values - 1)**2):.3f}")
    ax.axvline(1, color=dark, label="Истинная дисперсия")
    ax.set(xlabel="Оценка дисперсии", ylabel="Плотность", title="N = 6; 6000 псевдоэкспериментов")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_dir / "mle_variance_estimators_n6.png", dpi=180)
    plt.close(fig)

    random = mulberry32(20260910)
    lifetimes = np.array([-2 * math.log(max(1e-12, 1 - random())) for _ in range(200)])
    tau = np.linspace(0.4, 4.5, 800)

    def life_q(t, n, estimate):
        return 2 * n * (np.log(t / estimate) + estimate / t - 1)

    estimate = float(lifetimes[:20].mean())
    low = brentq(lambda t: life_q(t, 20, estimate) - 1, 1e-6, estimate)
    high = brentq(lambda t: life_q(t, 20, estimate) - 1, estimate, 10 * estimate)
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    ax.plot(tau, -life_q(tau, 20, estimate) / 2, color=blue, lw=2.5,
            label="Точное правдоподобие")
    ax.plot(tau, -10 * (tau - estimate)**2 / estimate**2, "--", color="#72808a",
            label="Квадратичное приближение")
    ax.axhline(-0.5, color=dark, ls=":", label="q = 1")
    ax.axvline(2, color=dark, ls="--", label=r"Истинное $\tau_0=2$ мкс")
    for bound in (low, high):
        ax.axvline(bound, color=orange, ls=":")
    ax.set(xlim=(0.4, 4.5), ylim=(-5, 0.15), xlabel=r"Время жизни $\tau$, мкс",
           ylabel=r"$\ell(\tau)-\ell_{\max}$", title=f"N = 20; оценка τ̂ = {estimate:.2f} мкс")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_dir / "mle_lifetime_n20.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    for n, color in ((20, blue), (200, orange)):
        estimate = float(lifetimes[:n].mean())
        ax.plot(tau, life_q(tau, n, estimate), color=color, lw=2.5,
                label=f"N = {n}; τ̂ = {estimate:.2f} мкс")
    ax.axhline(1, color=dark, ls=":", label="q = 1")
    ax.axvline(2, color=dark, ls="--", label=r"Истинное $\tau_0$")
    ax.set(xlim=(0.8, 3.5), ylim=(0, 9), xlabel=r"Время жизни $\tau$, мкс", ylabel=r"$q(\tau)$")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_dir / "mle_lifetime_n200.png", dpi=180)
    plt.close(fig)

    rho = 0.75
    theta = np.linspace(-3, 3, 241)
    xx, yy = np.meshgrid(theta, theta)
    joint = np.exp(-0.5 * (xx**2 - 2 * rho * xx * yy + yy**2) / (1 - rho**2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.7))
    axes[0].pcolormesh(xx, yy, joint, cmap="magma", shading="auto", vmin=0, vmax=1)
    axes[0].plot(theta, rho * theta, color="white", lw=2)
    axes[0].axvline(1.2, color=blue)
    axes[0].scatter([1.2], [rho * 1.2], color=orange, s=45)
    axes[0].set(xlabel=r"$\theta$", ylabel=r"$\eta$", title=r"$L/L_{\max}$; $\rho=0.75$")
    axes[1].plot(theta, theta**2, color=orange, label="Профиль", lw=2.5)
    axes[1].plot(theta, theta**2 / (1 - rho**2), color=blue, label=r"Сечение $\eta=0$", lw=2.5)
    axes[1].axhline(1, color=dark, ls=":")
    axes[1].set(xlabel=r"$\theta$", ylabel=r"$q(\theta)$", ylim=(0, 9))
    axes[1].legend()
    axes[1].grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_dir / "mle_profile_likelihood_rho075.png", dpi=180)
    plt.close(fig)

    # Huber (235U, 239Pu, 241Pu), Mueller (238U), as in the lecture.
    components = (
        (0.58, [4.367, -4.577, 2.100, -0.5294, 0.06186, -0.002777]),
        (0.07, [0.4833, 0.1927, -0.1283, -0.006762, 0.002233, -0.0001536]),
        (0.30, [4.757, -5.392, 2.563, -0.6596, 0.07820, -0.003536]),
        (0.05, [2.990, -2.882, 1.278, -0.3343, 0.03905, -0.001754]),
    )
    edges = np.linspace(1.8, 8, 19)
    energy = (edges[1:] + edges[:-1]) / 2
    flux = sum(fraction * np.exp(sum(a * energy**p for p, a in enumerate(coeffs)))
               for fraction, coeffs in components)
    ee = energy - 1.293
    weights = flux * ee * np.sqrt(np.maximum(0, ee**2 - 0.511**2)) * np.diff(edges)
    no_osc = 2500 * weights / weights.sum()

    def expected(amplitude, dm):
        return no_osc * (1 - amplitude * np.sin(1.267 * dm * 1e-3 * 1600 / energy)**2)

    random = mulberry32(20260910 + 17 * 18 + 2500 + 101 * 85 + 1009 * 250)

    def poisson(lam):
        parts = max(1, math.ceil(lam / 30))
        limit = math.exp(-lam / parts)
        total = 0
        for _ in range(parts):
            count, product = 0, 1.0
            while True:
                count += 1
                product *= random()
                if product <= limit:
                    break
            total += count - 1
        return total

    true_mu = expected(0.085, 2.5)
    counts = np.array([poisson(lam) for lam in true_mu])
    amplitudes, dm_values = np.linspace(0, 0.2, 61), np.linspace(1.6, 3.4, 61)
    loglike = np.array([[np.sum(counts * np.log(expected(a, dm)) - expected(a, dm))
                         for dm in dm_values] for a in amplitudes])
    q = -2 * (loglike - loglike.max())
    ai, di = np.unravel_index(np.argmax(loglike), loglike.shape)
    best_a, best_dm = amplitudes[ai], dm_values[di]
    fig = plt.figure(figsize=(10.5, 8))
    grid = fig.add_gridspec(3, 2, width_ratios=(1, 1.05))
    ax_map = fig.add_subplot(grid[:, 0])
    ax_spectrum = fig.add_subplot(grid[0, 1])
    ax_a = fig.add_subplot(grid[1, 1])
    ax_dm = fig.add_subplot(grid[2, 1])
    ax_map.pcolormesh(dm_values, amplitudes, np.exp(-q / 2), cmap="magma", shading="auto", vmin=0, vmax=1)
    ax_map.contour(dm_values, amplitudes, q, levels=[2.30, 6.18], colors="white", linewidths=[1.5, 0.8])
    ax_map.scatter([2.5], [0.085], color="#00a86b", edgecolor="black", label="Генерация", s=55)
    ax_map.scatter([best_dm], [best_a], color=orange, edgecolor="black", label="Максимум", s=55)
    ax_map.set(xlabel=r"$\Delta m^2$, $10^{-3}$ эВ$^2$", ylabel=r"$A=\sin^2(2\theta)$", title=r"$L/L_{\max}$; уровни $q=2.30,\ 6.18$")
    ax_map.legend(loc="upper left", fontsize=9)
    ax_spectrum.stairs(counts, edges, fill=True, color="#d9d9d9")
    ax_spectrum.plot(energy, no_osc, "--", color=blue, label="Без осцилляций")
    ax_spectrum.plot(energy, true_mu, "--", color="#00a86b")
    ax_spectrum.plot(energy, expected(best_a, best_dm), color=orange)
    ax_spectrum.set(xlabel="Энергия, МэВ", ylabel="События в бине")
    ax_spectrum.legend(fontsize=8)
    ax_a.plot(amplitudes, q.min(axis=1), color=orange)
    ax_dm.plot(dm_values, q.min(axis=0), color=blue)
    for ax, truth in ((ax_a, 0.085), (ax_dm, 2.5)):
        ax.axhline(1, color=dark, ls=":")
        ax.axvline(truth, color="#00a86b", ls="--")
        ax.set_ylim(0, 9)
        ax.grid(alpha=0.2)
    ax_a.set(xlabel=r"$A$", ylabel=r"$q_{\mathrm{p}}(A)$")
    ax_dm.set(xlabel=r"$\Delta m^2$, $10^{-3}$ эВ$^2$", ylabel=r"$q_{\mathrm{p}}(\Delta m^2)$")
    fig.suptitle(f"N₀ = 2500; N = {counts.sum()}; 18 бинов; Â = {best_a:.3f}; Δm̂² = {best_dm:.2f}·10⁻³ эВ²", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_dir / "mle_reactor_oscillation_default.png", dpi=180)
    plt.close(fig)


def weighted_line_fit(x: np.ndarray, y: np.ndarray, sigma: np.ndarray):
    """Fit a line with known independent errors, using centered coordinates."""
    w = 1.0 / sigma**2
    s = w.sum()
    xbar, ybar = np.dot(w, x) / s, np.dot(w, y) / s
    qx = np.dot(w, (x - xbar)**2)
    b = np.dot(w * (x - xbar), y - ybar) / qx
    a = ybar - b * xbar
    covariance = np.array([[1 / s + xbar**2 / qx, -xbar / qx],
                           [-xbar / qx, 1 / qx]])
    return a, b, covariance, xbar, qx


def build_chapter11_fallbacks(out_dir: Path) -> None:
    """Chapter 11: the same data and geometry as the book's OJS applets."""
    blue, orange, ink = "#367ab5", "#d88a24", "#263640"

    # The calibration table is a specified educational data set, not a sample
    # from an experiment. Errors refer to fitted peak centers in ADC channels.
    x = np.array([1., 2., 3.])
    y = np.array([103., 200., 303.])
    sigma = np.full(3, 2.)
    a, b, covariance, xbar, qx = weighted_line_fit(x, y, sigma)
    grid = np.linspace(0., 4., 301)
    mean_error = np.sqrt(1 / np.sum(1 / sigma**2) + (grid - xbar)**2 / qx)
    prediction_error = np.sqrt(4 + mean_error**2)
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 7.0), sharex=True)
    axes[0].errorbar(x, y, yerr=sigma, fmt="o", color=ink, capsize=4,
                     label="центры калибровочных пиков")
    axes[0].plot(grid, a + b * grid, color=orange, label="подогнанная прямая")
    axes[0].set_ylabel("Амплитуда, канал")
    axes[1].fill_between(grid, -prediction_error, prediction_error,
                         color=blue, alpha=.18, label="новое измерение: ±1σ")
    axes[1].fill_between(grid, -mean_error, mean_error, color=blue, alpha=.45,
                         label="средний сигнал: ±1σ")
    axes[1].axhline(0, color=orange)
    axes[1].errorbar(x, y - a - b * x, yerr=sigma, fmt="o", color=ink, capsize=4)
    axes[1].set_ylabel("Отклонение от прямой, канал")
    axes[1].set_xlabel("Энергия x, МэВ")
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "lsq_calibration_bands.png", dpi=180)
    plt.close(fig)

    # Normalize the eight coordinates to zero mean and unit RMS. Project the
    # residual pattern off both fitted directions, so a=1, b=.55 really is
    # the best fit and the plotted points have exactly the stated S and Qx.
    center, spread, s = 1.8, 1., 18.
    offsets = np.array([-1.55, -1.05, -.55, -.12, .35, .82, 1.28, 1.62])
    offsets -= offsets.mean()
    offsets /= np.sqrt(np.mean(offsets**2))
    residual = np.array([.09, -.04, .06, -.08, .02, .07, -.05, -.07])
    residual = residual - residual.mean() - np.mean(residual * offsets) * offsets
    x = center + spread * offsets
    y = 1 + .55 * x + residual
    sigma = np.full(8, np.sqrt(8 / s))
    a, b, covariance, actual_center, qx = weighted_line_fit(x, y, sigma)
    assert np.allclose([a, b, actual_center, qx], [1, .55, center, s * spread**2])
    grid = np.linspace(min(0, x.min()) - .5, max(0, x.max()) + .5, 121)
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 7.0))
    for k in [-1, 0, 1]:
        slope = b + k * np.sqrt(covariance[1, 1])
        intercept = 1 + .55 * center - slope * center
        axes[0].plot(grid, intercept + slope * grid, color=orange if k == 0 else blue,
                     linestyle="-" if k == 0 else "--",
                     label="лучшая прямая" if k == 0 else ("наклоны b̂ ± σ_b" if k == -1 else None))
    axes[0].errorbar(x, y, yerr=sigma, fmt="o", color=blue, capsize=3)
    axes[0].axvline(center, color=orange, alpha=.6)
    axes[0].axvline(0, color="gray", linestyle="--", alpha=.5)
    axes[0].plot(center, 1 + .55 * center, "o", color=orange, markeredgecolor=ink)
    axes[0].set(xlabel="x", ylabel="y")
    phase = np.linspace(0, 2 * np.pi, 241)
    ellipse = np.sqrt(2.30) * np.linalg.cholesky(covariance) @ np.array([np.cos(phase), np.sin(phase)])
    axes[1].plot(*ellipse, color=orange, label="Δχ² = 2.30")
    db_max = max(.42, 1.18 * np.max(np.abs(ellipse[1])))
    db = np.array([-db_max, db_max])
    axes[1].plot(-center * db, db, "--", color=blue, label="профиль: δa = −x̄_w δb")
    da_max = max(.55, 1.18 * np.max(np.abs(ellipse[0])))
    axes[1].set(xlabel="δa", ylabel="δb", xlim=(-da_max, da_max), ylim=(-db_max, db_max))
    axes[1].plot(0, 0, "o", color=ink)
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "lsq_parameter_geometry.png", dpi=180)
    plt.close(fig)

    # Default initial state and Box-Muller transform match least-squares-outlier.ojs.
    x = np.linspace(-4.5, 4.5, 16)
    sigma = .55 * (.72 + .56 * (np.arange(16) % 4) / 3)
    noise = normal_sample_from_seed(20260911, 16)
    base_y = 1 + .8 * x + sigma * noise
    grid = np.linspace(-5., 5., 201)
    for shift, filename in [(0., "lsq_fit_no_outlier.png"), (4., "lsq_fit_with_outlier.png")]:
        y = base_y.copy()
        y[12] += shift
        a, b, covariance, _, _ = weighted_line_fit(x, y, sigma)
        residual = (y - a - b * x) / sigma
        fig, axes = plt.subplots(2, 1, figsize=(7.4, 7.0), sharex=True)
        axes[0].errorbar(x, y, yerr=sigma, fmt="o", color=blue, capsize=3)
        axes[0].plot(x[12], y[12], "s", color="#c44536", label="изменяемая точка")
        axes[0].plot(grid, 1 + .8 * grid, "--", color="gray", label="истинная прямая")
        axes[0].plot(grid, a + b * grid, color=orange, label="подгонка")
        axes[0].set_ylabel("y")
        axes[0].legend(fontsize=10)
        axes[0].set_title(f"â = {a:.3f} ± {np.sqrt(covariance[0, 0]):.3f}; "
                          f"b̂ = {b:.3f} ± {np.sqrt(covariance[1, 1]):.3f}")
        axes[1].axhline(0, color=ink)
        for level in [-2, 2]:
            axes[1].axhline(level, color="gray", linestyle="--")
        axes[1].plot(x, residual, "o", color=blue)
        axes[1].plot(x[12], residual[12], "s", color="#c44536")
        limit = max(3, 1.15 * np.max(np.abs(residual)))
        axes[1].set(xlabel="x", ylabel="u = остаток / σᵢ", ylim=(-limit, limit))
        axes[1].set_title(f"χ²_min = {np.sum(residual**2):.1f}; N − 2 = 14; d = {shift:g}")
        for ax in axes:
            ax.grid(alpha=.2)
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)


def normalization_example(fraction: float = .1):
    """Chapter 12: fixed absolute errors, one common Gaussian calibration."""
    y, s = np.array([8., 8.5]), np.array([.16, .17])
    w = 1 / s**2
    m, v = np.dot(w, y) / w.sum(), 1 / w.sum()
    q0 = np.sum(w * (y - m)**2)
    empirical = np.diag(s**2) + fraction**2 * np.outer(y, y)
    u = np.linalg.solve(empirical, np.ones(2))
    weights = u / u.sum()
    radical = np.sqrt(fraction**2 * m**2 + (1 - fraction**2) * v)
    return dict(y=y, s=s, m=m, v=v, q0=q0, bad=weights @ y,
                weights=weights, bad_variance=1 / u.sum(),
                error=np.sqrt(v + fraction**2 * m**2),
                low=(m - radical) / (1 - fraction**2),
                high=(m + radical) / (1 - fraction**2))


def build_chapter12_fallbacks(out_dir: Path) -> None:
    """Reproducible contours and default states of the two chapter 12 applets."""
    blue, red, ink = "#367ab5", "#c44536", "#263640"
    delta = np.linspace(-2.5, 2.5, 401)
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(delta, delta**2, color=blue, label=r"$\Delta\chi^2=(\theta-\hat\theta)^2$")
    ax.axhline(1, color=red, linestyle="--", label="Уровень c = 1")
    ax.vlines([-1, 1], 0, 1, colors=red, linestyles="--")
    ax.plot([-1, 1], [1, 1], "o", color=red)
    ax.plot(0, 0, "o", color=ink)
    ax.set(xlabel=r"$\theta-\hat\theta$", ylabel=r"$\Delta\chi^2$",
           xlim=(-2.5, 2.5), ylim=(0, 5))
    ax.grid(alpha=.2)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "lsq_delta_chi2_one_sigma.png", dpi=180)
    plt.close(fig)

    phase = np.linspace(0, 2 * np.pi, 501)
    covariance = np.array([[1., .7], [.7, 1.]])
    unit = np.linalg.cholesky(covariance) @ np.array([np.cos(phase), np.sin(phase)])
    fig, ax = plt.subplots(figsize=(6.4, 4.5))
    for level, style in [(1., "-"), (2.30, "--")]:
        ellipse = np.sqrt(level) * unit
        ax.plot(*ellipse, style, color=blue if level == 1 else red,
                label=f"Δχ² = {level:g}")
    ax.plot(0, 0, "o", color=ink)
    ax.set(xlabel=r"$\theta_1-\hat\theta_1$", ylabel=r"$\theta_2-\hat\theta_2$",
           xlim=(-1.8, 1.8), ylim=(-1.8, 1.8))
    ax.set_aspect("equal")
    ax.grid(alpha=.2)
    ax.legend(fontsize=11)
    fig.tight_layout()
    fig.savefig(out_dir / "lsq_quadratic_chi2_surface.png", dpi=180)
    plt.close(fig)

    # Four noiseless mean values illustrate the exact alias omega -> omega+2pi
    # at integer times. These are educational data, not an experimental fit.
    times = np.arange(1, 5)
    observations = .6 * np.sin(1.2 * times)
    omega = np.linspace(.3, 8., 1601)
    amplitudes = np.linspace(0., 1.05, 501)
    omega_grid, amplitude_grid = np.meshgrid(omega, amplitudes)
    q = sum(((observations[i] - amplitude_grid * np.sin(omega_grid * t)) / .15)**2
            for i, t in enumerate(times))
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    contour = ax.contour(omega_grid, amplitude_grid, q, levels=[1., 2.30, 6.18],
                        colors=[blue, red, "#9b7327"], linestyles=["-", "--", ":"],
                        linewidths=1.8)
    ax.clabel(contour, inline=True, fontsize=10, fmt="%g")
    ax.plot([1.2, 1.2 + 2 * np.pi], [.6, .6], "o", color=ink, markersize=4)
    ax.set(xlabel=r"Частота $\omega$", ylabel=r"Амплитуда $A$",
           xlim=(.3, 8.), ylim=(0, 1.05), title="Уровни Δχ²; s = 0.15")
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(out_dir / "lsq_oscillatory_chi2_surface.png", dpi=180)
    plt.close(fig)

    f = .1
    result = normalization_example(f)
    mu = np.linspace(3.5, 13.5, 701)
    profile = (mu - result["m"])**2 / (result["v"] + f**2 * mu**2)
    bad = (mu - result["bad"])**2 / result["bad_variance"]
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 6.1),
                             gridspec_kw={"height_ratios": [1, 1.5]})
    ax = axes[0]
    ax.axhline(2, color="gray", linestyle="--", alpha=.5)
    ax.plot(result["y"], [2, 2], "o", color=ink)
    for x, label, offset, alignment in zip(
            result["y"], ["y₁ = 8.00 пб", "y₂ = 8.50 пб"],
            [-4, 4], ["right", "left"]):
        ax.annotate(label, (x, 2), xytext=(offset, 10),
                    textcoords="offset points", ha=alignment, fontsize=10)
    for value, row, label, color, marker in [
        (result["bad"], 0, "Ковариация из данных", red, "s"),
        (result["m"], 1, "Модель общей нормировки", blue, "D")]:
        ax.plot(value, row, marker, color=color)
        ax.text(7.4, row - .32, label, ha="center", fontsize=10)
    ax.set(xlim=(5.5, 9.3), ylim=(-.65, 2.6), yticks=[], xlabel="Сечение μ, пб")
    ax.grid(axis="x", alpha=.2)
    ax = axes[1]
    ax.plot(mu, profile, color=blue, label="Профиль модели")
    ax.plot(mu, bad, "--", color=red, label="Ковариация из данных")
    ax.axhline(1, color="gray", linestyle=":", alpha=.7)
    ax.plot([result["low"], result["high"]], [1, 1], "o", color=blue, markersize=4)
    ax.set(xlim=(3.5, 13.5), ylim=(0, 5), xlabel="Сечение μ, пб", ylabel="Δχ²")
    ax.grid(alpha=.2)
    ax.legend(fontsize=10)
    fig.suptitle(f"f_N = 10%; μ̂ = {result['m']:.3f} пб; "
                 f"μ̂_data = {result['bad']:.3f} пб", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_dir / "lsq_dagostini_comparison.png", dpi=180)
    plt.close(fig)



def goodness_random(seed: int):
    """LCG shared with the chapter 13 OJS examples."""
    state = seed

    def draw():
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 4294967296

    return draw


def goodness_uniform_values(count: int = 5000):
    """Independent calibration/test samples; finite-sample rank p-values."""
    random = goodness_random(246813579)

    def sample(size):
        result = np.empty(size)
        for index in range(size):
            total = 0.
            for _ in range(10):
                g = math.sqrt(-2 * math.log(max(random(), 1e-12))) * math.cos(2 * math.pi * random())
                total += g * g
            result[index] = total
        return result

    calibration = np.sort(sample(20000))
    observed = sample(count)
    right = calibration.size - np.searchsorted(calibration, observed, side="left")
    return (right + 1) / (calibration.size + 1)


GOODNESS_POISSON_MEANS = np.array([
    .158, .295, .513, .833, 1.263, 1.785, 2.355, 2.899, 3.330, 3.568,
    3.568, 3.330, 2.899, 2.355, 1.785, 1.263, .833, .513, .295, .158,
])


def goodness_poisson_sample(count: int = 80000):
    """The same Poisson draws and ordering as goodness-low-count-calibration.ojs."""
    random = goodness_random(123456789)
    means = GOODNESS_POISSON_MEANS
    limits = np.exp(-means)
    result = np.empty(count)
    for index in range(count):
        total = 0.
        for mu, limit in zip(means, limits):
            product, k = 1., 0
            while True:
                k += 1
                product *= random()
                if product <= limit:
                    break
            total += (k - 1 - mu)**2 / mu
        result[index] = total
    return result


def goodness_poisson_reference(count: int = 1000000):
    """Independent NumPy check quoted in chapter 13, seed 12345, T_obs = 29.8."""
    rng = np.random.default_rng(12345)
    exceedances, total, total2 = 0, 0., 0.
    for start in range(0, count, 10000):
        n = rng.poisson(GOODNESS_POISSON_MEANS, size=(min(10000, count - start), 20))
        values = ((n - GOODNESS_POISSON_MEANS)**2 / GOODNESS_POISSON_MEANS).sum(axis=1)
        exceedances += np.count_nonzero(values >= 29.8)
        total += values.sum()
        total2 += np.dot(values, values)
    return dict(p=exceedances / count, mean=total / count,
                variance=total2 / count - (total / count)**2)


def build_chapter13_fallbacks(out_dir: Path) -> None:
    """Default states of the six chapter 13 applets, with full-tail probabilities."""
    from scipy.stats import chi2, norm

    blue, red, gray = "#367ab5", "#c44536", "#536773"

    def finish(fig, ax, filename):
        ax.grid(alpha=.2)
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)

    nu = 10
    sigma = math.sqrt(2 * nu)
    t = np.linspace(0, nu + 5 * sigma, 1000)
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.fill_between(t, chi2.pdf(t, nu), color=blue, alpha=.14)
    ax.plot(t, chi2.pdf(t, nu), color=blue)
    ax.axvline(nu, color=red, label="среднее")
    for sign in [-1, 1]:
        ax.axvline(nu + sign * sigma, color=gray, linestyle="--",
                   label="среднее ± стандартное отклонение" if sign == -1 else None)
    ax.set(xlabel="t", ylabel="f(t; ν)", xlim=(0, t[-1]),
           ylim=(0, 1.12 * chi2.pdf(nu - 2, nu)), title="ν = 10")
    ax.legend(fontsize=9)
    finish(fig, ax, "gof_chi2_nu10.png")

    nu, observed = 50, 70
    xmax = nu + 6 * math.sqrt(2 * nu)
    t = np.linspace(0, xmax, 1200)
    tail = np.linspace(observed, xmax, 600)
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.plot(t, chi2.pdf(t, nu), color=blue)
    ax.fill_between(tail, chi2.pdf(tail, nu), color=red, alpha=.35)
    ax.axvline(observed, color=red)
    ax.set(xlabel="t", ylabel="f(t; ν)", xlim=(0, xmax),
           ylim=(0, 1.12 * chi2.pdf(nu - 2, nu)),
           title=f"ν = {nu}; t_obs = {observed}; p = {chi2.sf(observed, nu):.5f}")
    finish(fig, ax, "gof_pvalue_nu50_obs70.png")

    pvalues = goodness_uniform_values()
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.hist(pvalues, bins=np.linspace(0, 1, 21), density=True, color=blue, alpha=.6)
    ax.axhline(1, color=red, linestyle="--")
    ax.set(xlabel="p", ylabel="плотность", xlim=(0, 1), ylim=(0, 1.45),
           title=f"20 000 калибровочных и 5000 проверяемых опытов; доля p ≤ 0.05: {np.mean(pvalues <= .05):.4f}")
    finish(fig, ax, "gof_p_uniform.png")

    g = np.linspace(-4.5, 4.5, 1201)
    z = 2
    for two in [False, True]:
        fig, ax = plt.subplots(figsize=(7.6, 3.4))
        ax.plot(g, norm.pdf(g), color=blue)
        tail = np.linspace(z, 4.5, 400)
        ax.fill_between(tail, norm.pdf(tail), color=red, alpha=.4)
        ax.axvline(z, color=red)
        if two:
            ax.fill_between(-tail, norm.pdf(tail), color=red, alpha=.4)
            ax.axvline(-z, color=red)
        p = (2 if two else 1) * norm.sf(z)
        ax.set(xlabel="g", ylabel="φ(g)", xlim=(-4.5, 4.5), ylim=(0, .43),
               title=f"Z = 2; {'два хвоста' if two else 'один хвост'}; p = {p:.5f}")
        filename = "gof_p_to_z_two_sided.png" if two else "gof_p_to_z_one_sided.png"
        finish(fig, ax, filename)

    values = goodness_poisson_sample()
    p = np.mean(values >= 29.8)
    error = math.sqrt(p * (1 - p) / len(values))
    counts, edges = np.histogram(values, bins=np.arange(61))
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.bar(edges[:-1], counts / len(values), width=1, align="edge",
           color="#8d9ea8", alpha=.62, label="псевдоэксперименты")
    t = np.linspace(0, 60, 1201)
    ax.plot(t, chi2.pdf(t, 20), "--", color=blue, label="χ²₂₀")
    ax.axvline(29.8, color=red)
    ax.set(xlabel="T", ylabel="плотность", xlim=(0, 60), ylim=(0, .1),
           title=f"p из опытов = {p:.5f} ± {error:.5f}; p по χ²₂₀ = {chi2.sf(29.8,20):.5f}")
    ax.legend(fontsize=9)
    finish(fig, ax, "gof_low_count_toys.png")
    print("Chapter 13, independent Poisson check:", goodness_poisson_reference())


def main() -> None:
    root = project_root()
    out_dir = ensure_dir(root / "shared" / "figures" / "generated")
    build_normal_density(out_dir)
    build_poisson_pmf(out_dir)
    build_poisson_pmf_profiles(out_dir)
    build_binomial_pmf_profiles(out_dir)
    build_normal_density_profiles(out_dir)
    build_numpy_sampling_demos(out_dir)
    build_clt_uniform_sums(out_dir)
    build_chapter05_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter06_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter07_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter08_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter09_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter10_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter11_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter12_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))
    build_chapter13_fallbacks(ensure_dir(root / "ru" / "book" / "assets" / "figures"))


if __name__ == "__main__":
    main()
