from pathlib import Path

FILES = {
    "backend/app/mesh/refinement.py": '''import trimesh

def refine_mesh(mesh):
    """
    Perform conservative mesh cleanup.
    Improves topological integrity without altering anatomical geometry.
    """
    mesh.remove_infinite_values()
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()

    try:
        mesh.update_faces(mesh.unique_faces())
    except AttributeError:
        pass

    try:
        mesh.update_faces(mesh.nondegenerate_faces())
    except AttributeError:
        pass

    if not mesh.is_watertight:
        trimesh.repair.fill_holes(mesh)
        mesh.remove_unreferenced_vertices()

    return mesh
''',

    "backend/tests/refine_mesh.py": '''import sys
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

    print("\\n" + "=" * 60)
    print(f"{name.upper()} KIDNEY REFINEMENT")
    print("=" * 60)

    if not input_path.exists():
        print(f"Error: Mesh file not found at {input_path}")
        return

    mesh = trimesh.load_mesh(str(input_path))
    original_volume = mesh.volume
    original_vertices = len(mesh.vertices)
    original_faces = len(mesh.faces)

    print("\\nORIGINAL")
    print("-" * 60)
    print(f"Vertices: {original_vertices:,}")
    print(f"Faces:    {original_faces:,}")
    print(f"Volume:   {original_volume / 1000.0:.2f} cm³")

    refined = refine_mesh(mesh)
    refined_volume = refined.volume

    print("\\nREFINED")
    print("-" * 60)
    print(f"Vertices:   {len(refined.vertices):,}")
    print(f"Faces:      {len(refined.faces):,}")
    print(f"Volume:     {refined_volume / 1000.0:.2f} cm³")
    print(f"Watertight: {refined.is_watertight}")

    volume_change = (abs(refined_volume - original_volume) / original_volume) * 100
    print(f"Volume change: {volume_change:.4f}%")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    refined.export(str(output_path))
    print(f"\\nSaved refined mesh to:\\n{output_path.resolve()}")

def main():
    process_mesh("kidney_left.stl", "kidney_left_refined.stl", "Left")
    process_mesh("kidney_right.stl", "kidney_right_refined.stl", "Right")

if __name__ == "__main__":
    main()
''',

    "backend/tests/view_3d_plotly.py": '''import sys
from pathlib import Path

# Add backend directory to Python search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import trimesh
import plotly.graph_objects as go

MESH_DIR = Path("../data/refined_meshes")
OUTPUT_HTML = Path("../data/viewer/kidney_model.html")

def add_mesh_trace(mesh, color, name):
    vertices = mesh.vertices
    faces = mesh.faces
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        color=color,
        opacity=0.85,
        name=name,
        showscale=False
    )

def main():
    left_path = MESH_DIR / "kidney_left_refined.stl"
    right_path = MESH_DIR / "kidney_right_refined.stl"

    if not left_path.exists() or not right_path.exists():
        print("Refined meshes not found. Falling back to raw meshes...")
        MESH_DIR_RAW = Path("../data/meshes")
        left_path = MESH_DIR_RAW / "kidney_left.stl"
        right_path = MESH_DIR_RAW / "kidney_right.stl"

    left_mesh = trimesh.load_mesh(str(left_path))
    right_mesh = trimesh.load_mesh(str(right_path))

    fig = go.Figure(data=[
        add_mesh_trace(left_mesh, 'forestgreen', f'Left Kidney ({left_mesh.volume / 1000.0:.2f} cm³)'),
        add_mesh_trace(right_mesh, 'darkorange', f'Right Kidney ({right_mesh.volume / 1000.0:.2f} cm³)')
    ])

    fig.update_layout(
        title="Anato3D — Patient-Specific Interactive 3D Model",
        scene=dict(
            xaxis=dict(title="X (mm)", backgroundcolor="rgb(20, 20, 20)", gridcolor="gray"),
            yaxis=dict(title="Y (mm)", backgroundcolor="rgb(20, 20, 20)", gridcolor="gray"),
            zaxis=dict(title="Z (mm)", backgroundcolor="rgb(20, 20, 20)", gridcolor="gray"),
            aspectmode="data"
        ),
        paper_bgcolor="black",
        font=dict(color="white"),
        margin=dict(r=10, l=10, b=10, t=50)
    )

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUTPUT_HTML))
    print(f"Interactive 3D HTML Viewer created at:\\n{OUTPUT_HTML.resolve()}")

if __name__ == "__main__":
    main()
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nRefinement and Interactive Viewer setup complete!")