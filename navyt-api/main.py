from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import search, downloads
import os

load_dotenv()

app = FastAPI(title="Navyt API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])

@app.get("/api/health")
def health():
    return {"status": "ok"}