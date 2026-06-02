"""
VCN3 - Calcul de la fréquence de retour
Loi     : Log-Normale
Estimateur : L-moments
Incertitude : Bootstrap paramétrique (PBOOT)

Adapté de Benjamin Renard (Irstea Lyon) / HydroPortailStats
Formule : q(T) = F⁻¹( (1/T - p0) / (1 - p0) ; µ, σ )
"""
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import warnings
warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# 1. Estimateur des L-moments pour la loi Log-Normale
# ---------------------------------------------------------------------------

def lmom_lognormal(z: np.ndarray) -> tuple[float, float]:
    """
    Estime les paramètres (mu, sigma) de la loi Log-Normale
    par la méthode des L-moments.

    Les L-moments d'ordre 1 et 2 sont :
        L1 = moyenne = exp(mu + sigma²/2)
        L2 = exp(mu + sigma²/2) * (2*Phi(sigma/sqrt(2)) - 1)
    où Phi est la CDF de la loi normale standard.

    On résout numériquement le rapport L2/L1 pour trouver sigma, puis mu.
    """
    n = len(z)
    z_sorted = np.sort(z)

    # Calcul des L-moments empiriques par la méthode PWM (Probability Weighted Moments)
    # b0 = L1 = moyenne
    # b1 = (1/n) * sum( (i-1)/(n-1) * z_i )
    i = np.arange(1, n + 1, dtype=float)
    b0 = np.mean(z_sorted)
    b1 = np.sum(((i - 1) / (n - 1)) * z_sorted) / n

    L1 = b0
    L2 = 2 * b1 - b0   # L-moment d'ordre 2 (L-scale)

    tau2 = L2 / L1      # L-CV (coefficient de variation des L-moments)

    # Résolution numérique : tau2 = 2*Phi(sigma/sqrt(2)) - 1
    # → sigma = sqrt(2) * Phi⁻¹( (tau2 + 1) / 2 )
    sigma = np.sqrt(2) * stats.norm.ppf((tau2 + 1) / 2)
    mu    = np.log(L1) - sigma**2 / 2

    return mu, sigma


def fit_lognormal_lmom(z: np.ndarray) -> tuple:
    """
    Ajuste une loi Log-Normale par L-moments.
    Retourne les paramètres au format scipy.stats.lognorm :
        (s=sigma, loc=0, scale=exp(mu))
    """
    mu, sigma = lmom_lognormal(z)
    return (sigma, 0.0, np.exp(mu))


# ---------------------------------------------------------------------------
# 2. Fonctions quantile et CDF Log-Normale
# ---------------------------------------------------------------------------

def quantile_lognormal(p: float, params: tuple) -> float:
    """Quantile de la loi Log-Normale pour la probabilité p."""
    return stats.lognorm.ppf(p, *params)


def cdf_lognormal(x: float, params: tuple) -> float:
    """CDF de la loi Log-Normale en x."""
    if x <= 0:
        return 0.0
    return stats.lognorm.cdf(x, *params)


# ---------------------------------------------------------------------------
# 3. Fréquences empiriques (plotting position Hazen)
# ---------------------------------------------------------------------------

def get_emp_freq(n: int) -> np.ndarray:
    """Fréquences empiriques de non-dépassement — formule de Hazen : (i-0.5)/n."""
    i = np.arange(1, n + 1, dtype=float)
    return (i - 0.5) / n


# ---------------------------------------------------------------------------
# 4. Calcul principal
# ---------------------------------------------------------------------------

