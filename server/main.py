from fastapi import FastAPI
import httpx
from dotenv import load_dotenv
import os



#Routes
from routes.ollama import router as ollama_router
from routes import generate, edit


load_dotenv()



app = FastAPI()

@app.get("/health")
def read_root():
    return {"message": "Backend is running"}


app.include_router(ollama_router, prefix="/ollama", tags=["ollama"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(edit.router, prefix="/api", tags=["edit"])