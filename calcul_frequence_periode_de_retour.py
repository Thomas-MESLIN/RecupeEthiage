"""
VCN3 - Calcul de la fréquence de retour
Loi     : Log-Normale
Estimateur : L-moments
Incertitude : Bootstrap paramétrique (PBOOT)

Adapté de Benjamin Renard (Irstea Lyon) / HydroPortailStats
"""
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as stats
import plot_grandeur
from tqdm import tqdm
import utils
import calcul_vcn3
import station
from lmoments3 import distr as lm_distr

# ---------------------------------------------------------------------------
# 1. Estimateur des L-moments pour la loi Log-Normale
# ---------------------------------------------------------------------------

def fit_lognormal_lmom(z: np.ndarray) -> tuple:
    """
    Estimateur des L-moments pour la loi Log-Normale.
    :param z: Les données à estimer.
    :return: Renvoie l'écart type, un truc et la moyenne.
    """
    paras = lm_distr.nor.lmom_fit(np.log(z))   # {"loc": mu, "scale": sigma}
    return (paras["scale"], 0.0, np.exp(paras["loc"]))

# ---------------------------------------------------------------------------
# 2. Fonctions quantile et CDF Log-Normale
# ---------------------------------------------------------------------------

def quantile_lognormal(p: float, params: tuple) -> float:
    """
    Quantile de la loi Log-Normale pour la probabilité p.
    :param p: La probabilité pour extraire ses quantiles
    :param params: Le résultat de fit_lognormal_lmom()
    :return: Renvoie les quantiles de la loi Log-Normale pour cette probabilité.
    """
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

