from fastapi.testclient import TestClient


def test_create_account(client: TestClient, auth_headers: dict):
    """Test creating a new checking account."""
    payload = {
        "name": "Chase Checking",
        "type": "CHECKING",
        "balance": "1000.00",
        "currency": "USD"
    }
    response = client.post("/api/v1/accounts", json=payload, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chase Checking"
    assert float(data["balance"]) == 1000.00
    assert "id" in data


def test_list_accounts(client: TestClient, auth_headers: dict):
    """Test retrieving active accounts for the user."""
    payload = {"name": "Savings", "type": "SAVINGS", "balance": "500.00", "currency": "USD"}
    client.post("/api/v1/accounts", json=payload, headers=auth_headers)

    response = client.get("/api/v1/accounts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Savings"


def test_update_account(client: TestClient, auth_headers: dict):
    """Test patching an existing account's name and balance."""
    create_res = client.post(
        "/api/v1/accounts", 
        json={"name": "Old Name", "type": "CHECKING", "balance": "100.00", "currency": "USD"}, 
        headers=auth_headers
    )
    account_id = create_res.json()["id"]

    update_res = client.patch(
        f"/api/v1/accounts/{account_id}", 
        json={"name": "New Name", "balance": "250.00"}, 
        headers=auth_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Name"
    assert float(update_res.json()["balance"]) == 250.00


def test_delete_account(client: TestClient, auth_headers: dict):
    """Test soft-deleting an account."""
    create_res = client.post(
        "/api/v1/accounts", 
        json={"name": "Temp Account", "type": "CASH", "balance": "50.00", "currency": "USD"}, 
        headers=auth_headers
    )
    account_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert del_res.status_code == 204

    list_res = client.get("/api/v1/accounts", headers=auth_headers)
    assert len(list_res.json()) == 0