import re

from app.preprocessing import clean_text
from app.aspect_extraction import extract_aspects
from app.sentiment_analysis import ASPECT_TERMS
from app.roberta_sentiment import analyze_with_roberta


def get_aspect_text(review, aspect):
    """
    Find sentences that mention the selected aspect.
    If none are found, use the complete review.
    """

    keywords = ASPECT_TERMS.get(aspect, [aspect])

    sentences = re.split(
        r"[.!?]+|\b(?:but|however|although|though)\b",
        review,
        flags=re.IGNORECASE
    )

    relevant_sentences = []

    for sentence in sentences:
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, sentence, re.IGNORECASE):
                relevant_sentences.append(sentence.strip())
                break

    if relevant_sentences:
        return " ".join(relevant_sentences)

    return review


def analyze_review(review):

    # Step 1: Preprocess the review
    clean_review = clean_text(review)

    # Step 2: Extract product aspects
    aspects = extract_aspects(clean_review)

    # Step 3: Analyse sentiment using pretrained RoBERTa
    aspect_results = {}

    for aspect in aspects:

        aspect_text = get_aspect_text(clean_review, aspect)

        sentiment = analyze_with_roberta(aspect_text)

        aspect_results[aspect] = sentiment

    # If no aspect is found, analyse the complete review
    if not aspect_results:

        aspect_results["general"] = analyze_with_roberta(
            clean_review
        )

    return {
        "clean_review": clean_review,
        "aspects": aspect_results,
        "summary": create_summary(aspect_results)
    }


def create_summary(aspects):

    if "general" in aspects:
        return (
            "The review expresses a "
            + aspects["general"].lower()
            + " overall opinion."
        )

    positive_aspects = [
        aspect for aspect, sentiment in aspects.items()
        if sentiment == "Positive"
    ]

    negative_aspects = [
        aspect for aspect, sentiment in aspects.items()
        if sentiment == "Negative"
    ]

    neutral_aspects = [
        aspect for aspect, sentiment in aspects.items()
        if sentiment == "Neutral"
    ]

    parts = []

    if positive_aspects:
        parts.append(
            "Positive feedback on " + ", ".join(positive_aspects)
        )

    if negative_aspects:
        parts.append(
            "Negative feedback on " + ", ".join(negative_aspects)
        )

    if neutral_aspects:
        parts.append(
            "Neutral feedback on " + ", ".join(neutral_aspects)
        )

    return ". ".join(parts) + "."