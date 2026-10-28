from pathlib import Path

FILES = {
    "backend/app/analysis/volume_validation.py": '''def calculate_volume_error(mask_volume_cm3, mesh_volume_cm3):
    """
    Calculate absolute and percentage difference between mask and mesh volume.
    """
    absolute_error = abs(mask_volume_cm3 - mesh_volume_cm3)
    if mask_volume_cm3 == 0:
        percentage_error = 0.0
    else:
        percentage_error = (absolute_error / mask_volume_cm3) * 100.0

    return {
        "mask_volume_cm3": mask_volume_cm3,
        "mesh_volume_cm3": mesh_volume_cm3,
        "absolute_error_cm3": absolute_error,
        "percentage_error": percentage_error
    }
''',

    "backend/app/analysis/report.py": '''import json
from pathlib import Path
import SimpleITK as sitk
import trimesh
from app.analysis.volume_validation import calculate_volume_error

def get_mask_volume(mask_path):
    image = sitk.ReadImage(str(mask_path))
    mask = sitk.GetArrayFromImage(image)
    voxel_count = (mask > 0).sum()
    spacing = image.GetSpacing()
    voxel_volume_mm3 = spacing[0] * spacing[1] * spacing[2]
    volume_cm3 = (voxel_count * voxel_volume_mm3) / 1000.0
    return float(volume_cm3)

def analyze_structure(name, mask_path, mesh_path):
    mask_volume = get_mask_volume(mask_path)
    mesh = trimesh.load_mesh(str(mesh_path))
    mesh_volume = mesh.volume / 1000.0
    volume_validation = calculate_volume_error(mask_volume, mesh_volume)

    return {
        "name": name,
        "mask_volume_cm3": round(mask_volume, 3),
        "mesh_volume_cm3": round(mesh_volume, 3),
        "volume_error_cm3": round(volume_validation["absolute_error_cm3"], 3),
        "volume_error_percent": round(volume_validation["percentage_error"], 4),
        "surface_area_cm2": round(mesh.area / 100.0, 3),
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "watertight": bool(mesh.is_watertight),
        "valid_volume": bool(mesh.is_volume),
        "winding_consistent": bool(mesh.is_winding_consistent)
    }

def generate_report():
    base = Path(__file__).resolve().parent.parent.parent / "data"

    ct_path = base / "isotropic_volume.nii.gz"
    left_mask = base / "segmentations" / "kidney_left.nii.gz"
    right_mask = base / "segmentations" / "kidney_right.nii.gz"
    left_mesh = base / "refined_meshes" / "kidney_left_refined.stl"
    right_mesh = base / "refined_meshes" / "kidney_right_refined.stl"

    ct = sitk.ReadImage(str(ct_path))

    report = {
        "project": "Anato3D",
        "modality": "CT",
        "volume": {
            "size": ct.GetSize(),
            "spacing_mm": ct.GetSpacing(),
            "origin": ct.GetOrigin(),
            "direction": ct.GetDirection()
        },
        "structures": [
            analyze_structure("Left Kidney", left_mask, left_mesh),
            analyze_structure("Right Kidney", right_mask, right_mesh)
        ]
    }

    output_dir = base / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "validation_report.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"Report saved to:\\n{output_path.resolve()}")
    return report

if __name__ == "__main__":
    generate_report()
''',

    "backend/tests/generate_report.py": '''import sys
from pathlib import Path

# Add backend directory to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.analysis.report import generate_report

if __name__ == "__main__":
    generate_report()
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nValidation report module files successfully created!")