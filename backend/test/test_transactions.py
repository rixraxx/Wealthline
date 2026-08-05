from fastapi.testclient import TestClient

def test_filter_transactions_by_search_and_dates(client: TestClient, auth_headers: dict):
    """Test searching transactions by keyword and date window."""
    acc_res = client.post(
        "/api/v1/accounts",
        json={"name": "Checking", "type": "CHECKING", "balance": "1000.00", "currency": "USD"},
        headers=auth_headers,
    )
    account_id = acc_res.json()["id"]

    # Create two transactions
    client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "amount": "45.00",
            "type": "EXPENSE",
            "description": "Organic Trader Joes Groceries",
            "transaction_date": "2026-08-01T12:00:00Z",
        },
        headers=auth_headers,
    )
    client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "amount": "120.00",
            "type": "EXPENSE",
            "description": "Electric Utility Bill",
            "transaction_date": "2026-08-05T12:00:00Z",
        },
        headers=auth_headers,
    )

    # Search query
    search_res = client.get("/api/v1/transactions?search=trader", headers=auth_headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data) == 1
    assert "Trader" in search_data[0]["description"]

    # Date range query
    date_res = client.get(
        "/api/v1/transactions?start_date=2026-08-04&end_date=2026-08-06",
        headers=auth_headers,
    )
    assert date_res.status_code == 200
    date_data = date_res.json()
    assert len(date_data) == 1
    assert "Electric" in date_data[0]["description"]


def test_transactions_pagination(client: TestClient, auth_headers: dict):
    """Test pagination skip and limit controls."""
    acc_res = client.post(
        "/api/v1/accounts",
        json={"name": "Wallet", "type": "CASH", "balance": "500.00", "currency": "USD"},
        headers=auth_headers,
    )
    account_id = acc_res.json()["id"]

    for i in range(5):
        client.post(
            "/api/v1/transactions",
            json={
                "account_id": account_id,
                "amount": f"{10 + i}.00",
                "type": "EXPENSE",
                "description": f"Item {i}",
                "transaction_date": "2026-08-01T12:00:00Z",
            },
            headers=auth_headers,
        )

    # Limit to 2 items
    page1 = client.get("/api/v1/transactions?skip=0&limit=2", headers=auth_headers).json()
    assert len(page1) == 2

    # Skip 2 items
    page2 = client.get("/api/v1/transactions?skip=2&limit=2", headers=auth_headers).json()
    assert len(page2) == 2
    assert page1[0]["id"] != page2[0]["id"]