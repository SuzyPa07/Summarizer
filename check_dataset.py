import pandas as pd

file_path = "data/1429_1.csv"

df = pd.read_csv(file_path)

print("\n--- COLUMNS ---")
print(df.columns.tolist())

print("\n--- FIRST 5 REVIEWS ---")
print(df.head())

print("\n--- DATASET SIZE ---")
print(df.shape)