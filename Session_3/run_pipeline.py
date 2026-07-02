import logging
import os

from loafly.config import (
    API_KEY_ENV_VAR,
    DISCOUNT_PERCENT,
    ENV_FILE_PATH,
    LOG_FILE_PATH,
    RAW_ORDERS_PATH,
    RETRY_COUNT,
    RETRY_WAIT_SECONDS,
)
from loafly.extract import read_raw_orders
from loafly.transform import build_orders
from loafly.load import save_orders


def configure_logging():
    logging.basicConfig(
        filename=LOG_FILE_PATH,
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )


def load_env_file(path):
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key, value)


def main():
    configure_logging()
    load_env_file(ENV_FILE_PATH)

    api_key = os.getenv(API_KEY_ENV_VAR)

    if not api_key:
        raise RuntimeError(f"Missing required environment variable: {API_KEY_ENV_VAR}")

    logging.info("Starting Loafly orders pipeline")

    rows = read_raw_orders(RAW_ORDERS_PATH)
    orders = build_orders(rows)

    save_orders(
        orders=orders,
        discount_percent=DISCOUNT_PERCENT,
        retry_count=RETRY_COUNT,
        retry_wait_seconds=RETRY_WAIT_SECONDS,
        api_key=api_key,
    )

    logging.info("Finished Loafly orders pipeline")


if __name__ == "__main__":
    main()