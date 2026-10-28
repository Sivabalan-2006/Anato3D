import numpy as np

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
