from app import preprocessing

file_path = "data/reviews_0-250.csv"

df = preprocessing.preprocess_dataset(file_path)

print("\n--- CLEANED REVIEW ---")
print(df["clean_review"].head())