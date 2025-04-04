import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("APP_PORT"))
    # logger.info(f"Starting Service Image retriever {host}:{port}")
    uvicorn.run(app, host=host, port=port)
