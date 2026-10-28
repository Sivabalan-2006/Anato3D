import trimesh

def export_mesh(vertices, faces, output_path):
    """
    Export 3D vertices and triangular faces as an STL mesh file.
    """
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    print(f"Mesh vertices: {len(mesh.vertices)}")
    print(f"Mesh faces: {len(mesh.faces)}")
    print(f"Mesh watertight: {mesh.is_watertight}")
    print(f"Mesh volume: {mesh.volume:.2f} mm³")
    
    mesh.export(output_path)
    print(f"Mesh exported to:\n{output_path}")
    return mesh
