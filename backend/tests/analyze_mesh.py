import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import trimesh
from app.analysis.measurements import analyze_mesh
from app.analysis.validation import validate_mesh

MESH_DIR = Path("../data/meshes")

def analyze(filename, name):
    path = MESH_DIR / filename
    print("\n" + "=" * 60)
    print(f"{name.upper()} KIDNEY")
    print("=" * 60)

    if not path.exists():
        print(f"Error: Mesh file not found at {path}")
        return

    mesh = trimesh.load_mesh(str(path))
    measurements = analyze_mesh(mesh)
    validation = validate_mesh(mesh)

    print("\nGEOMETRY")
    print("-" * 60)
    print(f"Vertices:     {measurements['vertices']:,}")
    print(f"Faces:        {measurements['faces']:,}")
    print(f"Volume:       {measurements['volume_cm3']:.2f} cm³")
    print(f"Surface area: {measurements['surface_area_cm2']:.2f} cm²")
    print(f"Width:        {measurements['width_mm']:.2f} mm")
    print(f"Depth:        {measurements['depth_mm']:.2f} mm")
    print(f"Height:       {measurements['height_mm']:.2f} mm")

    print("\nCENTROID")
    print("-" * 60)
    print(f"X: {measurements['centroid_x_mm']:.2f} mm")
    print(f"Y: {measurements['centroid_y_mm']:.2f} mm")
    print(f"Z: {measurements['centroid_z_mm']:.2f} mm")

    print("\nVALIDATION")
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
