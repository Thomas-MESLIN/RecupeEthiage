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
import cProfile

from tqdm import tqdm

import utils
import calcul_vcn3_1991_2020
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
    # 4.5 Grille de probabilités fixe pour le tracé continu
    #
    # p_fine est une grille FIXE de probabilités (indépendante des params),
    # qui sert d'axe commun à toutes les simulations bootstrap.
    # Pour chaque sim, on calcule q_sim(p) = F_sim⁻¹(p) sur cette grille.
    # Les IC résultants sont donc des intervalles sur les DÉBITS à p fixé,
    # ce qui est la définition correcte de l'enveloppe d'incertitude.
    #
    # x_grid et cdf_grid sont ensuite dérivés des params initiaux pour le tracé.
    # -----------------------------------------------------------------------
    p_fine = np.linspace(1e-4, 1.0 - 1e-4, 300)  # grille fixe de probabilités
    x_grid = np.array([  # débits théoriques initiaux
        0.0 if p <= p0 else max(quantile_lognormal((p - p0) / (1.0 - p0), params), 0.0)
        for p in p_fine
    ])
    cdf_grid = p_fine  # par construction
    T_cdf = np.where(p_fine > 0, 1.0 / p_fine, np.nan)

    # -----------------------------------------------------------------------
    # 4.6 Bootstrap PARAMÉTRIQUE — une seule boucle pour T_grid ET p_fine
    # -----------------------------------------------------------------------
    alpha = 1.0 - IC_level
    Q_sim = np.full((n_sim, len(T_grid)), np.nan)  # IC sur points discrets T_grid
    Q_fine = np.full((n_sim, len(p_fine)), np.nan)  # IC sur grille continue p_fine

    for i in range(n_sim):
        z_sim = stats.lognorm.rvs(*params, size=len(z), random_state=rng)
        n0_sim = rng.binomial(ny, p0)
        p0_sim = n0_sim / ny

        if len(z_sim) < 4:
            continue
        try:
            params_sim = fit_lognormal_lmom(z_sim)

            # IC discrets (T_grid) — vectorisé
            mask_sim = p_grid > p0_sim
            p_adj = np.where(mask_sim, (p_grid - p0_sim) / (1.0 - p0_sim), np.nan)
            q_vec = np.where(mask_sim, np.maximum(quantile_lognormal(p_adj, params_sim), 0.0), 0.0)
            Q_sim[i, :] = q_vec

            # IC continus (p_fine) — vectorisé
            mask_fine = p_fine > p0_sim
            p_adj_fine = np.where(mask_fine, (p_fine - p0_sim) / (1.0 - p0_sim), np.nan)
            q_fine_vec = np.where(mask_fine, np.maximum(quantile_lognormal(p_adj_fine, params_sim), 0.0), 0.0)
            Q_fine[i, :] = q_fine_vec

        except Exception:
            continue

    IC_low = np.nanquantile(Q_sim, alpha / 2, axis=0)
    IC_high = np.nanquantile(Q_sim, 1.0 - alpha / 2, axis=0)
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
# 7. Période de retour d'un débit donné
# ---------------------------------------------------------------------------

def get_period_from_flow(q_obs: float, res: dict) -> dict:
    """
    Retrouve la période de retour T correspondant à un débit observé q_obs,
    par interpolation sur la courbe théorique (grille continue pcdf).

    Paramètres
    ----------
    q_obs : débit observé (m³/s)
    res   : résultat de vcn3_frequence_retour()

    Retourne
    --------
    dict avec :
        'q'      : débit en entrée
        'p'      : probabilité de non-dépassement interpolée
        'T'      : période de retour (ans)
        'IC_low' : borne basse IC 95% sur T
        'IC_high': borne haute IC 95% sur T
    """
    x = res["pcdf"]["x"]
    cdf = res["pcdf"]["cdf"]
    ic_low = res["pcdf"]["IC_low"]
    ic_high = res["pcdf"]["IC_high"]

    if q_obs <= 0:
        return {"q": q_obs, "p": res["p0"], "T": 1.0 / res["p0"] if res["p0"] > 0 else np.inf,
                "IC_low": np.nan, "IC_high": np.nan}

    if q_obs < x[0] or q_obs > x[-1]:
        raise ValueError(f"q_obs={q_obs} hors de la plage de la grille [{x[0]:.3f}, {x[-1]:.3f}].")

    # Interpolation linéaire sur la grille x → cdf
    p_interp = np.interp(q_obs, x, cdf)
    # Pour l'IC : la borne basse du IC débit → borne haute du IC en T (et vice-versa)
    # ic_low[i] = débit bas pour une fréquence donnée → T plus grand
    # ic_high[i] = débit haut pour une fréquence donnée → T plus petit
    # On inverse : pour q_obs fixé, on cherche la fréquence sur ic_high et ic_low
    p_ic_low = np.interp(q_obs, ic_high, cdf)  # q sur courbe haute → fréquence basse → T grand
    p_ic_high = np.interp(q_obs, ic_low, cdf)  # q sur courbe basse → fréquence haute → T petit

    T = 1.0 / p_interp if p_interp > 0 else np.inf
    T_low = 1.0 / p_ic_high if p_ic_high > 0 else np.inf
    T_high = 1.0 / p_ic_low if p_ic_low > 0 else np.inf

    result = {"q": q_obs, "p": p_interp, "T": T, "IC_low": T_low, "IC_high": T_high}

    # Affichage
    print(f"\n{'=' * 55}")
    print(f"  Débit observé          : {q_obs:.4f} m³/s")
    print(f"  Prob. non-dépassement  : {p_interp:.4f}")
    print(f"  Période de retour      : {T:.1f} ans")
    print(f"  IC 95%                 : [{T_low:.1f} – {T_high:.1f}] ans")
    print(f"{'=' * 55}\n")

    return result


