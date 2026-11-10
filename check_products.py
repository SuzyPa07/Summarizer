
import pandas as pd
from collections import Counter

# Load dataset
df = pd.read_csv("data/1429_1.csv", low_memory=False)

# Clean product names
def clean_name(value):
    if pd.isna(value):
        return "Unknown Product"

    names = str(value).split(",,,\r\n")
    names = [name.strip(" ,\r\n\"") for name in names]

    return next(
        (name for name in names if name),
        "Unknown Product"
    )


df["clean_name"] = df["name"].apply(clean_name)

# Group reviews using product ID
products = []

for product_id, group in df.groupby("id", dropna=True):

    names = [
        name for name in group["clean_name"]
        if name != "Unknown Product"
    ]

    if not names:
        continue

    product_name = Counter(names).most_common(1)[0][0]

    asins = group["asins"].dropna().astype(str).unique()

    review_count = group["reviews.text"].notna().sum()

    products.append({
        "Product ID": product_id,
        "Product Name": product_name,
        "ASIN": asins[0] if len(asins) else "Not available",
        "Review Count": review_count
    })

result = pd.DataFrame(products)

print("\nTOTAL PRODUCTS:", len(result))
print("\nPRODUCT CATALOG:\n")

print(result.head(30).to_string(index=False))
