import asyncio
import time
import requests
import urllib3


BASE_URL = "https://openlibrary.org/search.json"

# Set this to True if your certificates work normally.
# Keep False only if you have the corporate/self-signed SSL problem.
VERIFY_SSL = False

if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_result_count(subject):
    """
    Fetch the Open Library result count for one subject.
    Returns a dictionary with the subject and its result count.
    """

    params = {
        "q": subject,
        "page": 1,
        "limit": 1,  # We only need the count, not many book records
        "fields": "title",
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10,
            verify=VERIFY_SSL,
        )

        response.raise_for_status()
        data = response.json()

        return {
            "subject": subject,
            "count": data.get("numFound", 0),
        }

    except requests.exceptions.RequestException as error:
        print(f"Request failed for subject '{subject}': {error}")

        return {
            "subject": subject,
            "count": 0,
        }


def fetch_counts_sync(subjects):
    """
    Fetch result counts one subject at a time.
    """

    results = []

    for subject in subjects:
        result = fetch_result_count(subject)
        results.append(result)

    return results


async def fetch_counts_async(subjects):
    """
    Fetch result counts for all subjects together.

    requests.get() is blocking, so asyncio.to_thread() runs each call
    in a separate thread. asyncio.gather() waits for all calls to finish.
    """

    tasks = [
        asyncio.to_thread(fetch_result_count, subject)
        for subject in subjects
    ]

    results = await asyncio.gather(*tasks)

    return results


if __name__ == "__main__":
    subjects = [
        "python",
        "data engineering",
        "machine learning",
        "sql",
        "cloud computing",
        "algorithms",
        "statistics",
        "databases",
    ]

    print("SYNC VERSION")
    sync_start = time.perf_counter()

    sync_results = fetch_counts_sync(subjects)

    sync_end = time.perf_counter()
    sync_time = sync_end - sync_start

    for result in sync_results:
        print(f"{result['subject']}: {result['count']} books")

    print(f"\nSync time: {sync_time:.2f} seconds")

    print("\nASYNC VERSION")
    async_start = time.perf_counter()

    async_results = asyncio.run(fetch_counts_async(subjects))

    async_end = time.perf_counter()
    async_time = async_end - async_start

    for result in async_results:
        print(f"{result['subject']}: {result['count']} books")

    print(f"\nAsync time: {async_time:.2f} seconds")

    if async_time > 0:
        speedup = sync_time / async_time
        print(f"\nSpeedup: {speedup:.2f}x faster")