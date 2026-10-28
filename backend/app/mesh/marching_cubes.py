import numpy as np
import SimpleITK as sitk
from skimage.measure import marching_cubes

def mask_to_mesh(mask_path, output_path):
    """
    Convert a binary NIfTI segmentation mask into a 3D triangular mesh.
    """
    print(f"Loading mask: {mask_path}")
    image = sitk.ReadImage(mask_path)
    mask = sitk.GetArrayFromImage(image)

    # Ensure binary mask
    mask = (mask > 0).astype(np.uint8)

    print(f"Mask shape: {mask.shape}")
    print(f"Spacing: {image.GetSpacing()}")

    # SimpleITK array order is Z, Y, X; spacing must match Z, Y, X order
    spacing_xyz = image.GetSpacing()
    spacing_zyx = (spacing_xyz[2], spacing_xyz[1], spacing_xyz[0])

    # Extract 3D surface using Marching Cubes
    vertices, faces, normals, values = marching_cubes(mask, level=0.5, spacing=spacing_zyx)

    # Reorder vertices from (Z, Y, X) to (X, Y, Z)
    vertices_xyz = vertices[:, [2, 1, 0]]

    # Map to physical DICOM coordinate origin
    origin = np.asarray(image.GetOrigin(), dtype=float)
    vertices_xyz = vertices_xyz + origin

    print(f"Vertices: {len(vertices_xyz)}")
    print(f"Faces: {len(faces)}")

    return vertices_xyz, faces
