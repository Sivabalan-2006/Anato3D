from pathlib import Path

from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["System"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def check_file(path: Path):
    return {
        "available": path.exists(),
        "path": str(path),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


@router.get("/health")
def health_check():
    volume = DATA_DIR / "isotropic_volume.nii.gz"

    left_segmentation = (
        DATA_DIR / "segmentations" / "kidney_left.nii.gz"
    )

    right_segmentation = (
        DATA_DIR / "segmentations" / "kidney_right.nii.gz"
    )

    left_mesh = (
        DATA_DIR / "meshes" / "kidney_left.stl"
    )

    right_mesh = (
        DATA_DIR / "meshes" / "kidney_right.stl"
    )

    validation = (
        DATA_DIR / "reports" / "validation_report.json"
    )

    components = {
        "volume": check_file(volume),
        "left_segmentation": check_file(left_segmentation),
        "right_segmentation": check_file(right_segmentation),
        "left_mesh": check_file(left_mesh),
        "right_mesh": check_file(right_mesh),
        "validation_report": check_file(validation),
    }

    all_available = all(
        item["available"]
        for item in components.values()
    )

    return {
        "status": "ok" if all_available else "incomplete",
        "service": "Anato3D API",
        "version": "0.1.0",
        "pipeline_complete": all_available,
        "components": components,
    }