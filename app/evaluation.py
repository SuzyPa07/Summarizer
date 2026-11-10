import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from app.roberta_sentiment import analyze_with_roberta
from app.preprocessing import clean_text


def rating_to_sentiment(rating):
    """Convert star ratings into sentiment labels."""

    try:
        rating = float(rating)
    except (ValueError, TypeError):
        return None

    if rating <= 2:
        return "Negative"
    elif rating == 3:
        return "Neutral"
    elif rating >= 4:
        return "Positive"

    return None


def evaluate_model(csv_path): 
    """Evaluate pretrained RoBERTa using rating-derived labels."""

    df = pd.read_csv(csv_path, low_memory=False)
    df = df.sample(n=min(100, len(df)), random_state=42)

    if "reviews.rating" not in df.columns:
        raise ValueError("Rating column not found.")

    if "reviews.text" not in df.columns:
        raise ValueError("Review text column not found.")

    df = df[["reviews.text", "reviews.rating"]].dropna()

    df["actual"] = df["reviews.rating"].apply(
        rating_to_sentiment
    )

    df = df.dropna(subset=["actual"])

    df["predicted"] = df["reviews.text"].apply(
        lambda review: analyze_with_roberta(clean_text(review))
    )

    actual = df["actual"]
    predicted = df["predicted"]

    labels = ["Negative", "Neutral", "Positive"]

    return {
        "total_reviews_evaluated": len(df),
        "accuracy": round(accuracy_score(actual, predicted), 4),
        "precision": round(
            precision_score(
                actual, predicted,
                labels=labels,
                average="macro",
                zero_division=0
            ), 4
        ),
        "recall": round(
            recall_score(
                actual, predicted,
                labels=labels,
                average="macro",
                zero_division=0
            ), 4
        ),
        "f1_score": round(
            f1_score(
                actual, predicted,
                labels=labels,
                average="macro",
                zero_division=0
            ), 4
        ),
        "classification_report": classification_report(
            actual,
            predicted,
            labels=labels,
            zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            actual,
            predicted,
            labels=labels
        ).tolist()
    }


if __name__ == "__main__":
    results = evaluate_model("data/1429_1.csv")

    for key, value in results.items():
        print(f"\n{key}:")
        print(value)