import pandas as pd
import os, glob, hashlib

dfs = pd.read_parquet("dataset.parquet.gzip")
for src in dfs.Source.unique():
    ID = str(hashlib.md5(src.encode('utf-8')).hexdigest())
    if not os.path.isfile("xls/"+ID+".xlsx"):
        print("Missing table:",ID)
        df = dfs[dfs.Source == src].reset_index(drop=True)
        df.to_excel("xls/"+ID+".xlsx",index=False)

files = glob.glob("xls/*.xlsx")
print(len(files))
dfs = []
for f in files:
    dfs.append(pd.read_excel(f))
df = pd.concat(dfs).reset_index(drop=True)
df.to_parquet("xls/db.parquet.gzip", compression="gzip")
print(len(df))
df.head(3)