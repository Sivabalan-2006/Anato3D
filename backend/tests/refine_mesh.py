import sys
from pathlib import Path

# Add backend directory to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import trimesh
from app.mesh.refinement import refine_mesh

INPUT_DIR = Path("../data/meshes")
OUTPUT_DIR = Path("../data/refined_meshes")

def process_mesh(input_filename, output_filename, name):
    input_path = INPUT_DIR / input_filename
    output_path = OUTPUT_DIR / output_filename

    print("\n" + "=" * 60)
    print(f"{name.upper()} KIDNEY REFINEMENT")
    print("=" * 60)

    if not input_path.exists():
        print(f"Error: Mesh file not found at {input_path}")
        return

    mesh = trimesh.load_mesh(str(input_path))
    original_volume = mesh.volume
    original_vertices = len(mesh.vertices)
    original_faces = len(mesh.faces)

    print("\nORIGINAL")
    print("-" * 60)
    print(f"Vertices: {original_vertices:,}")
    print(f"Faces:    {original_faces:,}")
    print(f"Volume:   {original_volume / 1000.0:.2f} cm³")

    refined = refine_mesh(mesh)
    refined_volume = refined.volume

    print("\nREFINED")
    print("-" * 60)
    print(f"Vertices:   {len(refined.vertices):,}")
    print(f"Faces:      {len(refined.faces):,}")
    print(f"Volume:     {refined_volume / 1000.0:.2f} cm³")
    print(f"Watertight: {refined.is_watertight}")

    volume_change = (abs(refined_volume - original_volume) / original_volume) * 100
    print(f"Volume change: {volume_change:.4f}%")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refined.export(str(output_path))
    print(f"\nSaved refined mesh to:\n{output_path.resolve()}")

def main():
    process_mesh("kidney_left.stl", "kidney_left_refined.stl", "Left")
    process_mesh("kidney_right.stl", "kidney_right_refined.stl", "Right")

if __name__ == "__main__":
    main()
