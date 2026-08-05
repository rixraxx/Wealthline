from datetime import datetime, timezone
from fastapi.testclient import TestClient


def test_cash_flow_summary(client: TestClient, auth_headers: dict):
    # Setup account
    acc = client.post(
        "/api/v1/accounts",
        json={"name": "Bank", "type": "CHECKING", "balance": "1000.00", "currency": "USD"},
        headers=auth_headers,
    ).json()

    # Add Income ($2000)
    client.post(
        "/api/v1/transactions",
        json={
            "account_id": acc["id"],
            "amount": "2000.00",
            "type": "INCOME",
            "transaction_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )

    # Add Expense ($500)
    client.post(
        "/api/v1/transactions",
        json={
            "account_id": acc["id"],
            "amount": "500.00",
            "type": "EXPENSE",
            "transaction_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=auth_headers,
    )

    res = client.get("/api/v1/analytics/cash-flow", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_income"] == "2000.00"
    assert data["total_expense"] == "500.00"
    assert data["net_cash_flow"] == "1500.00"