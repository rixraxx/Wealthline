from fastapi.testclient import TestClient


def test_create_category(client: TestClient, auth_headers: dict):
    """Test creating a custom user category."""
    payload = {
        "name": "Groceries",
        "type": "EXPENSE",
        "icon": "shopping_cart",
        "color": "#00FF00",
    }
    response = client.post("/api/v1/categories", json=payload, headers=auth_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Groceries"
    assert data["type"] == "EXPENSE"
    assert data["icon"] == "shopping_cart"
    assert data["color"] == "#00FF00"
    assert "id" in data


def test_list_categories(client: TestClient, auth_headers: dict):
    """Test listing user-accessible categories."""
    client.post(
        "/api/v1/categories",
        json={"name": "Salary", "type": "INCOME", "icon": "work", "color": "#0000FF"},
        headers=auth_headers,
    )
    client.post(
        "/api/v1/categories",
        json={"name": "Rent", "type": "EXPENSE", "icon": "home", "color": "#FF0000"},
        headers=auth_headers,
    )

    response = client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_category_by_id(client: TestClient, auth_headers: dict):
    """Test retrieving a single category by ID."""
    create_res = client.post(
        "/api/v1/categories",
        json={"name": "Utilities", "type": "EXPENSE", "icon": "bolt", "color": "#FFFF00"},
        headers=auth_headers,
    )
    category_id = create_res.json()["id"]

    response = client.get(f"/api/v1/categories/{category_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Utilities"


def test_update_category(client: TestClient, auth_headers: dict):
    """Test updating a category's name and color."""
    create_res = client.post(
        "/api/v1/categories",
        json={"name": "Dining Out", "type": "EXPENSE", "icon": "restaurant", "color": "#123456"},
        headers=auth_headers,
    )
    category_id = create_res.json()["id"]

    update_res = client.patch(
        f"/api/v1/categories/{category_id}",
        json={"name": "Restaurants & Cafes", "color": "#654321"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200

    data = update_res.json()
    assert data["name"] == "Restaurants & Cafes"
    assert data["color"] == "#654321"


def test_delete_category(client: TestClient, auth_headers: dict):
    """Test deleting a custom category."""
    create_res = client.post(
        "/api/v1/categories",
        json={"name": "Subscriptions", "type": "EXPENSE", "icon": "movie", "color": "#FF00FF"},
        headers=auth_headers,
    )
    category_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/categories/{category_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify category no longer exists
    get_res = client.get(f"/api/v1/categories/{category_id}", headers=auth_headers)
    assert get_res.status_code == 404