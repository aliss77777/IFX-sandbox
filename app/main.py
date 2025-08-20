from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio

app = FastAPI()


@app.get('/health')
def health_check():
    return {'status': 'OK'}


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Send asset message
            await websocket.send_json({
                'type': 'asset',
                'url': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/attachments/gen-images/public/ai-assistant-robot-l1IAF9CkiQVhKrbSIUu6IP1eBboy1C.png'
            })

            # Stream text chunks
            text = "Hello, world! This is a streamed message."
            for char in text:
                await websocket.send_json({
                    'type': 'text_chunk',
                    'chunk': char
                })
                await asyncio.sleep(0.05)

            # Send stream end message
            await websocket.send_json({
                'type': 'stream_end'
            })

    except WebSocketDisconnect:
        print("Client disconnected")
