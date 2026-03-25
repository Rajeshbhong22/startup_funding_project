import pandas as pd

df=pd.read_csv("data\startup_funding.csv")
#find out distinct startup's names
sorted(df["Startup Name"].unique().tolist())
