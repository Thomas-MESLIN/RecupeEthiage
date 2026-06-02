import numpy as np
import pandas as pd
from lmoments3 import lmom_ratios
from lmoments3 import distr

vcn3_numpy_array = pd.read_csv("output/test/vcn3_station_U200201001.csv")["vcn3_mensuel"].to_numpy()

lmoms = lmom_ratios(vcn3_numpy_array)
print(lmoms)

params = distr

print(params)

boot_q5 = []
nboot = 5000
for _ in range(nboot):

    sample = distr.ln3.rand(
        len(vcn3_numpy_array),
        params
    )

    p_boot = distr.ln3.lmom_fit(sample)

    q = distr.ln3.qua(
        0.2,      # T=5 ans
        p_boot
    )

    boot_q5.append(q)
boot_q5 = np.array(boot_q5)

ic_low = np.quantile(boot_q5,0.025)
ic_high = np.quantile(boot_q5,0.975)

print(ic_low, ic_high)