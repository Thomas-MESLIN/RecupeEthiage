import pandas as pd

pd_moyenne = pd.DataFrame(
    data={"donnne":[0.1,0.5,0.6,pd.NA]}
)

pd_moyenne = pd_moyenne.mean()
print(pd_moyenne)
