from app.aspect_extraction import extract_aspects

reviews = [
    "The camera quality is excellent.",
    "The build quality is poor.",
    "The product quality is amazing.",
    "The screen quality is terrible.",
    "The battery is bad, but the camera quality is excellent."
]

for review in reviews:
    print("\nReview:", review)
    print("Aspects:", extract_aspects(review))