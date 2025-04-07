import uvicorn
from fastapi.staticfiles import StaticFiles
from api import app

# Mount the static React files
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)