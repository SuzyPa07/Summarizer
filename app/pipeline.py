from app.preprocessing import clean_text
from app.aspect_extraction import extract_aspects
from app.sentiment_analysis import analyze_sentiment


def analyze_review(review, domain="electronics"):

    # Step 1: Preprocess
    clean_review = clean_text(review)

    # Step 2: Extract aspects
    aspects = extract_aspects(clean_review, domain)

    # Step 3: Analyze sentiment
    sentiment = analyze_sentiment(clean_review)

    # Create aspect-wise results
    aspect_results = {}

    for aspect in aspects:
        aspect_results[aspect] = sentiment

    # If no aspect is found
    if not aspect_results:
        aspect_results["general"] = sentiment

    return {
        "clean_review": clean_review,
        "aspects": aspect_results,
        "summary": create_summary(aspect_results)
    }


def create_summary(aspects):

    if "general" in aspects:
        return "The review expresses a " + aspects["general"].lower() + " opinion."

    aspect_names = list(aspects.keys())

    return (
        "The review discusses "
        + ", ".join(aspect_names)
        + " and expresses an overall "
        + aspects[aspect_names[0]].lower()
        + " opinion."
    )