def plot_period_from_flow(q_obs: float, res: dict, code_station: str,
                          output_path: str = "/mnt/user-data/outputs/vcn3_retour_qobs.png") -> None:
    """Trace la courbe T vs débit avec le débit q_obs mis en évidence."""
    r = get_period_from_flow(q_obs, res)

    pcdf = res["pcdf"]
    emp = res["empirical"]
    T_min = min(emp["T"].min(), 1.0)
    T_max = emp["T"].max() * 1.05
    mask = np.isfinite(pcdf["T"]) & (pcdf["T"] >= T_min) & (pcdf["T"] <= T_max)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(T_min, T_max)

    ax.fill_between(pcdf["T"][mask], pcdf["IC_low"][mask], pcdf["IC_high"][mask],
                    color="firebrick", alpha=0.15, label="IC 95% (PBOOT)")
    ax.plot(pcdf["T"][mask], pcdf["x"][mask], color="firebrick",
            linewidth=1.5, label="Loi Log-Normale (L-mom)")
    ax.scatter(emp["T"], emp["y_sorted"], color="steelblue", s=20, zorder=5,
               alpha=0.8, label="Observations")

    # Lignes de lecture
    ax.axhline(q_obs, color="darkorange", linestyle="--", linewidth=1.2)
    ax.axvline(r["T"], color="darkorange", linestyle="--", linewidth=1.2)
    ax.plot(r["T"], q_obs, "o", color="darkorange", markersize=9, zorder=10,
            label=f"q = {q_obs:.2f} m³/s → T = {r['T']:.1f} ans")

    # Zone IC sur T (bande verticale)
    ax.axvspan(r["IC_low"], r["IC_high"], color="darkorange", alpha=0.10,
               label=f"IC T : [{r['IC_low']:.1f} – {r['IC_high']:.1f}] ans")

    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.set_xlabel("Période de retour T (ans)", fontsize=11)
    ax.set_ylabel("VCN3 (m³/s)", fontsize=11)
    ax.set_title(f"Période de retour pour q = {q_obs:.4f} m³/s - Station {code_station}", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, which="both", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Graphique sauvegardé : {output_path}")


# ==========================
# 9. Get resultat station
# ==========================

def get_result_station(code_station:str, mois:str, vcn3_observation):
    """

    :param code_station:
    :param mois:
    :param vcn3_observation:
    :return:
    """
    mois_a_etudier = f"{mois:02}"
    calcul_vcn3_1991_2020.ensure_calcul_vcn3_station(code_station)
    df_all_vcn3 = pd.read_csv(utils.get_path_vcn3_station(code_station))
    df_mois_precis = df_all_vcn3[df_all_vcn3["annee_mois"].astype(str).str.contains(f"-{mois_a_etudier}")]
    # On enlève les cases vide...
    vcn3_exemple =  df_mois_precis["vcn3_mensuel"].dropna().to_numpy()

    try:
        resultats = vcn3_frequence_retour(
            y           = vcn3_exemple,
            T_grid      = np.array([2, 5, 10, 20, 50, 100]),
            split_zeros = True,
            IC_level    = 0.95,
            n_sim       = 1000,
        )
    except ValueError:
        return {}

    #print_results(resultats)
    plot_results(resultats, title=f"VCN3 — Analyse fréquentielle - Station : {code_station}", output_path=Path(f"output/VCN3/plot_stations/analyse-frequentielle-{code_station}-{mois:02}.png"))
    # Juste le résultat numérique
    r = get_period_from_flow(q_obs=vcn3_observation, res=resultats)

    plot_period_from_flow(q_obs=vcn3_observation, res=resultats, code_station=code_station,
                      output_path=Path(f"output/VCN3/plot_stations/periode-de-retour-{code_station}-{mois:02}.png"))
    print(f"Résultat période estimé : {r}")
    return r

# ---------------------------------------------------------------------------
# 8. Exemple d'utilisation
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    #get_result_station("U214201001", 4, 10539)
    code_sandre = "BSH001"
    date = pd.to_datetime("2026-04-01")
    annee_mois = date.strftime("%Y-%m")
    mois = date.strftime("%m")
    df_station = utils.get_stations("BSH001","2026-04")
    df_station = df_station.head(30)
    # On charge les données des stations du mois désiré.

    df_annee_mois_selectionne = pd.read_csv(utils.get_path_vcn3(code_sandre, annee_mois))
    all_rows = []
    with tqdm(total=len(df_station)) as pbar:
        for station_code in df_station["code_station"]:
            df_valeur = df_annee_mois_selectionne[df_annee_mois_selectionne["code_station"] == station_code]
            valeur = df_valeur["vcn3_mensuel"].iloc[0] if not df_valeur.empty else pd.NA
            if not pd.isna(valeur):
                row = get_result_station(station_code, mois, valeur)
                row["code_station"] = station_code
                all_rows.append(row)
            else:
                print(f"La station {station_code} n'a pas de donnée du mois {mois}.")
            df_all_analysis = pd.DataFrame(data=all_rows)
            df_all_analysis.to_csv(Path(f"output/VCN3/analyse_frequence_periode/analyse-frequence-{annee_mois}.csv"),
                                   index=False)
            pbar.update(1)
    #df_all_analysis = pd.DataFrame(data=all_rows)
    #df_all_analysis.to_csv(Path(f"output/VCN3/analyse_frequence_periode/analyse-frequence-{annee_mois}.csv"),
    #                       index=False)
# calcul_vcn3_1991_2020.ensure_calcul_vcn3_station(station_code)
#