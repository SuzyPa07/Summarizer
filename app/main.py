from functools import lru_cache
import csv
import io

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Query
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.pipeline import analyze_review
from app.preprocessing import clean_text, lemmatize_text
from app.database import get_db_connection

from app.product_catalog import (
    get_product_catalog,
    search_products,
    get_product_reviews
)

from app.mobile_catalog import (
    get_mobile_products,
    search_mobile_products,
    get_mobile_product_reviews
)


# Application configuration
app = FastAPI(
    title="Aspect-Based E-Commerce Product Feedback Summarizer",
    description="Analyze customer reviews and generate aspect-wise sentiment summaries.",
    version="1.2"
)


# Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    product: str
    review: str
    domain: str = "electronics"


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Aspect-Based E-Commerce Product Feedback Summarizer API is running!"
    }


# Analyse one customer review
@app.post("/predict")
def predict(request: ReviewRequest):

    result = analyze_review(request.review)

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        for aspect, sentiment in result["aspects"].items():

            cursor.execute(
                """
                INSERT INTO customer_reviews
                (product_id, product_name, review_text,
                 rating, aspect, sentiment, summary)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    request.product,
                    request.product,
                    request.review,
                    None,
                    aspect,
                    sentiment,
                    result["summary"]
                )
            )

        connection.commit()

    except Exception as error:
        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database save failed: {str(error)}"
        )

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return {
        "product": request.product,
        "aspects": result["aspects"],
        "summary": result["summary"],
        "database_status": "Review saved successfully"
    }


# Upload and analyse CSV
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    contents = await file.read()

    try:
        text = contents.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        if not reader.fieldnames:
            raise ValueError("The CSV file is empty.")

        columns = {
            column.strip().lower(): column
            for column in reader.fieldnames if column
        }

        possible_columns = [
            "review_text",
            "reviews.text",
            "review",
            "reviews",
            "text"
        ]

        review_column = next(
            (
                columns[name]
                for name in possible_columns
                if name in columns
            ),
            None
        )

        if review_column is None:
            raise ValueError("Review text column not found.")

        results = []
        skipped_reviews = 0
        upload_limit = 100

        for row in reader:

            review = row.get(review_column, "")

            if not review or not review.strip():
                skipped_reviews += 1
                continue

            # Limit expensive model inference during CSV uploads
            if len(results) >= upload_limit:
                break

            # Step 1: Clean review
            cleaned_review = clean_text(review)

            # Step 2: Tokenise and lemmatise using spaCy
            processed_review = lemmatize_text(cleaned_review)

            # Step 3: Aspect extraction and RoBERTa sentiment analysis
            result = analyze_review(cleaned_review)

            results.append({
                "review": review,
                "clean_review": cleaned_review,
                "processed_review": processed_review,
                "aspects": result["aspects"],
                "summary": result["summary"]
            })

        return {
            "message": "CSV analysis completed successfully!",
            "total_reviews_analyzed": len(results),
            "upload_limit": upload_limit,
            "skipped_empty_reviews": skipped_reviews,
            "results": results
        }

    except (UnicodeDecodeError, ValueError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:
        await file.close()


# Search products across both datasets
@app.get("/products/search")
def product_search(q: str = Query(default="")):

    if not q.strip():
        return {"products": []}

    original_products = search_products(q)
    mobile_products = search_mobile_products(q)

    combined_products = original_products + mobile_products

    return {
        "products": combined_products[:20]
    }


# Get all products from both datasets
@app.get("/products")
def products_list():

    original_products = get_product_catalog()
    mobile_products = get_mobile_products()

    combined_products = original_products + mobile_products

    return {
        "total_products": len(combined_products),
        "products": combined_products
    }


# Get reviews belonging to a selected product
@app.get("/products/{product_id}/reviews")
def product_reviews(product_id: str):

    reviews = get_reviews_for_product(product_id)

    if not reviews:
        raise HTTPException(
            status_code=404,
            detail="No reviews found for this product."
        )

    return {
        "product_id": product_id,
        "total_reviews": len(reviews),
        "reviews": reviews
    }


# Get reviews from the correct dataset
def get_reviews_for_product(product_id):

    if product_id.startswith("mobile_"):
        asin = product_id.replace("mobile_", "", 1)
        return get_mobile_product_reviews(asin)

    return get_product_reviews(product_id)


# Calculate and cache overall product analysis
@lru_cache(maxsize=50)
def calculate_product_analysis(product_id):

    reviews = get_reviews_for_product(product_id)

    if not reviews:
        raise HTTPException(
            status_code=404,
            detail="No reviews found for this product."
        )

    aspect_counts = {}
    analyzed_reviews = 0

    for item in reviews:

        result = analyze_review(item["review"])
        aspects = result.get("aspects", {})

        if aspects:
            analyzed_reviews += 1

        for aspect, sentiment in aspects.items():

            if aspect == "general":
                continue

            if aspect not in aspect_counts:
                aspect_counts[aspect] = {
                    "Positive": 0,
                    "Negative": 0,
                    "Neutral": 0
                }

            if sentiment in aspect_counts[aspect]:
                aspect_counts[aspect][sentiment] += 1

    aspect_analysis = {}

    for aspect, counts in aspect_counts.items():

        total = sum(counts.values())

        if total == 0:
            continue

        percentages = {
            sentiment: round(
                (count / total) * 100, 1
            )
            for sentiment, count in counts.items()
        }

        highest = max(counts.values())

        leaders = [
            sentiment
            for sentiment, count in counts.items()
            if count == highest
        ]

        overall_sentiment = (
            leaders[0] if len(leaders) == 1 else "Mixed"
        )

        aspect_analysis[aspect] = {
            "total_mentions": total,
            "sentiment_counts": counts,
            "sentiment_percentages": percentages,
            "overall_sentiment": overall_sentiment
        }

    return {
        "product_id": product_id,
        "total_reviews": len(reviews),
        "analyzed_reviews": analyzed_reviews,
        "aspect_analysis": aspect_analysis
    }


# Overall product analysis
@app.get("/products/{product_id}/analysis")
def product_overall_analysis(product_id: str):

    return calculate_product_analysis(product_id)