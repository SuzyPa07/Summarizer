import pandas as pd
import re
import spacy


# Load the English spaCy model
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def clean_text(text):
    """Clean review text while preserving its original wording."""
    if pd.isna(text):
        return ""

    text = str(text)

    # Remove HTML tags
    text = re.sub(r"<.*?>", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def lemmatize_text(text):
    """Tokenize and lemmatize text using spaCy."""
    if not text:
        return ""

    doc = nlp(text)

    # Preserve negation words because they affect sentiment
    preserve_words = {"not", "no", "never", "nor"}

    tokens = [
        token.lemma_
        for token in doc
        if not token.is_space
        and (not token.is_stop or token.text in preserve_words)
        and token.is_alpha
    ]

    return " ".join(tokens)


def preprocess_dataset(file_path):
    """Load a CSV dataset and create cleaned and processed review columns."""
    df = pd.read_csv(file_path, low_memory=False)

    possible_columns = [
        "review_text",
        "reviews.text",
        "review",
        "reviews",
        "Review Text",
        "Text"
    ]

    review_column = None

    for column in possible_columns:
        if column in df.columns:
            review_column = column
            break

    if review_column is None:
        raise ValueError(
            "Review column not found. Available columns: "
            + str(list(df.columns))
        )

    # Clean reviews
    df["clean_review"] = df[review_column].apply(clean_text)

    # Tokenize and lemmatize using spaCy
    df["processed_review"] = df["clean_review"].apply(lemmatize_text)

    return df


if __name__ == "__main__":
    df = preprocess_dataset("data/1429_1.csv")

    print(df[["reviews.text", "clean_review", "processed_review"]].head())