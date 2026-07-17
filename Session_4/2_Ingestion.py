import requests
import urllib3


BASE_URL = "https://openlibrary.org/search.json"

# Only use this workaround if your environment has corporate/self-signed SSL issues.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_books(subject, page, limit=10):
    """
    Call the Open Library search API and return a list of cleaned book dictionaries.
    """

    params = {
        "q": subject,
        "page": page,
        "limit": limit,
        "fields": "title,author_name,first_publish_year,ratings_average",
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10,
            verify=False,  # Use True in normal environments
        )

        response.raise_for_status()
        data = response.json()

        docs = data.get("docs", [])

        books = []

        for book in docs:
            authors = book.get("author_name", [])

            books.append(
                {
                    "title": book.get("title", "Unknown title"),
                    "author": ", ".join(authors) if authors else "Unknown author",
                    "first_publish_year": book.get("first_publish_year"),
                    "rating": book.get("ratings_average"),
                }
            )

        return books

    except requests.exceptions.RequestException as error:
        print(f"API request failed on page {page}: {error}")
        return []


def full_load_books(subject, page_cap=5):
    """
    Pull books page by page until an empty page is returned or page_cap is reached.
    """

    all_books = []

    for page in range(1, page_cap + 1):
        books = get_books(subject, page)

        if not books:
            print(f"Stopping at page {page}: no books returned.")
            break

        all_books.extend(books)
        print(f"Loaded page {page}: {len(books)} books")

    return all_books


def get_watermark(books):
    """
    Return the newest first_publish_year from the books loaded.
    """

    publish_years = [
        book["first_publish_year"]
        for book in books
        if book.get("first_publish_year") is not None
    ]

    if not publish_years:
        return None

    return max(publish_years)


def incremental_load_books(subject, watermark, page_cap=5):
    """
    Pull pages again, but keep only books newer than the previous watermark.
    """

    new_books = []

    for page in range(1, page_cap + 1):
        books = get_books(subject, page)

        if not books:
            print(f"Stopping incremental load at page {page}: no books returned.")
            break

        books_newer_than_watermark = [
            book
            for book in books
            if book.get("first_publish_year") is not None
            and book["first_publish_year"] > watermark
        ]

        new_books.extend(books_newer_than_watermark)

        print(
            f"Checked page {page}: "
            f"{len(books_newer_than_watermark)} new books found"
        )

    return new_books


if __name__ == "__main__":
    subject = "python"
    page_cap = 5

    print("FULL LOAD")
    full_books = full_load_books(subject, page_cap=page_cap)

    print(f"\nFull load count: {len(full_books)}")

    watermark = get_watermark(full_books)
    print(f"Watermark, newest publish year seen: {watermark}")

    print("\nINCREMENTAL LOAD")
    incremental_books = incremental_load_books(
        subject=subject,
        watermark=watermark,
        page_cap=page_cap,
    )

    print(f"\nIncremental load count: {len(incremental_books)}")

    print("\nSample incremental books:")
    for book in incremental_books[:5]:
        print(book)