def vcn3_frequence_retour(
        y: np.ndarray,
        T_grid: np.ndarray = None,
        split_zeros: bool = True,
        IC_level: float = 0.95,
        n_sim: int = 1000,
        seed: int = 42,
) -> dict:
    """
    Calcule la fréquence de retour du VCN3.

    Loi         : Log-Normale
    Estimateur  : L-moments
    Incertitude : Bootstrap paramétrique (PBOOT)
                  → on simule n_sim échantillons depuis la loi ajustée,
                    on ré-estime les paramètres sur chacun, on recalcule les quantiles.

    Paramètres
    ----------
    y           : série de VCN3 annuels (m³/s)
    T_grid      : périodes de retour (ans). Défaut : [2, 5, 10, 20, 50, 100]
    split_zeros : séparer les années à débit nul
    IC_level    : niveau de l'intervalle de confiance (ex. 0.95)
    n_sim       : nombre de simulations bootstrap
    seed        : graine aléatoire

    Retourne
    --------
    dict avec 'empirical', 'params', 'quantiles', 'pcdf', 'p0'
    """
    rng = np.random.default_rng(seed)

    if T_grid is None:
        T_grid = np.array([2, 5, 10, 20, 50, 100])

    y = np.asarray(y, dtype=float)
    ny = len(y)

    # -----------------------------------------------------------------------
    # 4.1 Séparation des zéros
    # -----------------------------------------------------------------------
    if split_zeros:
        z = y[y > 0]
        p0 = np.sum(y <= 0) / ny
    else:
        z = y.copy()
        p0 = 0.0

    if len(z) < 5:
        raise ValueError("Pas assez de valeurs positives (minimum 5 requis).")

    # -----------------------------------------------------------------------
    # 4.2 Ajustement par L-moments
    # -----------------------------------------------------------------------
    params = fit_lognormal_lmom(z)
    mu = np.log(params[2])  # params = (sigma, 0, exp(mu))
    sigma = params[0]

    # -----------------------------------------------------------------------
    # 4.3 Fréquences empiriques
    # -----------------------------------------------------------------------
    y_sorted = np.sort(y)
    freq_emp = get_emp_freq(ny)
    T_emp = 1.0 / freq_emp

    # -----------------------------------------------------------------------
    # 4.4 Quantiles théoriques
    # Formule : q(T) = F⁻¹( (1/T - p0) / (1 - p0) ; θ )
    # -----------------------------------------------------------------------
    p_grid = 1.0 / T_grid
    quantiles = []
    for p in p_grid:
        if p <= p0:
            quantiles.append(0.0)
        else:
            p_adj = (p - p0) / (1.0 - p0)
            quantiles.append(max(quantile_lognormal(p_adj, params), 0.0))
    quantiles = np.array(quantiles)

    # -----------------------------------------------------------------------
    # 4.5 Bootstrap PARAMÉTRIQUE pour les intervalles de confiance
    # On simule depuis la loi Log-Normale ajustée (et non depuis les données)
    # -----------------------------------------------------------------------
    alpha = 1.0 - IC_level
    Q_sim = np.full((n_sim, len(T_grid)), np.nan)

    for i in range(n_sim):
        # Simulation depuis la loi ajustée (bootstrap paramétrique)
        z_sim = stats.lognorm.rvs(*params, size=len(z), random_state=rng)

        # Recalcul de p0 : on tire ny valeurs en tout, dont n0 sont nulles
        n0_sim = rng.binomial(ny, p0)
        p0_sim = n0_sim / ny

        if len(z_sim) < 4:
            continue
        try:
            params_sim = fit_lognormal_lmom(z_sim)
            for j, p in enumerate(p_grid):
                if p <= p0_sim:
                    Q_sim[i, j] = 0.0
                else:
                    p_adj = (p - p0_sim) / (1.0 - p0_sim)
                    Q_sim[i, j] = max(quantile_lognormal(p_adj, params_sim), 0.0)
        except Exception:
            continue

    IC_low = np.nanquantile(Q_sim, alpha / 2, axis=0)
    IC_high = np.nanquantile(Q_sim, 1.0 - alpha / 2, axis=0)

    # -----------------------------------------------------------------------
    # 4.6 Grille CDF théorique (pour tracé)
    # -----------------------------------------------------------------------
    x_max = max(y.max(), quantiles.max()) * 1.2
    x_grid = np.linspace(0.001, x_max, 300)
    cdf_grid = np.array([p0 + (1 - p0) * cdf_lognormal(x, params) for x in x_grid])
    T_cdf = np.where(cdf_grid > 0, 1.0 / cdf_grid, np.nan)

    # -----------------------------------------------------------------------
    # 4.7 IC sur la grille continue (enveloppe lisse pour le tracé)
    # -----------------------------------------------------------------------
    Q_fine = np.full((n_sim, len(x_grid)), np.nan)
    rng2 = np.random.default_rng(seed)
    for i in range(n_sim):
        z_sim = stats.lognorm.rvs(*params, size=len(z), random_state=rng2)
        n0_sim = rng2.binomial(ny, p0)
        p0_sim = n0_sim / ny
        if len(z_sim) < 4:
            continue
        try:
            params_sim = fit_lognormal_lmom(z_sim)
            for j, p in enumerate(cdf_grid):
                if p <= p0_sim:
                    Q_fine[i, j] = 0.0
                else:
                    p_adj = (p - p0_sim) / (1.0 - p0_sim)
                    Q_fine[i, j] = max(quantile_lognormal(p_adj, params_sim), 0.0)
        except Exception:
            continue
    IC_low_fine = np.nanquantile(Q_fine, alpha / 2, axis=0)
    IC_high_fine = np.nanquantile(Q_fine, 1.0 - alpha / 2, axis=0)

    return {
        "y": y,
        "z": z,
        "p0": p0,
        "mu": mu,
        "sigma": sigma,
        "params": params,
        "empirical": {
            "y_sorted": y_sorted,
            "freq": freq_emp,
            "T": T_emp,
        },
        "quantiles": {
            "T": T_grid,
            "p": p_grid,
            "q": quantiles,
            "IC_low": IC_low,
            "IC_high": IC_high,
        },
        "pcdf": {
            "x": x_grid,
            "cdf": cdf_grid,
            "T": T_cdf,
            "IC_low": IC_low_fine,
            "IC_high": IC_high_fine,
        },
    }


# ---------------------------------------------------------------------------
# 5. Affichage console
# ---------------------------------------------------------------------------

