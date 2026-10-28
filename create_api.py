from pathlib import Path

FILES = {
    "backend/app/api/__init__.py": "",

    "backend/app/api/health.py": '''from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["System"])

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Anato3D API",
        "version": "0.1.0"
    }
''',

    "backend/app/api/studies.py": '''from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/studies", tags=["Studies"])

BASE_DATA = Path(__file__).resolve().parent.parent.parent.parent / "data"

@router.get("/current")
def get_current_study():
    isotropic_volume = BASE_DATA / "isotropic_volume.nii.gz"
    left_mesh = BASE_DATA / "refined_meshes" / "kidney_left_refined.stl"
    if not left_mesh.exists():
        left_mesh = BASE_DATA / "meshes" / "kidney_left.stl"
        
    right_mesh = BASE_DATA / "refined_meshes" / "kidney_right_refined.stl"
    if not right_mesh.exists():
        right_mesh = BASE_DATA / "meshes" / "kidney_right.stl"

    report = BASE_DATA / "reports" / "validation_report.json"

    return {
        "study_id": "demo-study",
        "modality": "CT",
        "status": "completed",
        "outputs": {
            "volume": isotropic_volume.exists(),
            "left_kidney_mesh": left_mesh.exists(),
            "right_kidney_mesh": right_mesh.exists(),
            "validation_report": report.exists()
        }
    }
''',

    "backend/app/main.py": '''from fastapi import FastAPI
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
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nFastAPI Backend setup complete!")