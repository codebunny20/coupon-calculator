from decimal import Decimal

from app import app, calculate_multibuy


def test_index_has_compact_basic_calculator_widget():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'basic calculator' in html.lower()
    assert 'normal-calculator-modal' in html
    assert 'normal-calculator-history' in html


def test_buy_x_get_y_free_deal():
    form = {
        "unit_price": "2.99",
        "quantity": "6",
        "deal_type": "buy_x_get_y_free",
        "buy_qty": "2",
        "free_qty": "1",
    }

    result, error = calculate_multibuy(form)

    assert error is None
    assert result["regular_total"] == Decimal("17.94")
    assert result["deal_total"] == Decimal("11.96")
    assert result["savings"] == Decimal("5.98")
    assert result["effective_unit_price"] == Decimal("1.99")


def test_x_for_y_items_deal():
    form = {
        "unit_price": "2.99",
        "quantity": "5",
        "deal_type": "x_for_y_items",
        "bundle_size": "3",
        "pay_for_qty": "2",
    }

    result, error = calculate_multibuy(form)

    assert error is None
    assert result["regular_total"] == Decimal("14.95")
    assert result["deal_total"] == Decimal("11.96")
    assert result["savings"] == Decimal("2.99")
    assert result["effective_unit_price"] == Decimal("2.39")


def test_x_for_fixed_price_deal():
    form = {
        "unit_price": "2.99",
        "quantity": "5",
        "deal_type": "x_for_fixed_price",
        "bundle_size": "2",
        "bundle_price": "5.00",
    }

    result, error = calculate_multibuy(form)

    assert error is None
    assert result["regular_total"] == Decimal("14.95")
    assert result["deal_total"] == Decimal("12.99")
    assert result["savings"] == Decimal("1.96")
    assert result["effective_unit_price"] == Decimal("2.60")