def print_results(res: dict) -> None:
    print("=" * 65)
    print("  Loi : Log-Normale  |  Estimateur : L-moments  |  IC : PBOOT")
    print(f"  µ (log) = {res['mu']:.4f}   σ (log) = {res['sigma']:.4f}")
    print(f"  p0 (prob. débit nul) = {res['p0']:.3f}")
    print(f"  n total = {len(res['y'])}   n positifs = {len(res['z'])}")
    print("=" * 65)
    print(f"\n{'T (ans)':>10}  {'p non-dép.':>12}  {'VCN3 (m³/s)':>14}  {'IC bas':>10}  {'IC haut':>10}")
    print("-" * 65)
    q = res["quantiles"]
    for T, p, qv, ic_l, ic_h in zip(q["T"], q["p"], q["q"], q["IC_low"], q["IC_high"]):
        print(f"{T:>10.0f}  {p:>12.4f}  {qv:>14.4f}  {ic_l:>10.4f}  {ic_h:>10.4f}")
    print()


# ---------------------------------------------------------------------------
# 6. Tracé
# ---------------------------------------------------------------------------

def plot_results(res: dict, title: str = "Analyse fréquentielle VCN3",
                 output_path: str = "/mnt/user-data/outputs/vcn3_resultat.png") -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(title + "\n[Log-Normale — L-moments — Bootstrap paramétrique]",
                 fontsize=12, fontweight="bold")

    emp = res["empirical"]
    quant = res["quantiles"]
    pcdf = res["pcdf"]
    mask_cdf = np.isfinite(pcdf["T"]) & (pcdf["T"] > 0) & (pcdf["T"] < 500)

    # -------------------------------------------------------------------
    # Graphique 1 : Période de retour T (ans) vs débit
    # -------------------------------------------------------------------
    ax1 = axes[0]
    ax1.scatter(emp["T"], emp["y_sorted"], color="steelblue", s=20, zorder=5,
                alpha=0.8, label="Observations")
    ax1.plot(pcdf["T"][mask_cdf], pcdf["x"][mask_cdf], color="firebrick",
             linewidth=1.5, label="Loi Log-Normale (L-mom)")
    ax1.fill_between(pcdf["T"][mask_cdf],
                     pcdf["IC_low"][mask_cdf], pcdf["IC_high"][mask_cdf],
                     color="firebrick", alpha=0.15, label="IC 95% (PBOOT)")
    ax1.set_xscale("log")
    ax1.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax1.set_xlabel("Période de retour T (ans)", fontsize=11)
    ax1.set_ylabel("VCN3 (m³/s)", fontsize=11)
    ax1.set_title("Période de retour vs débit")
    ax1.legend(fontsize=9)
    ax1.grid(True, which="both", alpha=0.3)
    ax1.set_xlim(left=1)

    # -------------------------------------------------------------------
    # Graphique 2 : Fréquence de non-dépassement vs débit
    # axe x = probabilité de non-dépassement (0 → 1)
    # IC calculé sur la grille continue pcdf pour une enveloppe lisse
    # -------------------------------------------------------------------
    ax2 = axes[1]
    ax2.scatter(emp["freq"], emp["y_sorted"], color="steelblue", s=20, zorder=5,
                alpha=0.8, label="Observations")
    ax2.plot(pcdf["cdf"], pcdf["x"], color="firebrick",
             linewidth=1.5, label="Loi Log-Normale (L-mom)")
    ax2.fill_between(pcdf["cdf"],
                     pcdf["IC_low"], pcdf["IC_high"],
                     color="firebrick", alpha=0.15, label="IC 95% (PBOOT)")
    ax2.set_xlabel("Fréquence de non-dépassement", fontsize=11)
    ax2.set_ylabel("VCN3 (m³/s)", fontsize=11)
    ax2.set_title("Fréquence vs débit")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 7000)

    # -------------------------------------------------------------------
    # Graphique 3 : CDF — débit vs probabilité de non-dépassement
    # -------------------------------------------------------------------
    ax3 = axes[2]
    ax3.plot(pcdf["x"], pcdf["cdf"], color="firebrick", linewidth=1.5,
             label="CDF Log-Normale (L-mom)")
    ax3.scatter(emp["y_sorted"], emp["freq"], color="steelblue", s=20,
                zorder=5, alpha=0.8, label="Fréquences empiriques (Hazen)")
    if res["p0"] > 0:
        ax3.axhline(res["p0"], color="gray", linestyle="--", linewidth=0.8,
                    label=f"p0 = {res['p0']:.2f}")
    ax3.set_xlabel("VCN3 (m³/s)", fontsize=11)
    ax3.set_ylabel("Probabilité de non-dépassement", fontsize=11)
    ax3.set_title("CDF empirique vs théorique")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Graphique sauvegardé : {output_path}")


# ---------------------------------------------------------------------------
# 7. Exemple d'utilisation
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    vcn3_exemple =  pd.read_csv(Path("output/test/vcn3_station_U200201001.csv"))["vcn3_mensuel"].to_numpy()

    resultats = vcn3_frequence_retour(
        y           = vcn3_exemple,
        T_grid      = np.array([2, 5, 10, 20, 50, 100]),
        split_zeros = True,
        IC_level    = 0.95,
        n_sim       = 1000,
    )

    print_results(resultats)
    plot_results(resultats, title="VCN3 — Analyse fréquentielle", output_path=Path("output/test/vcn3_plot_result.png"))
