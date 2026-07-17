import pytest

from pricing import member_price, add_gst, delivery_fee, loyalty_points


def test_member_price_normal_discount():
    assert member_price(1000, 10) == pytest.approx(900.0)


def test_member_price_zero_discount():
    assert member_price(1000, 0) == pytest.approx(1000.0)


def test_member_price_full_discount():
    assert member_price(1000, 100) == pytest.approx(0.0)


def test_add_gst_default_rate():
    assert add_gst(1000) == pytest.approx(1050.0)


def test_add_gst_custom_rate():
    assert add_gst(1000, 18) == pytest.approx(1180.0)


def test_add_gst_zero_rate():
    assert add_gst(1000, 0) == pytest.approx(1000.0)


def test_delivery_fee_below_threshold():
    assert delivery_fee(300) == 40


def test_delivery_fee_at_threshold_boundary():
    assert delivery_fee(500) == 0


def test_delivery_fee_above_threshold():
    assert delivery_fee(600) == 0


def test_delivery_fee_custom_threshold_and_fee():
    assert delivery_fee(order_total=750, free_above=1000, flat=60) == 60


def test_loyalty_points_normal_amount():
    assert loyalty_points(950) == 9


def test_loyalty_points_exact_hundred():
    assert loyalty_points(1000) == 10


def test_loyalty_points_below_hundred():
    assert loyalty_points(99) == 0


def test_loyalty_points_zero_amount():
    assert loyalty_points(0) == 0