def is_enough_data(y: np.ndarray, split_zeros:bool) -> bool:
    """
    Renvoie vrai si il y a assez de données dans la série pour calculer le reste.
    :param y:
    :param split_zeros:
    :return:
    """
    y = np.asarray(y, dtype=float)
    ny = len(y)
    if ny == 0:
        return False

    if split_zeros:
        z = y[y > 0]
    else:
        z = y.copy()

    return len(z) >= 5

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
        'debit_obs' : débit en entrée
        'frequence_non_depassement' : probabilité de non-dépassement interpolée
        'Periode_de_retour' : période de retour (ans)
        'Periode_de_retour_interval_confiance_bas' : borne basse IC 95% sur T
        'Periode_de_retour_interval_confiance_haut': borne haute IC 95% sur T
    """
    x = res["pcdf"]["x"]
    cdf = res["pcdf"]["cdf"]
    ic_low = res["pcdf"]["IC_low"]
    ic_high = res["pcdf"]["IC_high"]

    if q_obs <= 0:
        return {"q": q_obs, "p": res["p0"], "T": 1.0 / res["p0"] if res["p0"] > 0 else np.inf,
                "IC_low": np.nan, "IC_high": np.nan}

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

    result = {"debit_obs": q_obs, "frequence_non_depassement": p_interp, "Periode_de_retour": T,
              "Periode_de_retour_interval_confiance_bas": T_low, "Periode_de_retour_interval_confiance_haut": T_high}

    return result

# ==========================
# 9. Get resultat station
# ==========================

def get_result_station(code_station:str, mois:str, code_sandre:str, vcn3_observation, plot_resultat:bool=False) -> dict:
    """
    Renvoie la période de retour de la station et sa fréquence de non-dépassement,
    ainsi que les intervalles de confiance associés
    :param code_sandre:
    :param plot_resultat: Si a True, va crée et sauvegarder des plots de toutes les statistiques calculées.
    :param code_station:Le code de la station à évaluer.
    :param mois: Au format MM
    :param vcn3_observation: vcn3 observé, à comparer avec les données historiques
    :return: dict avec :
        'debit_obs' : débit en entrée
        'frequence_non_depassement' : probabilité de non-dépassement interpolé
        'Periode_de_retour' : période de retour (ans)
        'Periode_de_retour_interval_confiance_bas' : borne basse IC 95% sur T
        'Periode_de_retour_interval_confiance_haut' : borne haute IC 95% sur T
    """
    mois_a_etudier = f"{mois:02}"
    calcul_vcn3.ensure_calcul_vcn3_station(code_station, code_sandre)
    df_all_vcn3 = pd.read_csv(utils.get_path_vcn3_station(code_station))
    df_mois_precis = df_all_vcn3[df_all_vcn3["annee_mois"].astype(str).str.contains(f"-{mois_a_etudier}")]
    # On enlève les cases vide...
    vcn3_a_calculer =  df_mois_precis["vcn3_mensuel"].dropna().to_numpy()
    if is_enough_data(vcn3_a_calculer, True):
        try:
            resultats = vcn3_frequence_retour(
                y           = vcn3_a_calculer,
                T_grid      = np.array([2, 5, 10, 20, 50, 100]),
                split_zeros = True,
                IC_level    = 0.95,
                n_sim       = 1000,
            )
        except ValueError:
            return {"debit_obs":vcn3_observation}
    else:
        print(code_station)
        print("Donnéé insuffisante")
        return {"debit_obs":vcn3_observation}


    # print_results(resultats)
    # Juste le résultat numérique
    resultat_periode_de_retour = get_period_from_flow(q_obs=vcn3_observation, res=resultats)

    if plot_resultat:
        plot_grandeur.plot_result_station(code_station, mois_a_etudier, resultat_periode_de_retour, resultats)
    return resultat_periode_de_retour

# ---------------------------------------------------------------------------
# 8. Exemple d'utilisation
# ---------------------------------------------------------------------------

def ensure_frequence_non_depassement_periode_retour_calcule(annee_mois:str, code_sandre:str,
    is_result_plotted = False) -> pd.DataFrame:
    """
    S'assure que la frequence de retour est calculé et renvoie le résultat de celle-ci dans un DataFrame
    :param is_result_plotted: Si True, les résultats sont enregistré dans des plots, affichant les différentes stats calculées
    :param annee_mois: Format AAAA-MM
    :param code_sandre: Le code sandre des stations à explorer.
    :return: Un Dataframe contenant les périodes de retour
    """
    path_periode_de_retour = utils.get_path_periode_de_retour(code_sandre, annee_mois)
    if utils.is_res_updated_with_source(utils.get_path_sources(code_sandre, "QmnJ", annee_mois), path_periode_de_retour):
        return pd.DataFrame(pd.read_csv(utils.get_path_periode_de_retour(code_sandre, annee_mois)))

    print("Calcul des fréquences de non dépassement et des périodes de retour.")
    date = pd.to_datetime(f"{annee_mois}-01")
    annee_mois = date.strftime("%Y-%m")
    mois_str = date.strftime("%m")
    annee = date.year
    mois = date.month
    df_station = station.get_stations(code_sandre, annee_mois)
    # On charge les données des stations du mois désiré.

    all_rows = []
    with tqdm(total=len(df_station)) as pbar:
        for station_code in df_station["code_station"]:
            calcul_vcn3.ensure_calcul_vcn3_station(station_code, code_sandre)
            valeur = calcul_vcn3.get_vcn3_station_mois(calcul_vcn3.get_df_moyenne_glissante(annee_mois, code_sandre),station_code, annee=annee, mois=mois)
            if not pd.isna(valeur):
                row = get_result_station(station_code, mois_str, code_sandre, valeur, plot_resultat=is_result_plotted)
                row["code_station"] = station_code
                df_date_ouverture = df_station[df_station["code_station"] == station_code]["date_ouverture_station"]
                row["date_ouverture_station"] = df_date_ouverture.iloc[0] if not df_date_ouverture.empty else pd.NA
                all_rows.append(row)
            else:
                print(f"La station {station_code} n'a pas de donnée lors du mois {date.strftime('%B')}.")
            pbar.update(1)

    df_all_analysis = pd.DataFrame(data=all_rows)
    path_periode_retour = utils.get_path_periode_de_retour(code_sandre, annee_mois)
    df_all_analysis.to_csv(path_periode_retour,
                           index=False)
    print(f"Fréquence de non dépassement et période de retour calculé, Fichier sauvegardé à : {path_periode_retour}")
    return df_all_analysis

if __name__ == "__main__":
    ensure_frequence_non_depassement_periode_retour_calcule("2026-04","BSH001", is_result_plotted=False)
    ensure_frequence_non_depassement_periode_retour_calcule("2026-04","custom", is_result_plotted=False)
    ensure_frequence_non_depassement_periode_retour_calcule("2026-05","BSH001", is_result_plotted=False)
    ensure_frequence_non_depassement_periode_retour_calcule("2026-05","custom", is_result_plotted=True)
