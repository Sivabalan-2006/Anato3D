from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.studies import router as studies_router

app = FastAPI(
    title="Anato3D API",
    description="Patient-specific 3D anatomical reconstruction from DICOM imaging data",
    version="0.1.0"
)

# Allow React frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(studies_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Anato3D",
        "status": "running"
    }
