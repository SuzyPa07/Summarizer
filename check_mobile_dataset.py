from app.mobile_catalog import (
    get_mobile_products,
    search_mobile_products,
    get_mobile_product_reviews
)

print("\n========== MOBILE DATASET TEST ==========\n")

products = get_mobile_products()

print("Total mobile products:", len(products))

print("\nFirst 10 products:\n")

for product in products[:10]:
    print(
        product["brand"],
        "|",
        product["product_name"],
        "| Reviews:",
        product["review_count"]
    )

print("\n========== SEARCH TEST ==========\n")

for query in ["Samsung", "Motorola", "Nokia"]:
    results = search_mobile_products(query)

    print(f"{query}: {len(results)} matching products")

    for product in results[:3]:
        print("  -", product["product_name"])

print("\n========== REVIEW MATCH TEST ==========\n")

if products:
    selected = products[0]

    reviews = get_mobile_product_reviews(selected["asin"])

    print("Selected product:", selected["product_name"])
    print("Matched reviews:", len(reviews))

    if reviews:
        print("Sample review:", reviews[0]["review"][:200])
    else:
        print("No review text found for this product.")

print("\n========== TEST COMPLETE ==========")