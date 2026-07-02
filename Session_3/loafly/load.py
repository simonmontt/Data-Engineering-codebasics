import logging
import time

from gateway import save_to_orders_api
from loafly.transform import apply_discount

logger = logging.getLogger(__name__)


def save_order_with_retry(order_id, total, retry_count, retry_wait_seconds):
    for attempt in range(1, retry_count + 1):
        try:
            response = save_to_orders_api(order_id, total)
            logger.info("Saved order_id=%s successfully: %s", order_id, response)
            return True
        except ConnectionError as error:
            logger.warning(
                "Attempt %s/%s failed for order_id=%s: %s",
                attempt,
                retry_count,
                order_id,
                error,
            )

            if attempt < retry_count:
                time.sleep(retry_wait_seconds)

    logger.error("Giving up on order_id=%s after %s attempts", order_id, retry_count)
    return False


def save_orders(orders, discount_percent, retry_count, retry_wait_seconds, api_key):
    logger.info("API key loaded from environment")

    for order in orders.values():
        total = apply_discount(order.total(), discount_percent)

        logger.info(
            "Saving order_id=%s customer=%s total=%s",
            order.order_id,
            order.customer,
            total,
        )

        save_order_with_retry(
            order_id=order.order_id,
            total=total,
            retry_count=retry_count,
            retry_wait_seconds=retry_wait_seconds,
        )