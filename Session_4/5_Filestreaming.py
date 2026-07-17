from pathlib import Path

import pandas as pd


SALES_FILE = Path("sales.csv")
CHUNK_SIZE = 50_000


def bytes_to_mb(size_in_bytes):
    """
    Convert bytes to megabytes for easier reporting.
    """

    return size_in_bytes / (1024 * 1024)


def stream_revenue_by_genre(csv_path, chunksize):
    """
    Stream sales.csv in chunks and calculate total revenue by genre.

    Revenue = price * quantity

    The full CSV is never loaded into memory.
    Only one chunk is processed at a time.
    """

    total_revenue_by_genre = pd.Series(dtype="float64")

    for chunk_number, chunk in enumerate(
        pd.read_csv(csv_path, chunksize=chunksize),
        start=1,
    ):
        chunk["revenue"] = chunk["price"] * chunk["quantity"]

        chunk_revenue_by_genre = chunk.groupby("genre")["revenue"].sum()

        total_revenue_by_genre = total_revenue_by_genre.add(
            chunk_revenue_by_genre,
            fill_value=0,
        )

        print(f"Processed chunk {chunk_number}: {len(chunk)} rows")

    return total_revenue_by_genre.sort_values(ascending=False)


def optimise_chunk_memory(chunk):
    """
    Shrink memory usage for one DataFrame chunk.

    Optimisations:
    - price and rating: float64 -> float32
    - genre, city, payment_type: object -> category
    """

    optimised_chunk = chunk.copy()

    optimised_chunk["price"] = optimised_chunk["price"].astype("float32")
    optimised_chunk["rating"] = optimised_chunk["rating"].astype("float32")

    optimised_chunk["genre"] = optimised_chunk["genre"].astype("category")
    optimised_chunk["city"] = optimised_chunk["city"].astype("category")
    optimised_chunk["payment_type"] = optimised_chunk["payment_type"].astype("category")

    return optimised_chunk


def report_memory_usage(before_chunk, after_chunk):
    """
    Print memory usage before and after dtype optimisation.
    """

    memory_before = before_chunk.memory_usage(deep=True).sum()
    memory_after = after_chunk.memory_usage(deep=True).sum()

    reduction = memory_before - memory_after
    reduction_percent = (reduction / memory_before) * 100

    print("\nMEMORY USAGE BY COLUMN BEFORE:")
    print(before_chunk.memory_usage(deep=True))

    print("\nMEMORY USAGE BY COLUMN AFTER:")
    print(after_chunk.memory_usage(deep=True))

    print("\nMEMORY SUMMARY")
    print(f"Before: {bytes_to_mb(memory_before):.2f} MB")
    print(f"After:  {bytes_to_mb(memory_after):.2f} MB")
    print(f"Saved:  {bytes_to_mb(reduction):.2f} MB")
    print(f"Reduction: {reduction_percent:.2f}%")


if __name__ == "__main__":
    print("CHUNKED REVENUE BY GENRE")
    revenue_by_genre = stream_revenue_by_genre(
        csv_path=SALES_FILE,
        chunksize=CHUNK_SIZE,
    )

    print("\nTOTAL REVENUE BY GENRE")
    print(revenue_by_genre)

    print("\nMEMORY OPTIMISATION ON ONE CHUNK")
    first_chunk = pd.read_csv(SALES_FILE, nrows=CHUNK_SIZE)

    optimised_first_chunk = optimise_chunk_memory(first_chunk)

    report_memory_usage(
        before_chunk=first_chunk,
        after_chunk=optimised_first_chunk,
    )