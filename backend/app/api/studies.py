import json
from pathlib import Path
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import FileResponse, JSONResponse  # type: ignore
import trimesh  # type: ignore
from app.dicom.study_metadata import collect_dicom_metadata
DICOM_DIR = Path(r"C:\Users\Sivab\Downloads\isotropic_volume (1).nii")

router = APIRouter(prefix="/api/studies", tags=["Studies"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DICOM_DIR = Path(r"C:\Users\Sivab\Downloads\isotropic_volume (1).nii")

LEFT_MESH = DATA_DIR / "refined_meshes" / "kidney_left_refined.stl"
if not LEFT_MESH.exists():
    LEFT_MESH = DATA_DIR / "meshes" / "kidney_left.stl"

RIGHT_MESH = DATA_DIR / "refined_meshes" / "kidney_right_refined.stl"
if not RIGHT_MESH.exists():
    RIGHT_MESH = DATA_DIR / "meshes" / "kidney_right.stl"

ISOTROPIC_VOLUME = DATA_DIR / "isotropic_volume.nii.gz"
VALIDATION_REPORT = DATA_DIR / "reports" / "validation_report.json"

LEFT_MASK = DATA_DIR / "segmentations" / "kidney_left.nii.gz"
RIGHT_MASK = DATA_DIR / "segmentations" / "kidney_right.nii.gz"

def load_validation_report():
    if not VALIDATION_REPORT.exists():
        return None

    try:
        with open(
            VALIDATION_REPORT,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return None

def get_mesh_measurements(mesh_path):
    if not mesh_path.exists():
        return None
    try:
        mesh = trimesh.load(mesh_path, force="mesh")
        bounds = mesh.bounds
        dimensions = bounds[1] - bounds[0]
        return {
            "width_mm": float(dimensions[0]),
            "depth_mm": float(dimensions[1]),
            "height_mm": float(dimensions[2]),
            "centroid_x_mm": float(mesh.centroid[0]),
            "centroid_y_mm": float(mesh.centroid[1]),
            "centroid_z_mm": float(mesh.centroid[2]),
        }
    except Exception:
        return None

def extract_metadata(report):
    if not report:
        return None

    volume = report.get("volume", {})

    original = None

    if DICOM_DIR.exists():
        try:
            original = collect_dicom_metadata(
                str(DICOM_DIR)
            )
        except Exception:
            original = None

    return {
        "original": original,

        "reconstructed": {
            "size": volume.get("size"),
            "spacing_mm": volume.get("spacing_mm"),
            "origin": volume.get("origin"),
            "direction": volume.get("direction"),
        },
    }

def extract_measurements(report):
    if not report:
        return None

    structures = report.get("structures", [])
    measurements = {}

    for structure in structures:
        name = structure.get("name", "").lower()

        if name == "left kidney":
            measurements["left_kidney"] = {
                "mask_volume_cm3": structure.get("mask_volume_cm3"),
                "volume_cm3": structure.get("mesh_volume_cm3"),
                "volume_error_cm3": structure.get("volume_error_cm3"),
                "volume_error_percent": structure.get("volume_error_percent"),
                "surface_area_cm2": structure.get("surface_area_cm2"),
                "vertices": structure.get("vertices"),
                "faces": structure.get("faces"),
                "watertight": structure.get("watertight"),
                "valid_volume": structure.get("valid_volume"),
                "winding_consistent": structure.get("winding_consistent"),
                "width_mm": structure.get("width_mm"),
                "depth_mm": structure.get("depth_mm"),
                "height_mm": structure.get("height_mm"),
                "centroid_x_mm": structure.get("centroid_x_mm"),
                "centroid_y_mm": structure.get("centroid_y_mm"),
                "centroid_z_mm": structure.get("centroid_z_mm"),
            }

        elif name == "right kidney":
            measurements["right_kidney"] = {
                "mask_volume_cm3": structure.get("mask_volume_cm3"),
                "volume_cm3": structure.get("mesh_volume_cm3"),
                "volume_error_cm3": structure.get("volume_error_cm3"),
                "volume_error_percent": structure.get("volume_error_percent"),
                "surface_area_cm2": structure.get("surface_area_cm2"),
                "vertices": structure.get("vertices"),
                "faces": structure.get("faces"),
                "watertight": structure.get("watertight"),
                "valid_volume": structure.get("valid_volume"),
                "winding_consistent": structure.get("winding_consistent"),
                "width_mm": structure.get("width_mm"),
                "depth_mm": structure.get("depth_mm"),
                "height_mm": structure.get("height_mm"),
                "centroid_x_mm": structure.get("centroid_x_mm"),
                "centroid_y_mm": structure.get("centroid_y_mm"),
                "centroid_z_mm": structure.get("centroid_z_mm"),
            }

    return measurements

@router.get("/current")
def get_current_study():
    report = load_validation_report()
    measurements = extract_measurements(report)
    metadata = extract_metadata(report)

    # Dynamically augment missing mesh measurements from STL files if needed
    left_dimensions = get_mesh_measurements(LEFT_MESH)
    right_dimensions = get_mesh_measurements(RIGHT_MESH)

    if measurements:
        if measurements.get("left_kidney") and left_dimensions:
            measurements["left_kidney"].update({k: v for k, v in left_dimensions.items() if measurements["left_kidney"].get(k) is None})
        if measurements.get("right_kidney") and right_dimensions:
            measurements["right_kidney"].update({k: v for k, v in right_dimensions.items() if measurements["right_kidney"].get(k) is None})

    return {
        "study_id": "demo-study",
        "modality": "CT",
        "status": "completed",
        "outputs": {
            "volume": ISOTROPIC_VOLUME.exists(),
            "left_kidney_mesh": LEFT_MESH.exists(),
            "right_kidney_mesh": RIGHT_MESH.exists(),
            "left_kidney_segmentation": LEFT_MASK.exists(),
            "right_kidney_segmentation": RIGHT_MASK.exists(),
            "validation_report": VALIDATION_REPORT.exists(),
        },
        "models": {
            "left_kidney": "/api/studies/models/left-kidney",
            "right_kidney": "/api/studies/models/right-kidney",
        },
        "measurements": measurements,
        "metadata": metadata,
    }

@router.get("/report")
def get_report():
    if not VALIDATION_REPORT.exists():
        raise HTTPException(status_code=404, detail="Validation report not found")
    with open(VALIDATION_REPORT, "r", encoding="utf-8") as file:
        data = json.load(file)
    return JSONResponse(content=data)

@router.get("/models/left-kidney")
def get_left_kidney():
    if not LEFT_MESH.exists():
        raise HTTPException(status_code=404, detail="Left kidney mesh not found")
    return FileResponse(LEFT_MESH, media_type="model/stl", filename="kidney_left_refined.stl")

@router.get("/models/right-kidney")
def get_right_kidney():
    if not RIGHT_MESH.exists():
        raise HTTPException(status_code=404, detail="Right kidney mesh not found")
    return FileResponse(RIGHT_MESH, media_type="model/stl", filename="kidney_right_refined.stl")

@router.get("/volume")
def get_volume():
    if not ISOTROPIC_VOLUME.exists():
        raise HTTPException(status_code=404, detail="Isotropic CT volume not found")
    return FileResponse(ISOTROPIC_VOLUME, media_type="application/gzip", filename="isotropic_volume.nii.gz")

@router.get("/segmentations/left-kidney")
def get_left_kidney_mask():
    if not LEFT_MASK.exists():
        raise HTTPException(status_code=404, detail="Left kidney segmentation not found")
    return FileResponse(LEFT_MASK, media_type="application/gzip", filename="kidney_left.nii.gz")

@router.get("/segmentations/right-kidney")
def get_right_kidney_mask():
    if not RIGHT_MASK.exists():
        raise HTTPException(status_code=404, detail="Right kidney segmentation not found")
    return FileResponse(RIGHT_MASK, media_type="application/gzip", filename="kidney_right.nii.gz")