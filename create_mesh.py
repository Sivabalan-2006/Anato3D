from pathlib import Path

FILES = {
    "backend/app/analysis/measurements.py": '''import trimesh

def analyze_mesh(mesh):
    """
    Calculate geometric measurements and quality information for a 3D anatomical mesh.
    """
    bounds = mesh.bounds
    minimum = bounds[0]
    maximum = bounds[1]
    dimensions = maximum - minimum

    measurements = {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "volume_mm3": float(mesh.volume),
        "volume_cm3": float(mesh.volume / 1000.0),
        "surface_area_mm2": float(mesh.area),
        "surface_area_cm2": float(mesh.area / 100.0),
        "width_mm": float(dimensions[0]),
        "depth_mm": float(dimensions[1]),
        "height_mm": float(dimensions[2]),
        "centroid_x_mm": float(mesh.centroid[0]),
        "centroid_y_mm": float(mesh.centroid[1]),
        "centroid_z_mm": float(mesh.centroid[2]),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume)
    }
    return measurements
''',

    "backend/app/analysis/validation.py": '''import numpy as np

def validate_mesh(mesh):
    """
    Perform basic geometric validation of a mesh.
    """
    return {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "valid_volume": bool(mesh.is_volume),
        "vertex_count": int(len(mesh.vertices)),
        "face_count": int(len(mesh.faces)),
        "has_nan_vertices": bool(np.isnan(mesh.vertices).any())
    }
''',

    "backend/app/analysis/volume_validation.py": '''def calculate_volume_error(mask_volume_cm3, mesh_volume_cm3):
    """
    Calculate absolute and percentage difference between mask and mesh volume.
    """
    absolute_error = abs(mask_volume_cm3 - mesh_volume_cm3)
    percentage_error = (absolute_error / mask_volume_cm3) * 100
    return {
        "absolute_error_cm3": absolute_error,
        "percentage_error": percentage_error
    }
''',

    "backend/tests/analyze_mesh.py": '''import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import trimesh
from app.analysis.measurements import analyze_mesh
from app.analysis.validation import validate_mesh

MESH_DIR = Path("../data/meshes")

def analyze(filename, name):
    path = MESH_DIR / filename
    print("\\n" + "=" * 60)
    print(f"{name.upper()} KIDNEY")
    print("=" * 60)

    if not path.exists():
        print(f"Error: Mesh file not found at {path}")
        return

    mesh = trimesh.load_mesh(str(path))
    measurements = analyze_mesh(mesh)
    validation = validate_mesh(mesh)

    print("\\nGEOMETRY")
    print("-" * 60)
    print(f"Vertices:     {measurements['vertices']:,}")
    print(f"Faces:        {measurements['faces']:,}")
    print(f"Volume:       {measurements['volume_cm3']:.2f} cm³")
    print(f"Surface area: {measurements['surface_area_cm2']:.2f} cm²")
    print(f"Width:        {measurements['width_mm']:.2f} mm")
    print(f"Depth:        {measurements['depth_mm']:.2f} mm")
    print(f"Height:       {measurements['height_mm']:.2f} mm")

    print("\\nCENTROID")
    print("-" * 60)
    print(f"X: {measurements['centroid_x_mm']:.2f} mm")
    print(f"Y: {measurements['centroid_y_mm']:.2f} mm")
    print(f"Z: {measurements['centroid_z_mm']:.2f} mm")

    print("\\nVALIDATION")
    print("-" * 60)
    print(f"Watertight:         {validation['watertight']}")
    print(f"Winding consistent: {validation['winding_consistent']}")
    print(f"Valid volume:       {validation['valid_volume']}")
    print(f"NaN vertices:       {validation['has_nan_vertices']}")

def main():
    analyze("kidney_left.stl", "Left")
    analyze("kidney_right.stl", "Right")

if __name__ == "__main__":
    main()
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nAnalysis files successfully created!")