from pathlib import Path

FILES = {
    "backend/app/mesh/marching_cubes.py": '''import numpy as np
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
''',

    "backend/app/mesh/export.py": '''import trimesh

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
    print(f"Mesh exported to:\\n{output_path}")
    return mesh
''',

    "backend/tests/test_mesh.py": '''import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.mesh.marching_cubes import mask_to_mesh
from app.mesh.export import export_mesh

SEGMENTATION_DIR = Path("../data/segmentations")
OUTPUT_DIR = Path("../data/meshes")

def process_kidney(input_filename, output_filename):
    input_path = SEGMENTATION_DIR / input_filename
    
    # Support both .nii.gz and .nii extensions
    if not input_path.exists():
        alt_name = input_filename.replace(".nii.gz", ".nii") if input_filename.endswith(".nii.gz") else input_filename + ".gz"
        input_path = SEGMENTATION_DIR / alt_name

    output_path = OUTPUT_DIR / output_filename
    vertices, faces = mask_to_mesh(str(input_path), str(output_path))
    export_mesh(vertices, faces, str(output_path))

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\\nGenerating LEFT kidney mesh...")
    process_kidney("kidney_left.nii.gz", "kidney_left.stl")

    print("\\nGenerating RIGHT kidney mesh...")
    process_kidney("kidney_right.nii.gz", "kidney_right.stl")

if __name__ == "__main__":
    main()
'''
}

for rel_path, content in FILES.items():
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Created: {p.resolve()}")

print("\nPhase 5 3D mesh files successfully created!")