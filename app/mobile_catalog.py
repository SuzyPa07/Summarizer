import pandas as pd
from pathlib import Path
from functools import lru_cache

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ITEMS_FILE = DATA_DIR / "20191226-items.csv"
REVIEWS_FILE = DATA_DIR / "20191226-reviews.csv"


@lru_cache(maxsize=1)
def load_mobile_items():
    return pd.read_csv(ITEMS_FILE, low_memory=False)


@lru_cache(maxsize=1)
def load_mobile_reviews():
    return pd.read_csv(REVIEWS_FILE, low_memory=False)


@lru_cache(maxsize=1)
def get_mobile_products():
    items = load_mobile_items()
    reviews = load_mobile_reviews()

    items.columns = items.columns.str.strip()
    reviews.columns = reviews.columns.str.strip()

    # Precompute review counts once using a fast hash map
    clean_review_asins = reviews["asin"].dropna().astype(str).str.strip()
    review_counts = clean_review_asins.value_counts().to_dict()

    products = []

    for _, row in items.iterrows():
        asin = str(row.get("asin", "")).strip()

        if not asin or asin.lower() == "nan":
            continue

        title = str(row.get("title", "Unknown Product")).strip()
        brand = str(row.get("brand", "Unknown Brand")).strip()

        if title.lower() == "nan":
            title = "Unknown Product"

        if brand.lower() == "nan":
            brand = "Unknown Brand"

        count = review_counts.get(asin, 0)

        products.append({
            "product_id": "mobile_" + asin,
            "asin": asin,
            "product_name": title,
            "brand": brand,
            "review_count": int(count),
            "source": "mobile",
            "_search_key": f"{title.lower()} {brand.lower()} {asin.lower()}"
        })

    return products


def search_mobile_products(search_text):
    if not search_text or not search_text.strip():
        return []

    query = search_text.lower().strip()
    products = get_mobile_products()

    matches = [
        product for product in products
        if query in product["_search_key"]
    ]

    return matches[:10]


def get_mobile_product_reviews(asin):
    reviews_df = load_mobile_reviews()

    matches = reviews_df[
        reviews_df["asin"].astype(str).str.strip() == str(asin).strip()
    ]

    results = []

    for _, row in matches.iterrows():
        body = row.get("body")

        if pd.isna(body) or not str(body).strip():
            continue

        results.append({
            "review": str(body),
            "rating": (
                None if pd.isna(row.get("rating"))
                else row.get("rating")
            )
        })

    return results