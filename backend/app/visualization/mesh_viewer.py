import trimesh
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
    print(f"\nViewer saved to:\n{output_path}")
