from app import preprocessing

file_path = "data/1429_1.csv"

df = preprocessing.preprocess_dataset(file_path)

print("\n--- CLEANED REVIEW ---")
print(df["clean_review"].head())