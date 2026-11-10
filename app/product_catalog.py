import pandas as pd
from pathlib import Path
from functools import lru_cache

# Dataset location
DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "1429_1.csv"
)


@lru_cache(maxsize=1)
def load_dataset():
    df = pd.read_csv(
        DATASET_PATH,
        low_memory=False
    )
    return df


@lru_cache(maxsize=1)
def get_product_catalog():
    df = load_dataset()

    # Keep rows with a product ID
    df = df.dropna(subset=["id"])

    # Vectorized review count per ID
    has_review = (
        df["reviews.text"]
        .dropna()
        .astype(str)
        .str.strip()
        .ne("")
    )
    review_counts = df.loc[has_review.index, :].groupby("id").size().to_dict()

    products = []

    for product_id, group in df.groupby("id"):
        # Get the most frequently occurring product name
        names = group["name"].dropna().astype(str)

        if names.empty:
            product_name = "Unknown Product"
        else:
            product_name = names.value_counts().index[0]

        # Get ASIN
        asins = group["asins"].dropna().astype(str)
        asin = (
            asins.value_counts().index[0]
            if not asins.empty
            else "Not available"
        )

        products.append({
            "product_id": str(product_id),
            "product_name": product_name,
            "asin": asin,
            "review_count": int(review_counts.get(product_id, 0)),
            "_search_name": product_name.lower()
        })

    return products


def search_products(search_text):
    if not search_text.strip():
        return []

    search_text = search_text.lower().strip()
    products = get_product_catalog()

    matching_products = [
        product
        for product in products
        if search_text in product["_search_name"]
    ]

    return matching_products[:10]


def get_product_reviews(product_id):
    df = load_dataset()

    product_rows = df[
        df["id"].astype(str) == str(product_id)
    ]

    reviews = []

    for _, row in product_rows.iterrows():
        review_text = row.get("reviews.text")

        if pd.isna(review_text) or not str(review_text).strip():
            continue

        reviews.append({
            "review": str(review_text),
            "rating": (
                None
                if pd.isna(row.get("reviews.rating"))
                else row.get("reviews.rating")
            )
        })

    return reviews