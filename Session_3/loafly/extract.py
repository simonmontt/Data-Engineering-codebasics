import csv
import logging

logger = logging.getLogger(__name__)


def read_raw_orders(path):
    logger.info("Reading raw orders from %s", path)

    rows = []

    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    logger.info("Read %s raw order rows", len(rows))

    return rows