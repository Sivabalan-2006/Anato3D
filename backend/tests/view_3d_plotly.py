import sys
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
    print(f"Interactive 3D HTML Viewer created at:\n{OUTPUT_HTML.resolve()}")

if __name__ == "__main__":
    main()
