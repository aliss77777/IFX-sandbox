import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

debug = bool(os.getenv("DEBUG", False))

app = FastAPI(
    title='Docker Template',
    version='1.0',
    description='Docker Template with FastAPI',
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Your existing endpoints
@app.get('/')
async def home():
    return {'message': 'Home'}

if debug:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("VS Code debugger is ready to be attached, press F5 in VS Code...")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('server:app', host='0.0.0.0', port=8000, reload=True)
