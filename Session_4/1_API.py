import requests


BASE_URL = "https://openlibrary.org/search.json"


def get_books(subject, page):
    """
    Call the Open Library search API and return a list of book dictionaries.

    Each returned book contains:
    - title
    - author
    - first_publish_year
    - rating
    """

    params = {
        "q": subject,
        "page": page,
        "limit": 10,
        "fields": "title,author_name,first_publish_year,ratings_average",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10, verify=False)
        response.raise_for_status()

        data = response.json()
        books = data.get("docs", [])

        cleaned_books = []

        for book in books:
            authors = book.get("author_name", [])

            cleaned_books.append(
                {
                    "title": book.get("title", "Unknown title"),
                    "author": ", ".join(authors) if authors else "Unknown author",
                    "first_publish_year": book.get("first_publish_year"),
                    "rating": book.get("ratings_average"),
                }
            )

        return cleaned_books

    except requests.exceptions.RequestException as error:
        print(f"API request failed: {error}")
        return []


if __name__ == "__main__":
    books = get_books("python", 1)

    for book in books[:5]:
        print(book)