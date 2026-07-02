import logging

from loafly.models import Order

logger = logging.getLogger(__name__)


def clean_price(text):
    return float(text.replace(",", "").strip())


def apply_discount(price, percent):
    return price - price * percent / 100


def build_orders(rows):
    orders = {}

    for row in rows:
        oid = row["order_id"]

        if oid not in orders:
            orders[oid] = Order(
                order_id=oid,
                customer=row["customer"]
            )

        try:
            price = clean_price(row["item_price"])
        except ValueError:
            logger.warning(
                "Skipping item with missing or invalid price: order_id=%s item=%s",
                oid,
                row["item_name"]
            )
            continue
        finally:
            logger.info(
                "Checked price for order_id=%s item=%s",
                oid,
                row["item_name"]
            )

        orders[oid].add_item(row["item_name"], price)

    return orders