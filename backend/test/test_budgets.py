from datetime import date
from fastapi.testclient import TestClient


def test_create_budget(client: TestClient, auth_headers: dict):
    """Test creating a category-linked budget."""
    # Create category first
    cat_res = client.post(
        "/api/v1/categories",
        json={"name": "Groceries", "type": "EXPENSE", "icon": "cart", "color": "#00FF00"},
        headers=auth_headers,
    )
    cat_id = cat_res.json()["id"]

    payload = {
        "category_id": cat_id,
        "amount": "500.00",
        "start_date": "2026-08-01",
        "end_date": "2026-08-31",
    }
    response = client.post("/api/v1/budgets", json=payload, headers=auth_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["amount"] == "500.00"
    assert data["category_id"] == cat_id
    assert "id" in data


def test_list_budgets(client: TestClient, auth_headers: dict):
    """Test retrieving active budgets for the user."""
    client.post(
        "/api/v1/budgets",
        json={
            "category_id": None,
            "amount": "1000.00",
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
        },
        headers=auth_headers,
    )

    response = client.get("/api/v1/budgets", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_budget(client: TestClient, auth_headers: dict):
    """Test retrieving a specific budget by ID."""
    create_res = client.post(
        "/api/v1/budgets",
        json={
            "category_id": None,
            "amount": "750.00",
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
        },
        headers=auth_headers,
    )
    budget_id = create_res.json()["id"]

    response = client.get(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["amount"] == "750.00"


def test_update_budget(client: TestClient, auth_headers: dict):
    """Test updating budget amount and date window."""
    create_res = client.post(
        "/api/v1/budgets",
        json={
            "category_id": None,
            "amount": "300.00",
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
        },
        headers=auth_headers,
    )
    budget_id = create_res.json()["id"]

    update_res = client.patch(
        f"/api/v1/budgets/{budget_id}",
        json={"amount": "450.00"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["amount"] == "450.00"


def test_delete_budget(client: TestClient, auth_headers: dict):
    """Test deleting a budget."""
    create_res = client.post(
        "/api/v1/budgets",
        json={
            "category_id": None,
            "amount": "200.00",
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
        },
        headers=auth_headers,
    )
    budget_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert get_res.status_code == 404