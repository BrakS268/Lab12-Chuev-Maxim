import pytest
from fastapi.testclient import TestClient
from main import app, tutors_db, _next_id
import main


@pytest.fixture(autouse=True)
def clear_db():
    """Очищает in-memory БД перед каждым тестом."""
    tutors_db.clear()
    main._next_id = 1
    yield
    tutors_db.clear()
    main._next_id = 1


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_tutor_data():
    return {
        "full_name": "Иванов Иван Иванович",
        "email": "ivanov@example.com",
        "subject": "Математика",
        "hourly_rate": 1500.0,
        "experience_years": 5,
        "education": "МГУ, математический факультет, 2015",
        "bio": "Опытный репетитор по математике и физике",
        "is_active": True,
    }



def test_create_tutor_success(client, sample_tutor_data):
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["full_name"] == sample_tutor_data["full_name"]
    assert data["subject"] == "Математика"
    assert data["hourly_rate"] == 1500.0


def test_create_tutor_without_optional_bio(client, sample_tutor_data):
    sample_tutor_data.pop("bio")
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 201
    assert response.json()["bio"] is None


def test_create_tutor_invalid_negative_rate(client, sample_tutor_data):
    sample_tutor_data["hourly_rate"] = -100
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 422


def test_create_tutor_invalid_experience(client, sample_tutor_data):
    sample_tutor_data["experience_years"] = 99
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 422


def test_create_tutor_empty_name(client, sample_tutor_data):
    sample_tutor_data["full_name"] = ""
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 422


def test_create_tutor_missing_required_field(client, sample_tutor_data):
    del sample_tutor_data["subject"]
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 422



def test_get_all_tutors_empty(client):
    response = client.get("/tutors")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_tutors_with_data(client, sample_tutor_data):
    client.post("/tutors", json=sample_tutor_data)
    client.post("/tutors", json={**sample_tutor_data, "email": "other@example.com"})
    response = client.get("/tutors")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_tutor_by_id_success(client, sample_tutor_data):
    client.post("/tutors", json=sample_tutor_data)
    response = client.get("/tutors/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["full_name"] == sample_tutor_data["full_name"]


def test_get_tutor_not_found(client):
    response = client.get("/tutors/999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]



def test_update_tutor_partial(client, sample_tutor_data):
    client.post("/tutors", json=sample_tutor_data)
    response = client.put("/tutors/1", json={"hourly_rate": 2000.0})
    assert response.status_code == 200
    assert response.json()["hourly_rate"] == 2000.0
    assert response.json()["full_name"] == sample_tutor_data["full_name"]  # не изменилось


def test_update_tutor_full(client, sample_tutor_data):
    client.post("/tutors", json=sample_tutor_data)
    update = {"full_name": "Петров Пётр Петрович", "subject": "Физика", "hourly_rate": 1800.0}
    response = client.put("/tutors/1", json=update)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Петров Пётр Петрович"
    assert response.json()["subject"] == "Физика"


def test_update_tutor_not_found(client):
    response = client.put("/tutors/999", json={"hourly_rate": 2000.0})
    assert response.status_code == 404


def test_update_tutor_invalid_rate(client, sample_tutor_data):
    client.post("/tutors", json=sample_tutor_data)
    response = client.put("/tutors/1", json={"hourly_rate": -500})
    assert response.status_code == 422



def test_delete_tutor_success(client, sample_tutor_data):
    client.post("/tutors", json=sample_tutor_data)
    response = client.delete("/tutors/1")
    assert response.status_code == 204
    assert client.get("/tutors/1").status_code == 404


def test_delete_tutor_not_found(client):
    response = client.delete("/tutors/999")
    assert response.status_code == 404


def test_delete_tutor_removes_from_list(client, sample_tutor_data):
    client.post("/tutors", json=sample_tutor_data)
    client.delete("/tutors/1")
    response = client.get("/tutors")
    assert response.json() == []



def test_ids_increment_correctly(client, sample_tutor_data):
    r1 = client.post("/tutors", json=sample_tutor_data)
    r2 = client.post("/tutors", json={**sample_tutor_data, "email": "b@b.com"})
    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


def test_zero_hourly_rate_allowed(client, sample_tutor_data):
    sample_tutor_data["hourly_rate"] = 0.0
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 201


def test_zero_experience_allowed(client, sample_tutor_data):
    sample_tutor_data["experience_years"] = 0
    response = client.post("/tutors", json=sample_tutor_data)
    assert response.status_code == 201
    