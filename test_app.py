
from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "application": "virtual-mouse-keyboard",
    }


def test_homepage():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"Virtual Mouse" in response.data
