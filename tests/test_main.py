from fastapi.testclient import TestClient
from app.main import app
import pytest
from starlette.websockets import WebSocketDisconnect

client = TestClient(app)

def test_health_check():
    '''Test the health check endpoint'''
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}

def test_get_token():
    '''Test the token endpoint'''
    response = client.get('/auth/token')
    assert response.status_code == 200
    assert response.json() == {'token': 'static-token'}

def test_websocket_streaming():
    '''Test the websocket streaming endpoint'''
    with client.websocket_connect('/ws?token=static-token') as websocket:
        websocket.send_text('Hello')
        
        # Check for asset message
        asset_message = websocket.receive_json()
        assert asset_message['type'] == 'asset'
        assert asset_message['url'] == 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/attachments/gen-images/public/ai-assistant-robot-l1IAF9CkiQVhKrbSIUu6IP1eBboy1C.png'

        # Check for text chunks
        full_text = ''
        while True:
            message = websocket.receive_json()
            if message['type'] == 'stream_end':
                break
            assert message['type'] == 'text_chunk'
            full_text += message['chunk']
        
        assert full_text == 'Hello, world! This is a streamed message.'


def test_websocket_invalid_token():
    '''Test that the websocket rejects connections with an invalid token'''
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/ws?token=invalid') as websocket:
            websocket.receive_text()

def test_websocket_no_token():
    '''Test that the websocket rejects connections with no token'''
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/ws') as websocket:
            websocket.receive_text()

