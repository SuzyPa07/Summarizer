import pandas as pd
import re


def clean_text(text):
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


def preprocess_dataset(file_path):
    df = pd.read_csv(file_path)

    # Review column names used by our datasets
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

    # Create one common review column
    df["clean_review"] = df[review_column].apply(clean_text)

    return df

if __name__ == "__main__":

    from app.preprocessing import preprocess_dataset

    df = preprocess_dataset("data/1429_1.csv")

    print(df[["reviews.text", "clean_review"]].head())