import os
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

import pandas as pd


SALES_FILE = Path("sales.csv")

# Increase this if the serial/parallel difference is too small on your machine.
CPU_WORK = 15_000_000


def build_genre_payloads(csv_path):
    """
    Read sales.csv and prepare one payload per genre.

    Each payload contains:
    - genre name
    - rows belonging to that genre
    - amount of artificial CPU work
    """

    df = pd.read_csv(csv_path)

    payloads = []

    for genre, group in df.groupby("genre"):
        rows = list(
            zip(
                group["price"],
                group["quantity"],
                group["rating"],
            )
        )

        payloads.append(
            {
                "genre": genre,
                "rows": rows,
                "cpu_work": CPU_WORK,
            }
        )

    return payloads


def score_genre(payload):
    """
    CPU-heavy scoring function for one genre.

    The real business part calculates revenue, quantity and weighted rating.
    The artificial loop makes the job CPU-heavy enough to compare
    serial versus parallel execution.
    """

    genre = payload["genre"]
    rows = payload["rows"]
    cpu_work = payload["cpu_work"]

    total_revenue = 0.0
    total_quantity = 0
    weighted_rating_sum = 0.0

    for price, quantity, rating in rows:
        line_revenue = float(price) * int(quantity)

        total_revenue += line_revenue
        total_quantity += int(quantity)
        weighted_rating_sum += float(rating) * line_revenue

    if total_revenue == 0:
        average_rating = 0.0
    else:
        average_rating = weighted_rating_sum / total_revenue

    # Deterministic CPU-heavy loop.
    # This simulates an expensive scoring calculation.
    seed = int(total_revenue * 100) + int(average_rating * 1000) + total_quantity

    accumulator = 0

    for i in range(cpu_work):
        accumulator += ((seed + i) * (i % 97)) % 1_000_003

    final_score = (
        total_revenue * 0.001
        + average_rating * 100
        + total_quantity * 0.1
        + accumulator % 10_000
    )

    return {
        "genre": genre,
        "score": round(final_score, 2),
        "total_revenue": round(total_revenue, 2),
        "total_quantity": total_quantity,
        "average_rating": round(average_rating, 4),
    }


def run_serial(payloads):
    """
    Run the scoring job one genre at a time.
    """

    results = []

    for payload in payloads:
        result = score_genre(payload)
        results.append(result)

    return results


def run_parallel(payloads):
    """
    Run the scoring job across CPU cores with ProcessPoolExecutor.
    """

    with ProcessPoolExecutor() as pool:
        results = list(pool.map(score_genre, payloads))

    return results


def sort_results(results):
    """
    Sort results so serial and parallel outputs can be compared reliably.
    """

    return sorted(results, key=lambda row: row["genre"])


if __name__ == "__main__":
    core_count = os.cpu_count()

    print(f"Machine core count: {core_count}")
    print(f"CPU work per genre: {CPU_WORK:,} loop iterations")

    payloads = build_genre_payloads(SALES_FILE)

    print(f"Genres found: {len(payloads)}")

    print("\nSERIAL VERSION")
    serial_start = time.perf_counter()

    serial_results = run_serial(payloads)

    serial_end = time.perf_counter()
    serial_time = serial_end - serial_start

    print(f"Serial time: {serial_time:.2f} seconds")

    print("\nPARALLEL VERSION")
    parallel_start = time.perf_counter()

    parallel_results = run_parallel(payloads)

    parallel_end = time.perf_counter()
    parallel_time = parallel_end - parallel_start

    print(f"Parallel time: {parallel_time:.2f} seconds")

    serial_sorted = sort_results(serial_results)
    parallel_sorted = sort_results(parallel_results)

    results_match = serial_sorted == parallel_sorted

    print(f"\nResults match: {results_match}")

    if not results_match:
        raise AssertionError("Serial and parallel results do not match.")

    if parallel_time > 0:
        speedup = serial_time / parallel_time
        print(f"Speedup: {speedup:.2f}x")

    print("\nSample results:")
    for row in serial_sorted:
        print(row)