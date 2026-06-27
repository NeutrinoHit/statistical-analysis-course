from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import LightSource


OUT = Path(__file__).resolve().parent / "static"


def setup_dark_3d(ax):
    ax.set_facecolor("#050505")
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((0.03, 0.03, 0.03, 1.0))
        axis._axinfo["grid"]["color"] = (0.35, 0.35, 0.35, 0.35)
        axis._axinfo["grid"]["linewidth"] = 0.8
    ax.tick_params(colors="#f2f2f2", labelsize=9)
    ax.xaxis.label.set_color("#f2f2f2")
    ax.yaxis.label.set_color("#f2f2f2")
    ax.zaxis.label.set_color("#f2f2f2")
    ax.title.set_color("#f2f2f2")


def make_quadratic_surface():
    rho = 0.45
    sx = 1.35
    sy = 1.05
    level = 5.99
    zmax = 9.0

    l11 = sx
    l21 = rho * sy
    l22 = sy * np.sqrt(1 - rho**2)

    radius = np.linspace(0, np.sqrt(zmax), 82)
    phi = np.linspace(0, 2 * np.pi, 181)
    R, Phi = np.meshgrid(radius, phi)
    Z = R**2
    X = l11 * R * np.cos(Phi)
    Y = l21 * R * np.cos(Phi) + l22 * R * np.sin(Phi)

    t = np.linspace(0, 2 * np.pi, 361)
    z1 = np.sqrt(level) * np.cos(t)
    z2 = np.sqrt(level) * np.sin(t)
    ex = l11 * z1
    ey = l21 * z1 + l22 * z2

    fig = plt.figure(figsize=(13.5, 7.2), dpi=180, facecolor="#050505")
    ax = fig.add_subplot(111, projection="3d")
    setup_dark_3d(ax)
    ax.set_proj_type("ortho")

    ls = LightSource(azdeg=310, altdeg=45)
    facecols = ls.shade(Z, cmap=cm.magma, vert_exag=0.18, blend_mode="soft")
    facecols[..., -1] = 0.34
    ax.plot_surface(
        X,
        Y,
        Z,
        rstride=2,
        cstride=2,
        facecolors=facecols,
        linewidth=0.35,
        edgecolor=(1.0, 0.70, 0.55, 0.26),
        alpha=0.34,
        antialiased=True,
    )
    ax.plot_wireframe(
        X,
        Y,
        Z,
        rstride=8,
        cstride=8,
        color=(1.0, 0.65, 0.55, 0.35),
        linewidth=0.55,
    )

    plane_x = np.array([[-3.5, 3.5], [-3.5, 3.5]])
    plane_y = np.array([[-3.1, -3.1], [3.1, 3.1]])
    plane_z = np.full_like(plane_x, level)
    ax.plot_surface(
        plane_x,
        plane_y,
        plane_z,
        color="#7890ff",
        alpha=0.18,
        linewidth=0,
        shade=False,
    )

    ax.plot(ex, ey, np.full_like(ex, level), color="#ff5a5f", lw=3.0)
    ax.plot(ex, ey, np.zeros_like(ex), color="#74ff74", lw=3.2)
    ax.plot([0], [0], [0], "o", color="white", markeredgecolor="#111111", markersize=6)

    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-3.2, 3.2)
    ax.set_zlim(0.0, zmax)
    ax.set_box_aspect((1.35, 1.0, 0.48))
    ax.set_box_aspect((1.35, 1.0, 0.55))
    ax.set_xlabel(r"$\theta_1-\hat\theta_1$", labelpad=10)
    ax.set_ylabel(r"$\theta_2-\hat\theta_2$", labelpad=10)
    ax.set_zlabel(r"$\Delta\chi^2$", labelpad=8)
    ax.view_init(elev=27, azim=-58)
    ax.set_title(
        r"Квадратичная форма: сечение $\Delta\chi^2=5.99$ даёт эллипс",
        pad=14,
        fontsize=15,
        fontweight="bold",
    )

    fig.text(
        0.52,
        0.045,
        "красная линия — пересечение поверхности с плоскостью; зелёная — проекция на плоскость параметров",
        ha="center",
        va="center",
        color="#f2f2f2",
        fontsize=13,
    )
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.10, top=0.92)
    fig.savefig(OUT / "lsq_quadratic_chi2_surface.png", facecolor=fig.get_facecolor())
    plt.close(fig)


