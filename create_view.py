from pathlib import Path

FILES = {
    "backend/app/visualization/__init__.py": "",

    "backend/app/visualization/mesh_viewer.py": '''import trimesh
import plotly.graph_objects as go

def mesh_to_plotly(mesh, name, opacity=1.0):
    """
    Convert a Trimesh object into a Plotly Mesh3d trace.
    """
    vertices = mesh.vertices
    faces = mesh.faces
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        name=name,
        opacity=opacity,
        flatshading=False,
        hovertemplate=(
            f"{name}<br>"
            "X: %{x:.1f} mm<br>"
            "Y: %{y:.1f} mm<br>"
            "Z: %{z:.1f} mm"
            "<extra></extra>"
        )
    )

def create_kidney_viewer(left_mesh_path, right_mesh_path, output_path):
    """
    Create an interactive HTML viewer containing both kidney meshes.
    """
    print("Loading left kidney...")
    left_mesh = trimesh.load_mesh(left_mesh_path)
    print("Loading right kidney...")
    right_mesh = trimesh.load_mesh(right_mesh_path)

    left_trace = mesh_to_plotly(left_mesh, "Left Kidney")
    right_trace = mesh_to_plotly(right_mesh, "Right Kidney")

    fig = go.Figure(data=[left_trace, right_trace])

    fig.update_layout(
        title={"text": "Anato3D — Patient-Specific Kidney Model", "x": 0.5},
        scene=dict(
            xaxis_title="X (mm)",
            yaxis_title="Y (mm)",
            zaxis_title="Z (mm)",
            aspectmode="data",
            camera=dict(
                projection=dict(type="orthographic")
            )
        ),
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=0, r=0, t=60, b=0)
    )

    fig.write_html(output_path, include_plotlyjs=True)
    print(f"\\nViewer saved to:\\n{output_path}")
''',

    "backend/tests/create_viewer.py": '''import sys
from pathlib import Path

# Ensure backend package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.visualization.mesh_viewer import create_kidney_viewer

# Resolve path relative to backend root
BASE_DATA = Path(__file__).resolve().parent.parent.parent / "data"

LEFT_MESH = BASE_DATA / "refined_meshes" / "kidney_left_refined.stl"
RIGHT_MESH = BASE_DATA / "refined_meshes" / "kidney_right_refined.stl"
OUTPUT_DIR = BASE_DATA / "viewer"
OUTPUT_FILE = OUTPUT_DIR / "kidney_model.html"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    create_kidney_viewer(
        str(LEFT_MESH),
        str(RIGHT_MESH),
        str(OUTPUT_FILE)
    )

if __name__ == "__main__":
    main()
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nChatGPT visualization files successfully created!")