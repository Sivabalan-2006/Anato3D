import json
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
    # Resolves to root Anato3D/data
    base = Path(__file__).resolve().parent.parent.parent.parent / "data"

    ct_path = base / "isotropic_volume.nii.gz"
    left_mask = base / "segmentations" / "kidney_left.nii.gz"
    right_mask = base / "segmentations" / "kidney_right.nii.gz"

    # Support refined meshes if present, fallback to raw meshes
    left_mesh = base / "refined_meshes" / "kidney_left_refined.stl"
    if not left_mesh.exists():
        left_mesh = base / "meshes" / "kidney_left.stl"

    right_mesh = base / "refined_meshes" / "kidney_right_refined.stl"
    if not right_mesh.exists():
        right_mesh = base / "meshes" / "kidney_right.stl"

    print(f"Loading CT volume from: {ct_path}")
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

    print(f"\nReport successfully generated and saved to:\n{output_path.resolve()}")
    return report

if __name__ == "__main__":
    generate_report()