def make_oscillatory_surface():
    times = np.array([0.92, 1.28, 1.84])
    a0 = 0.54
    w0 = 2.45
    sigma = 0.20
    y0 = 1 - a0 * np.sin(w0 * times) ** 2

    a = np.linspace(0.0, 1.0, 150)
    w = np.linspace(0.35, 8.55, 260)
    W, A = np.meshgrid(w, a)
    pred = 1 - A[..., None] * np.sin(W[..., None] * times) ** 2
    chi2 = np.sum(((pred - y0) / sigma) ** 2, axis=-1)
    dchi2 = chi2 - chi2.min()
    zmax = 11.0
    dchi2_plot = np.where(dchi2 <= zmax, dchi2, np.nan)

    best = np.unravel_index(np.argmin(dchi2), dchi2.shape)
    best_a = A[best]
    best_w = W[best]

    fig = plt.figure(figsize=(14.0, 7.2), dpi=180, facecolor="#050505")
    ax3 = fig.add_subplot(111, projection="3d")
    ax3.set_position([-0.03, 0.06, 1.06, 0.92])
    setup_dark_3d(ax3)
    ax3.set_proj_type("ortho")
    facecols = cm.magma(np.clip(np.nan_to_num(dchi2_plot, nan=zmax) / zmax, 0, 1))
    facecols[..., -1] = 0.56
    surf = ax3.plot_surface(
        W,
        A,
        dchi2_plot,
        rstride=3,
        cstride=3,
        facecolors=facecols,
        linewidth=0.15,
        edgecolor=(1.0, 0.75, 0.55, 0.30),
        alpha=0.56,
        antialiased=True,
    )
    ax3.plot_wireframe(
        W,
        A,
        dchi2_plot,
        rstride=12,
        cstride=18,
        color=(1.0, 0.72, 0.45, 0.38),
        linewidth=0.50,
    )
    ax3.contour(
        W,
        A,
        dchi2,
        levels=[1, 4, 9],
        zdir="z",
        offset=0,
        colors=["white", "#ffb347", "#66d9ff"],
        linewidths=[3.0, 2.2, 1.8],
    )
    ax3.scatter([w0], [a0], [0], color="#1dd386", s=70, edgecolors="#111111", label="генерация")
    ax3.scatter([best_w], [best_a], [0], color="#ffb347", s=70, edgecolors="#111111", label="минимум")
    ax3.set_xlim(0.35, 8.55)
    ax3.set_ylim(0.0, 1.0)
    ax3.set_zlim(0.0, zmax)
    ax3.set_box_aspect((2.8, 1.5, 2.34), zoom=1.35)
    ax3.set_xlabel(r"$\omega$", labelpad=9)
    ax3.set_ylabel(r"$A$", labelpad=9)
    ax3.set_zlabel("")
    ax3.view_init(elev=24, azim=-62)
    # ax3.set_title("Осцилляционная форма не обязана быть параболой", pad=12, fontsize=16, fontweight="bold")

    # fig.text(
    #     0.50,
    #     0.045,
    #     r"$P(t; A,\omega)=1-A\,\sin^2(\omega t)$: локальная ковариация описывает один минимум, но не всю поверхность",
    #     ha="center",
    #     va="center",
    #     color="#f2f2f2",
    #     fontsize=13,
    # )
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.12, top=0.90)
    fig.savefig(OUT / "lsq_oscillatory_chi2_surface.png", facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_quadratic_surface()
    make_oscillatory_surface()
