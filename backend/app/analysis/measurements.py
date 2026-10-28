import trimesh

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
