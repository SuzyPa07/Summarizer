from app.pipeline import analyze_review

test_reviews = [
    "The product quality is amazing.",
    "The screen quality is terrible.",
    "The battery is bad, but the camera quality is excellent.",
    "The battery life is excellent and the phone is amazing.",
    "The screen is terrible and the battery drains very quickly.",
    "The phone is okay and works as expected."
]

for review in test_reviews:
    print("\n" + "=" * 60)
    print("Review:", review)

    result = analyze_review(review)

    print("Aspects:", result["aspects"])
    print("Summary:", result["summary"])