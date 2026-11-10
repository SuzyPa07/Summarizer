from app.database import get_db_connection

try:
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM customer_reviews;")
    reviews = cursor.fetchall()

    print("Reviews fetched successfully!")
    print("Total reviews:", len(reviews))

    for review in reviews:
        print(review)

    cursor.close()
    connection.close()

except Exception as error:
    print("Database query failed:")
    print(error)