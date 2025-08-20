from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    '''Test the health check endpoint'''
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_websocket_endpoint():
    '''Test the websocket endpoint'''
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello, world!")
        data = websocket.receive_text()
        assert data == "Message text was: Hello, world!"
