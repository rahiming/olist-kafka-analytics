import pandas as pd

from producer.producer import build_orders_dataframe, row_to_message


def test_build_orders_dataframe_filters_and_aggregates():
    orders = pd.DataFrame(
        [
            {
                "order_id": "o1",
                "customer_id": "c1",
                "order_status": "delivered",
                "order_purchase_timestamp": "2017-10-02 10:56:33",
            },
            {
                "order_id": "o2",
                "customer_id": "c2",
                "order_status": "canceled",
                "order_purchase_timestamp": "2017-10-02 11:56:33",
            },
        ]
    )
    items = pd.DataFrame(
        [
            {
                "order_id": "o1",
                "product_id": "p1",
                "price": 10.0,
                "freight_value": 1.0,
            },
            {
                "order_id": "o1",
                "product_id": "p2",
                "price": 20.0,
                "freight_value": 2.0,
            },
            {
                "order_id": "o2",
                "product_id": "p3",
                "price": 99.0,
                "freight_value": 9.0,
            },
        ]
    )
    products = pd.DataFrame(
        [
            {"product_id": "p1", "product_category_name": "books"},
            {"product_id": "p2", "product_category_name": None},
            {"product_id": "p3", "product_category_name": "games"},
        ]
    )

    result = build_orders_dataframe(orders, items, products)

    assert list(result["order_id"]) == ["o1"]
    assert result.iloc[0]["price"] == 30.0
    assert result.iloc[0]["freight_value"] == 3.0
    assert result.iloc[0]["total"] == 33.0
    assert result.iloc[0]["product_category_name"] == "books"


def test_row_to_message_rounds_numeric_fields():
    row = pd.Series(
        {
            "order_id": "o1",
            "customer_id": "c1",
            "order_status": "delivered",
            "product_category_name": "books",
            "price": 10.456,
            "freight_value": 1.239,
            "total": 11.695,
            "order_purchase_timestamp": "2017-10-02 10:56:33",
        }
    )

    message = row_to_message(row)

    assert message == {
        "order_id": "o1",
        "customer_id": "c1",
        "status": "delivered",
        "category": "books",
        "price": 10.46,
        "freight": 1.24,
        "total": 11.7,
        "timestamp": "2017-10-02 10:56:33",
    }
