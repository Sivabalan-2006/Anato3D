import trimesh

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
